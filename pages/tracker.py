"""Tracker page — run price scans manually or from competitor library."""
import streamlit as st
import time
import pandas as pd

try:
    from utils.scraper import scrape_product, detect_brand
    from utils.database import save_price, add_to_watchlist
    from data.competitors import COMPETITOR_LIBRARY, get_all_competitor_urls, get_brands, get_categories
    MODULES_OK = True
except Exception as e:
    MODULES_OK = False
    _import_err = str(e)


def render():
    st.markdown("""
    <div class="page-header">
        <div>
            <div class="page-title">TRACK <span>PRICES</span></div>
            <div class="page-sub">Manual URLs · Competitor Library · Batch Scan</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not MODULES_OK:
        st.error(f"Module import error: {_import_err}")
        return

    tab1, tab2, tab3 = st.tabs(["📋  Custom URLs", "🏷️  Competitor Library", "⚡  Batch Scan All"])

    # ─────────────────────────────────────────────
    # TAB 1: Custom URLs
    # ─────────────────────────────────────────────
    with tab1:
        st.markdown("**Paste product URLs** (one per line) — works on any Shopify store, Under Armour, Nike, and more.")
        st.markdown("")

        col_input, col_opts = st.columns([3, 1])
        with col_input:
            urls_text = st.text_area(
                "urls_custom", label_visibility="collapsed",
                height=160,
                placeholder="https://www.gymshark.com/products/...\nhttps://us.shop.underarmour.com/p/...",
            )
        with col_opts:
            brand_override = st.text_input("Brand label (optional)", placeholder="e.g. Gymshark")
            category_override = st.text_input("Category (optional)", placeholder="e.g. Leggings")
            save_watch = st.checkbox("Save to Watchlist", value=True)

        if st.button("🔍  TRACK NOW", key="track_custom"):
            urls = [u.strip() for u in urls_text.split('\n') if u.strip()]
            if not urls:
                st.warning("Enter at least one URL.")
            else:
                _run_scan(urls, brand_override, category_override, save_watch=save_watch)

    # ─────────────────────────────────────────────
    # TAB 2: Competitor Library
    # ─────────────────────────────────────────────
    with tab2:
        st.markdown("**Pre-built competitor database** — zero setup, just pick brands and track.")
        st.markdown("")

        filter_col1, filter_col2 = st.columns(2)
        with filter_col1:
            selected_brands = st.multiselect(
                "Select Brands",
                options=get_brands(),
                default=["Gymshark"],
            )
        with filter_col2:
            all_cats = get_categories()
            selected_cats = st.multiselect(
                "Filter by Category (optional)",
                options=all_cats,
            )

        # Preview selected URLs
        all_rows = get_all_competitor_urls()
        filtered = [
            r for r in all_rows
            if (not selected_brands or r['brand'] in selected_brands)
            and (not selected_cats or r['category'] in selected_cats)
        ]

        if filtered:
            st.markdown(f'<div style="font-size:0.78rem;color:#555;margin-bottom:8px;">{len(filtered)} products selected</div>', unsafe_allow_html=True)
            with st.expander("Preview selected URLs"):
                for r in filtered:
                    st.markdown(f'`{r["brand"]}` · {r["category"]} · `{r["url"]}`')

        if st.button("🔍  TRACK SELECTED", key="track_library", disabled=not filtered):
            urls = [r['url'] for r in filtered]
            brand_map = {r['url']: r['brand'] for r in filtered}
            cat_map   = {r['url']: r['category'] for r in filtered}
            _run_scan_mapped(urls, brand_map, cat_map, save_watch=True)

    # ─────────────────────────────────────────────
    # TAB 3: Batch scan all
    # ─────────────────────────────────────────────
    with tab3:
        st.markdown("**Full library scan** — tracks every pre-loaded competitor product. Use for scheduled daily runs.")
        st.markdown("")

        all_rows = get_all_competitor_urls()
        st.info(f"⚡ This will scan **{len(all_rows)} products** across {len(get_brands())} brands. Takes 2–5 minutes depending on site response times.")

        col_warn, col_btn = st.columns([3, 1])
        with col_btn:
            run_all = st.button("🚀  RUN FULL SCAN", key="track_all")

        if run_all:
            urls = [r['url'] for r in all_rows]
            brand_map = {r['url']: r['brand'] for r in all_rows}
            cat_map   = {r['url']: r['category'] for r in all_rows}
            _run_scan_mapped(urls, brand_map, cat_map, save_watch=True)

    # ─── Show last results ────────────────────────────────
    if st.session_state.get('last_scan_results'):
        _render_results(st.session_state.last_scan_results)


# ─────────────────────────────────────────────────────────────────
def _run_scan(urls, brand_override='', cat_override='', save_watch=True):
    results = []
    prog = st.progress(0, text="Starting scan...")
    status = st.empty()
    key = st.session_state.get('scraperapi_key', '')

    for i, url in enumerate(urls):
        brand = brand_override or detect_brand(url)
        status.markdown(f"🔍 Scanning **{brand}** · {url[:55]}...")
        prog.progress((i) / len(urls))

        r = scrape_product(url, brand=brand, category=cat_override, scraperapi_key=key)
        results.append(r)

        try:
            save_price(url, r['brand'], r['category'], r['product'],
                       r['price_raw'], r['price_num'], r['method'], r['status'])
            if save_watch:
                add_to_watchlist(url, r['brand'], r['category'], r['product'])
        except Exception:
            pass

        time.sleep(0.3)

    prog.progress(1.0, "✅ Done!")
    time.sleep(0.4)
    prog.empty(); status.empty()

    st.session_state.last_scan_results = results
    success = sum(1 for r in results if r['status'] == '✅')
    st.success(f"✅ Scanned {len(results)} products · {success} prices found")
    st.rerun()


def _run_scan_mapped(urls, brand_map, cat_map, save_watch=True):
    results = []
    prog = st.progress(0, text="Starting scan...")
    status = st.empty()
    key = st.session_state.get('scraperapi_key', '')

    for i, url in enumerate(urls):
        brand = brand_map.get(url, detect_brand(url))
        cat   = cat_map.get(url, '')
        status.markdown(f"🔍 **{brand}** · {cat} · {url[:45]}...")
        prog.progress(i / len(urls))

        r = scrape_product(url, brand=brand, category=cat, scraperapi_key=key)
        results.append(r)

        try:
            save_price(url, r['brand'], r['category'], r['product'],
                       r['price_raw'], r['price_num'], r['method'], r['status'])
            if save_watch:
                add_to_watchlist(url, r['brand'], r['category'])
        except Exception:
            pass

        time.sleep(0.35)

    prog.progress(1.0, "✅ Done!")
    time.sleep(0.4)
    prog.empty(); status.empty()

    st.session_state.last_scan_results = results
    success = sum(1 for r in results if r['status'] == '✅')
    st.success(f"✅ Scanned {len(results)} products · {success} prices found")
    st.rerun()


def _render_results(results):
    st.markdown('<div class="section-header">📊 SCAN RESULTS</div>', unsafe_allow_html=True)

    # Summary metrics
    success = [r for r in results if r['status'] == '✅']
    prices = [r['price_num'] for r in success if r['price_num']]
    methods = {}
    for r in success:
        methods[r['method']] = methods.get(r['method'], 0) + 1

    mcol1, mcol2, mcol3, mcol4 = st.columns(4)
    with mcol1:
        st.metric("Scanned", len(results))
    with mcol2:
        st.metric("Found", len(success))
    with mcol3:
        st.metric("Min Price", f"${min(prices):.2f}" if prices else "—")
    with mcol4:
        st.metric("Max Price", f"${max(prices):.2f}" if prices else "—")

    method_html = " ".join([
        f'<span class="badge badge-json">{m}: {n}</span>' if 'JSON' in m
        else f'<span class="badge badge-api">{m}: {n}</span>' if 'API' in m
        else f'<span class="badge badge-html">{m}: {n}</span>'
        for m, n in methods.items()
    ])
    st.markdown(f'<div style="margin-bottom:12px;">{method_html}</div>', unsafe_allow_html=True)

    for r in results:
        is_sale = r.get('price_num') and False  # promo check would go here
        price_class = "error" if r['status'] == '❌' else ""
        mc = r.get('method_class', '')
        method_badge = (
            f'<span class="badge badge-json">{r["method"]}</span>' if 'JSON' in r.get('method','')
            else f'<span class="badge badge-api">{r["method"]}</span>' if 'API' in r.get('method','')
            else f'<span class="badge badge-html">{r["method"]}</span>'
        )
        st.markdown(f"""
        <div class="data-row">
          <div style="flex:1; min-width:0;">
            <span class="badge badge-brand">{r['brand']}</span>
            {'<span class="badge badge-dtc" style="margin-left:6px;">'+r['category']+'</span>' if r.get('category') else ''}
            {method_badge}
            <div class="product-name">{(r.get('product') or 'Unknown')[:65]}</div>
            <div class="url-chip">{r['url']}</div>
          </div>
          <div style="text-align:right; min-width:100px;">
            <div class="price-display {price_class}">{r['price_raw']}</div>
            <div style="font-size:0.65rem;color:#444;">{r['status']}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # CSV export
    df = pd.DataFrame([{
        'Brand': r['brand'], 'Category': r.get('category',''),
        'Product': r.get('product',''), 'Price': r['price_raw'],
        'Method': r['method'], 'URL': r['url'], 'Status': r['status'],
    } for r in results])
    st.download_button("📥 Download CSV", df.to_csv(index=False).encode(),
                       f"allrj_scan.csv", "text/csv")
