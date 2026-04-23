"""Alerts page — price change detection and notifications."""
import streamlit as st
import pandas as pd

try:
    from utils.database import get_alerts, mark_alerts_seen, get_unseen_alert_count
    DB_OK = True
except Exception:
    DB_OK = False


def render():
    unseen = get_unseen_alert_count() if DB_OK else 0

    st.markdown(f"""
    <div class="page-header">
        <div>
            <div class="page-title">PRICE <span>ALERTS</span></div>
            <div class="page-sub">Auto-detected price changes · Sales · Increases</div>
        </div>
        {'<div style="font-family:var(--font-head);font-size:2rem;color:var(--accent2);">'+str(unseen)+' NEW</div>' if unseen else ''}
    </div>
    """, unsafe_allow_html=True)

    if not DB_OK:
        st.error("Database unavailable.")
        return

    # Controls
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        filter_type = st.selectbox("Filter by Type", ["All", "Sale (−15%+)", "Price Drop", "Price Increase"])
    with col2:
        filter_brand = st.text_input("Filter by Brand", placeholder="e.g. Gymshark")
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("✓ Mark All Seen"):
            mark_alerts_seen()
            st.rerun()

    alerts = get_alerts(limit=100)

    # Apply filters
    if filter_type == "Sale (−15%+)":
        alerts = [a for a in alerts if a.get('alert_type') == 'sale']
    elif filter_type == "Price Drop":
        alerts = [a for a in alerts if a.get('change_pct', 0) < 0]
    elif filter_type == "Price Increase":
        alerts = [a for a in alerts if a.get('change_pct', 0) > 0]
    if filter_brand:
        alerts = [a for a in alerts if filter_brand.lower() in (a.get('brand') or '').lower()]

    if not alerts:
        st.markdown("""
        <div class="empty-state">
          <div class="empty-icon">🔔</div>
          <div class="empty-title">NO ALERTS</div>
          <div class="empty-sub">
            Price alerts fire automatically when a competitor's price changes ≥5%.<br>
            Sales (−15%+) get flagged separately so you can react fast.
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("**How alerts work:**")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.markdown("""
            <div class="data-row" style="flex-direction:column;align-items:flex-start;gap:6px;">
              <span class="badge badge-sale">🔥 SALE</span>
              <div style="font-size:0.8rem;color:#aaa;">Price dropped 15%+ below 30-day average. Competitor is running a promo.</div>
            </div>
            """, unsafe_allow_html=True)
        with col_b:
            st.markdown("""
            <div class="data-row" style="flex-direction:column;align-items:flex-start;gap:6px;">
              <span class="badge badge-down">▼ DROP</span>
              <div style="font-size:0.8rem;color:#aaa;">Price dropped 5–15%. Could be permanent reduction or short-term discount.</div>
            </div>
            """, unsafe_allow_html=True)
        with col_c:
            st.markdown("""
            <div class="data-row" style="flex-direction:column;align-items:flex-start;gap:6px;">
              <span class="badge badge-up">▲ RISE</span>
              <div style="font-size:0.8rem;color:#aaa;">Price increased 5%+. Competitor raising margin — potential opportunity for you.</div>
            </div>
            """, unsafe_allow_html=True)
        return

    # Render alerts
    sales = [a for a in alerts if a.get('alert_type') == 'sale']
    others = [a for a in alerts if a.get('alert_type') != 'sale']

    if sales:
        st.markdown('<div class="section-header">🔥 ACTIVE SALES DETECTED</div>', unsafe_allow_html=True)
        for a in sales:
            _render_alert_row(a)

    if others:
        st.markdown('<div class="section-header">📊 PRICE CHANGES</div>', unsafe_allow_html=True)
        for a in others:
            _render_alert_row(a)

    # Export
    st.markdown("---")
    df = pd.DataFrame(alerts)
    if not df.empty:
        st.download_button("📥 Export Alerts CSV",
                           df.to_csv(index=False).encode(),
                           "allrj_alerts.csv", "text/csv")


def _render_alert_row(a):
    pct = a.get('change_pct', 0)
    atype = a.get('alert_type', 'change')
    is_sale = atype == 'sale'

    if is_sale:
        badge_html = '<span class="badge badge-sale">🔥 SALE</span>'
    elif pct < 0:
        badge_html = f'<span class="badge badge-down">▼ DROP {abs(pct):.1f}%</span>'
    else:
        badge_html = f'<span class="badge badge-up">▲ RISE {abs(pct):.1f}%</span>'

    seen_style = 'opacity:0.45;' if a.get('seen') else ''
    dt = (a.get('detected_at') or '')[:16].replace('T', ' ')
    row_class = 'sale-row' if is_sale else ''

    st.markdown(f"""
    <div class="data-row {row_class}" style="{seen_style}">
      <div style="flex:1;">
        <span class="badge badge-brand">{a.get('brand','')}</span>
        {badge_html}
        <div class="product-name">{(a.get('product') or 'Unknown')[:65]}</div>
        <div class="url-chip">{a.get('url','')[:70]}</div>
        <div style="font-family:var(--font-mono);font-size:0.62rem;color:#333;margin-top:3px;">Detected: {dt}</div>
      </div>
      <div style="text-align:right;min-width:120px;">
        <div class="price-display {'sale' if is_sale else ''}">${a['new_price']:.2f}</div>
        <div class="price-change {'down' if pct < 0 else 'up'}">
          {'▼' if pct < 0 else '▲'} from ${a['old_price']:.2f}
        </div>
        {'<div style="font-size:0.65rem;color:#444;margin-top:2px;">💡 Consider matching promo</div>' if is_sale else ''}
      </div>
    </div>
    """, unsafe_allow_html=True)
