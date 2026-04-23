"""Competitors page — browse the pre-built brand library."""
import streamlit as st

try:
    from data.competitors import COMPETITOR_LIBRARY, get_all_competitor_urls
    DATA_OK = True
except Exception:
    DATA_OK = False


TIER_COLORS = {
    "Major":       "#FF6B35",
    "Premium":     "#C8A96E",
    "Premium DTC": "#7EC8C8",
    "DTC Mid":     "#4D9FFF",
}


def render():
    st.markdown("""
    <div class="page-header">
        <div>
            <div class="page-title">COMPETITOR <span>LIBRARY</span></div>
            <div class="page-sub">Pre-built activewear brand database — zero setup required</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not DATA_OK:
        st.error("Competitor library unavailable.")
        return

    all_rows = get_all_competitor_urls()

    # Summary stats
    brands = list(COMPETITOR_LIBRARY.keys())
    all_cats = set(r['category'] for r in all_rows)
    total_urls = len(all_rows)

    st.markdown(f"""
    <div class="metric-grid">
      <div class="metric-card">
        <div class="metric-val">{len(brands)}</div>
        <div class="metric-lbl">Brands Pre-loaded</div>
      </div>
      <div class="metric-card">
        <div class="metric-val">{total_urls}</div>
        <div class="metric-lbl">Products Ready to Track</div>
      </div>
      <div class="metric-card green">
        <div class="metric-val">{len(all_cats)}</div>
        <div class="metric-lbl">Categories</div>
      </div>
      <div class="metric-card">
        <div class="metric-val">$0</div>
        <div class="metric-lbl">Setup Cost</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-header">BRAND DIRECTORY</div>', unsafe_allow_html=True)

    # Brand cards in a 3-col grid
    cols = st.columns(3)
    for i, (brand_name, info) in enumerate(COMPETITOR_LIBRARY.items()):
        col = cols[i % 3]
        tier = info.get('tier', '')
        tier_color = TIER_COLORS.get(tier, '#555')
        total_products = sum(len(v) for v in info['categories'].values())
        categories_list = ', '.join(info['categories'].keys())
        domain = info.get('domain', '')

        with col:
            st.markdown(f"""
            <div class="data-row" style="flex-direction:column; align-items:flex-start; padding:18px 20px; margin-bottom:12px;">
              <div style="display:flex; justify-content:space-between; width:100%; align-items:flex-start;">
                <div>
                  <div style="font-family:var(--font-head);font-size:1.3rem;letter-spacing:1px;color:var(--text);">{brand_name}</div>
                  <div style="font-family:var(--font-mono);font-size:0.65rem;color:#444;">{domain}</div>
                </div>
                <span style="font-size:0.65rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;
                             padding:3px 9px;border-radius:20px;
                             background:rgba(255,255,255,0.04);
                             color:{tier_color};
                             border:1px solid {tier_color}33;">{tier}</span>
              </div>
              <div style="margin-top:10px;width:100%;">
                <div style="font-size:0.72rem;color:#555;margin-bottom:6px;text-transform:uppercase;letter-spacing:1px;">Categories</div>
                <div style="font-size:0.78rem;color:#888;">{categories_list}</div>
              </div>
              <div style="margin-top:10px;display:flex;justify-content:space-between;width:100%;align-items:center;">
                <span style="font-family:var(--font-mono);font-size:0.72rem;color:#444;">{total_products} products</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"Track {brand_name}", key=f"track_brand_{brand_name}"):
                # Pre-select this brand in tracker
                st.session_state.page = 'tracker'
                st.session_state.preselect_brand = brand_name
                st.rerun()

    # Full URL table
    st.markdown('<div class="section-header">FULL PRODUCT LIST</div>', unsafe_allow_html=True)
    st.markdown("All pre-loaded product URLs — ready to track on demand.")

    import pandas as pd
    df = pd.DataFrame(all_rows)[['brand', 'tier', 'category', 'url']]
    df.columns = ['Brand', 'Tier', 'Category', 'URL']
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Add custom competitor
    st.markdown('<div class="section-header">➕ ADD CUSTOM COMPETITOR</div>', unsafe_allow_html=True)
    st.markdown("Track a brand not in the library — we'll remember it for future scans.")

    c1, c2, c3 = st.columns(3)
    with c1:
        new_brand = st.text_input("Brand Name", placeholder="e.g. Fabletics")
    with c2:
        new_cat = st.text_input("Category", placeholder="e.g. Leggings")
    with c3:
        new_url = st.text_input("Product URL", placeholder="https://...")

    if st.button("➕ Add to Library"):
        if new_brand and new_url:
            try:
                from utils.database import add_to_watchlist
                add_to_watchlist(new_url, new_brand, new_cat, new_brand)
                st.success(f"✅ Added {new_brand} to your watchlist! Track it from the Tracker page.")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please enter at least a Brand name and URL.")
