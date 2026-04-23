"""
Brand Comparison page — side-by-side price comparison across brands and categories.
"""
import streamlit as st
import pandas as pd

try:
    from utils.database import get_latest_price_per_url, get_price_history
    from data.competitors import COMPETITOR_LIBRARY, get_categories, TIER_ORDER
    DB_OK = True
except Exception as e:
    DB_OK = False
    _err = str(e)


def render():
    st.markdown("""
    <div class="page-header">
        <div>
            <div class="page-title">BRAND <span>COMPARISON</span></div>
            <div class="page-sub">Side-by-side pricing across brands and categories</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not DB_OK:
        st.error(f"Error: {_err}")
        return

    latest = get_latest_price_per_url()

    if not latest:
        st.markdown("""
        <div class="empty-state">
          <div class="empty-icon">📊</div>
          <div class="empty-title">NO DATA YET</div>
          <div class="empty-sub">Run a scan from the Track Prices page to populate comparison data</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("→ Track Prices"):
            st.session_state.page = 'tracker'
            st.rerun()
        return

    df = pd.DataFrame(latest)
    df = df[df['price_num'].notna()]

    tab1, tab2, tab3 = st.tabs([
        "🏷️  By Category",
        "🏢  By Brand",
        "📋  Full Matrix",
    ])

    # ── TAB 1: By Category ────────────────────────────────────────────────
    with tab1:
        st.markdown("**Pick a category and see how every brand prices it — ranked cheapest to most expensive.**")
        st.markdown("")

        cats = sorted(df['category'].dropna().unique().tolist())
        if not cats:
            st.info("No category data yet. Run a scan first.")
            return

        sel_cat = st.selectbox("Select Category", cats)
        cat_df = df[df['category'] == sel_cat].copy()
        cat_df = cat_df.sort_values('price_num')

        if cat_df.empty:
            st.info(f"No data for {sel_cat} yet.")
        else:
            # Summary metrics
            avg  = cat_df['price_num'].mean()
            low  = cat_df['price_num'].min()
            high = cat_df['price_num'].max()
            spread = high - low

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Cheapest", f"${low:.2f}")
            m2.metric("Most Expensive", f"${high:.2f}")
            m3.metric("Market Average", f"${avg:.2f}")
            m4.metric("Price Spread", f"${spread:.2f}")

            st.markdown("")

            # Ranked list with visual bar
            max_price = cat_df['price_num'].max()
            for _, row in cat_df.iterrows():
                pct_of_max = (row['price_num'] / max_price) * 100
                tier = COMPETITOR_LIBRARY.get(row['brand'], {}).get('tier', '')
                tier_badge = (
                    'badge-up' if tier == 'Major'
                    else 'badge-brand' if tier == 'Premium DTC'
                    else 'badge-down'
                )
                is_cheapest = row['price_num'] == low
                is_priciest = row['price_num'] == high

                crown = ' 👑' if is_priciest else (' 💚' if is_cheapest else '')

                st.markdown(f"""
                <div class="data-row" style="margin-bottom:6px;">
                  <div style="flex:1;min-width:0;">
                    <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
                      <span class="badge badge-brand">{row['brand']}</span>
                      <span class="badge {tier_badge}">{tier}</span>
                      {f'<span style="font-size:0.7rem;color:var(--text2);">{crown}</span>' if crown else ''}
                    </div>
                    <div style="background:var(--border);border-radius:4px;height:6px;overflow:hidden;">
                      <div style="width:{pct_of_max:.0f}%;height:100%;background:var(--accent);border-radius:4px;transition:width 0.3s;"></div>
                    </div>
                    <div class="url-chip" style="margin-top:4px;">{row.get('product','')[:55] or row['url'][:55]}</div>
                  </div>
                  <div style="text-align:right;min-width:90px;margin-left:16px;">
                    <div class="price-display">${row['price_num']:.2f}</div>
                    <div style="font-size:0.65rem;color:var(--muted);margin-top:2px;">
                      {'+' if row['price_num'] > avg else ''}{row['price_num']-avg:.2f} vs avg
                    </div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

            # Quick insight
            cheapest_brand = cat_df.iloc[0]['brand']
            priciest_brand = cat_df.iloc[-1]['brand']
            st.markdown(f"""
            <div style="background:var(--accent-dim);border:1px solid rgba(99,102,241,0.2);border-radius:var(--radius);padding:14px 18px;margin-top:12px;">
              <div style="font-size:0.72rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.8px;margin-bottom:4px;">💡 Quick Insight</div>
              <div style="font-size:0.82rem;color:var(--text2);line-height:1.6;">
                In <strong style="color:var(--text)">{sel_cat}</strong>, the market spans ${low:.2f} ({cheapest_brand}) to ${high:.2f} ({priciest_brand}) — a ${spread:.2f} spread.
                Pricing at <strong style="color:var(--accent-lt)">${avg*0.9:.2f}–${avg:.2f}</strong> puts you in the competitive mid-market while staying above budget perception.
              </div>
            </div>
            """, unsafe_allow_html=True)

    # ── TAB 2: By Brand ───────────────────────────────────────────────────
    with tab2:
        st.markdown("**Pick a brand and see their full pricing range across all categories.**")
        st.markdown("")

        brands = sorted(df['brand'].dropna().unique().tolist())
        sel_brand = st.selectbox("Select Brand", brands)
        brand_df = df[df['brand'] == sel_brand].copy()

        if brand_df.empty:
            st.info(f"No data for {sel_brand}.")
        else:
            tier = COMPETITOR_LIBRARY.get(sel_brand, {}).get('tier', '')
            domain = COMPETITOR_LIBRARY.get(sel_brand, {}).get('domain', '')

            st.markdown(f"""
            <div style="background:var(--surface);border:1px solid var(--border);border-radius:var(--radius-lg);padding:16px 20px;margin-bottom:16px;display:flex;align-items:center;gap:16px;">
              <div>
                <div style="font-family:var(--font-head);font-size:1.3rem;font-weight:700;color:var(--text);">{sel_brand}</div>
                <div style="font-family:var(--font-mono);font-size:0.68rem;color:var(--muted);">{domain}</div>
              </div>
              <span class="badge badge-brand">{tier}</span>
              <div style="margin-left:auto;text-align:right;">
                <div style="font-size:0.65rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.8px;">Avg Price</div>
                <div style="font-family:var(--font-head);font-size:1.6rem;font-weight:700;color:var(--text);">${brand_df['price_num'].mean():.2f}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            for _, row in brand_df.sort_values('price_num', ascending=False).iterrows():
                st.markdown(f"""
                <div class="data-row">
                  <div style="flex:1;">
                    <span class="badge badge-dtc">{row.get('category','—')}</span>
                    <div class="product-name">{(row.get('product') or '')[:60] or '—'}</div>
                    <div class="url-chip">{row['url'][:65]}</div>
                  </div>
                  <div class="price-display">${row['price_num']:.2f}</div>
                </div>
                """, unsafe_allow_html=True)

    # ── TAB 3: Full Matrix ────────────────────────────────────────────────
    with tab3:
        st.markdown("**Full brand × category price matrix — the complete picture.**")
        st.markdown("")

        if df.empty:
            st.info("No data yet.")
            return

        pivot = df.pivot_table(
            index='brand',
            columns='category',
            values='price_num',
            aggfunc='mean'
        ).round(2)

        # Add tier column for sorting
        pivot['_tier'] = pivot.index.map(
            lambda b: TIER_ORDER.index(COMPETITOR_LIBRARY.get(b, {}).get('tier', 'Rising DTC'))
            if COMPETITOR_LIBRARY.get(b, {}).get('tier', 'Rising DTC') in TIER_ORDER else 99
        )
        pivot = pivot.sort_values('_tier').drop(columns=['_tier'])

        # Format as currency
        def fmt(v):
            return f"${v:.2f}" if pd.notna(v) else "—"

        pivot_display = pivot.map(fmt)
        pivot_display.index.name = 'Brand'

        st.dataframe(pivot_display, use_container_width=True)

        st.markdown("")
        st.download_button(
            "📥 Export Matrix CSV",
            pivot.to_csv().encode(),
            "allrj_price_matrix.csv",
            "text/csv"
        )

        # Heatmap-style summary
        st.markdown('<div class="section-header">PRICE LEADERS BY CATEGORY</div>', unsafe_allow_html=True)
        st.markdown("The cheapest and most expensive brand in each tracked category.")

        cols_data = [c for c in pivot.columns]
        if cols_data:
            summary_rows = []
            for cat in cols_data:
                col_data = pivot[cat].dropna()
                if len(col_data) < 2:
                    continue
                summary_rows.append({
                    "Category":   cat,
                    "Cheapest":   f"{col_data.idxmin()} (${col_data.min():.2f})",
                    "Priciest":   f"{col_data.idxmax()} (${col_data.max():.2f})",
                    "Avg":        f"${col_data.mean():.2f}",
                    "Spread":     f"${col_data.max()-col_data.min():.2f}",
                })
            if summary_rows:
                st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)
