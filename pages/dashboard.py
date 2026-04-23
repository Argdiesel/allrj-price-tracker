from __future__ import annotations
"""Dashboard — intelligence first, structure second."""
import streamlit as st
import pandas as pd
from datetime import datetime

try:
    from utils.database import (
        get_summary_stats, get_alerts, get_promo_detection,
        get_latest_price_per_url, mark_alerts_seen
    )
    DB_OK = True
except Exception:
    DB_OK = False


def render():
    hour = datetime.now().hour
    greeting = "Good morning" if hour < 12 else ("Good afternoon" if hour < 17 else "Good evening")

    if DB_OK:
        stats  = get_summary_stats()
        alerts = get_alerts(limit=50)
        promos = get_promo_detection()
        latest = get_latest_price_per_url()
        unseen = stats.get("unseen_alerts", 0)
    else:
        stats  = {"total_scrapes":0,"brands_tracked":0,"urls_tracked":0,"sales_detected":0,"unseen_alerts":0}
        alerts = []
        promos = []
        latest = []
        unseen = 0

    has_data = bool(latest)

    st.markdown(f"""
    <div class="page-header">
      <div>
        <div class="page-title">COMMAND <span>CENTER</span></div>
        <div class="page-sub">{greeting} — here's what your competitors did while you were away</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── EMPTY STATE ───────────────────────────────────────
    if not has_data:
        st.markdown("""
        <div style="background:var(--surface);border:1px solid var(--border);
                    border-radius:var(--radius-lg);padding:48px 40px;text-align:center;margin-bottom:24px;">
          <div style="font-size:2.5rem;margin-bottom:16px;">⚡</div>
          <div style="font-family:var(--font-head);font-size:1.5rem;font-weight:700;
                      color:var(--text);margin-bottom:10px;">Run your first scan to unlock live intelligence</div>
          <div style="font-size:0.9rem;color:var(--text2);line-height:1.8;
                      max-width:500px;margin:0 auto 28px;">
            ALLRJ watches 25+ activewear competitors — Gymshark, Lululemon, Nike, AYBL and more.
            One scan tells you who dropped prices, who's running a sale, and what action to take.
          </div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("🔍  Scan Competitor Library", use_container_width=True):
                st.session_state.page = "tracker"
                st.rerun()
        with c2:
            if st.button("🏷️  Browse Brand Directory", use_container_width=True):
                st.session_state.page = "competitors"
                st.rerun()
        with c3:
            if st.button("⚙️  Add ScraperAPI Key", use_container_width=True):
                st.session_state.page = "settings"
                st.rerun()

        st.markdown("""
        <div style="margin-top:32px;">
          <div style="font-size:0.72rem;font-weight:600;text-transform:uppercase;
                      letter-spacing:1px;color:var(--muted);margin-bottom:16px;">
            What you'll see after your first scan
          </div>
          <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;">
            <div style="background:var(--surface);border:1px solid var(--border);
                        border-radius:var(--radius);padding:16px 18px;">
              <div style="font-size:1.1rem;margin-bottom:8px;">🔥</div>
              <div style="font-size:0.84rem;font-weight:600;color:var(--text);margin-bottom:4px;">
                Active Promotions</div>
              <div style="font-size:0.78rem;color:var(--text2);line-height:1.6;">
                See which competitors are running sales right now and how deep the discount is</div>
            </div>
            <div style="background:var(--surface);border:1px solid var(--border);
                        border-radius:var(--radius);padding:16px 18px;">
              <div style="font-size:1.1rem;margin-bottom:8px;">📊</div>
              <div style="font-size:0.84rem;font-weight:600;color:var(--text);margin-bottom:4px;">
                Price Movements</div>
              <div style="font-size:0.78rem;color:var(--text2);line-height:1.6;">
                Track every price change across 25+ brands with timestamps and trend direction</div>
            </div>
            <div style="background:var(--surface);border:1px solid var(--border);
                        border-radius:var(--radius);padding:16px 18px;">
              <div style="font-size:1.1rem;margin-bottom:8px;">💡</div>
              <div style="font-size:0.84rem;font-weight:600;color:var(--text);margin-bottom:4px;">
                Recommended Actions</div>
              <div style="font-size:0.78rem;color:var(--text2);line-height:1.6;">
                Plain-English advice on when to hold price, run a promo, or capture market share</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── METRICS ROW ───────────────────────────────────────
    alert_class = "alert" if unseen > 0 else ""
    st.markdown(f"""
    <div class="metric-grid">
      <div class="metric-card">
        <div class="metric-icon">🏷️</div>
        <div class="metric-val">{stats['brands_tracked']}</div>
        <div class="metric-lbl">Brands Tracked</div>
      </div>
      <div class="metric-card">
        <div class="metric-icon">📦</div>
        <div class="metric-val">{stats['urls_tracked']}</div>
        <div class="metric-lbl">Products Monitored</div>
      </div>
      <div class="metric-card">
        <div class="metric-icon">🔄</div>
        <div class="metric-val">{stats['total_scrapes']}</div>
        <div class="metric-lbl">Total Scans Run</div>
      </div>
      <div class="metric-card green">
        <div class="metric-icon">🔥</div>
        <div class="metric-val">{stats['sales_detected']}</div>
        <div class="metric-lbl">Sales Detected</div>
      </div>
      <div class="metric-card {alert_class}">
        <div class="metric-icon">🔔</div>
        <div class="metric-val">{unseen}</div>
        <div class="metric-lbl">New Alerts</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── INTELLIGENCE BRIEF ────────────────────────────────
    if promos or alerts:
        st.markdown('<div class="section-header">🧠 WHAT HAPPENED — PLAIN ENGLISH</div>', unsafe_allow_html=True)

        brief_lines = []
        if promos:
            sale_brands = list(set(p['brand'] for p in promos))
            brief_lines.append(f"<strong style='color:var(--text);'>{', '.join(sale_brands[:3])}</strong> "
                                f"{'are' if len(sale_brands) > 1 else 'is'} currently running promotions — "
                                f"prices are sitting below their 30-day average right now.")
        drops = [a for a in alerts if a.get('change_pct', 0) < -5 and a.get('alert_type') != 'sale']
        rises = [a for a in alerts if a.get('change_pct', 0) > 5]
        if drops:
            brief_lines.append(f"<strong style='color:var(--text);'>{len(drops)} price drop{'s' if len(drops)>1 else ''}</strong> "
                                f"detected recently — worth checking if these are permanent reductions or short-term promos.")
        if rises:
            brief_lines.append(f"<strong style='color:var(--text);'>{len(rises)} competitor{'s' if len(rises)>1 else ''}</strong> "
                                f"raised prices — a potential window to capture their price-sensitive customers.")
        if not brief_lines:
            brief_lines.append("Market looks stable right now. No major price movements detected since your last scan.")

        for line in brief_lines:
            st.markdown(f"""
            <div style="background:var(--surface);border-left:3px solid var(--accent);
                        border-radius:0 var(--radius) var(--radius) 0;
                        padding:14px 18px;margin-bottom:8px;
                        font-size:0.88rem;color:var(--text2);line-height:1.7;">
              {line}
            </div>
            """, unsafe_allow_html=True)

    # ── TWO COLUMN LAYOUT ─────────────────────────────────
    col1, col2 = st.columns([3, 2])

    with col1:
        # Active Promos
        st.markdown('<div class="section-header">🔥 ACTIVE COMPETITOR PROMOS</div>', unsafe_allow_html=True)
        if promos:
            for p in promos[:6]:
                pct = p.get("pct_change", 0)
                avg = p.get("avg_30d", 0)
                cur = p.get("current_price", 0)
                saving = avg - cur
                st.markdown(f"""
                <div class="data-row sale-row">
                  <div style="flex:1;min-width:0;">
                    <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
                      <span class="badge badge-brand">{p['brand']}</span>
                      <span class="badge badge-sale">SALE {pct:.0f}%</span>
                    </div>
                    <div class="product-name">{(p.get('product') or 'Product')[:55]}</div>
                    <div style="font-size:0.75rem;color:var(--green);margin-top:4px;line-height:1.5;">
                      💡 They dropped ${saving:.2f} below normal — monitor if this is a 
                      recurring pattern or a one-off clearance
                    </div>
                  </div>
                  <div style="text-align:right;min-width:90px;">
                    <div class="price-display sale">${cur:.2f}</div>
                    <div class="price-change down">was ${avg:.2f}</div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:var(--surface);border:1px dashed var(--border2);
                        border-radius:var(--radius);padding:28px;text-align:center;">
              <div style="font-size:1.5rem;margin-bottom:8px;">✅</div>
              <div style="font-size:0.84rem;font-weight:600;color:var(--text);margin-bottom:4px;">
                No active promotions detected</div>
              <div style="font-size:0.75rem;color:var(--text2);">
                Your competitors are holding full price right now</div>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        # Recent alerts
        st.markdown('<div class="section-header">🔔 RECENT ALERTS</div>', unsafe_allow_html=True)
        if alerts:
            for a in alerts[:8]:
                pct  = a.get("change_pct", 0)
                atype = a.get("alert_type", "change")
                is_sale = atype == "sale"
                badge = "badge-sale" if is_sale else ("badge-down" if pct < 0 else "badge-up")
                label = "🔥 SALE" if is_sale else ("▼ DROP" if pct < 0 else "▲ RISE")
                seen_opacity = "0.45" if a.get("seen") else "1"
                dt = (a.get("detected_at") or "")[:16].replace("T", " ")
                st.markdown(f"""
                <div class="data-row" style="opacity:{seen_opacity};padding:10px 14px;">
                  <div style="flex:1;min-width:0;">
                    <div style="display:flex;align-items:center;gap:6px;margin-bottom:4px;">
                      <span class="badge badge-brand" style="font-size:0.6rem;">{a['brand']}</span>
                      <span class="badge {badge}" style="font-size:0.6rem;">{label} {abs(pct):.0f}%</span>
                    </div>
                    <div style="font-size:0.78rem;color:var(--text2);line-height:1.4;">
                      {(a.get('product') or '')[:38]}</div>
                    <div style="font-size:0.65rem;color:var(--muted);margin-top:2px;">{dt}</div>
                  </div>
                  <div style="text-align:right;min-width:75px;">
                    <div style="font-family:var(--font-head);font-size:1.2rem;
                                font-weight:700;color:var(--text);">${a['new_price']:.2f}</div>
                    <div style="font-size:0.65rem;color:var(--muted);">from ${a['old_price']:.2f}</div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

            if unseen > 0:
                if st.button("✓ Mark all seen", key="mark_seen"):
                    mark_alerts_seen()
                    st.rerun()
        else:
            st.markdown("""
            <div style="background:var(--surface);border:1px dashed var(--border2);
                        border-radius:var(--radius);padding:28px;text-align:center;">
              <div style="font-size:1.5rem;margin-bottom:8px;">🔔</div>
              <div style="font-size:0.84rem;font-weight:600;color:var(--text);margin-bottom:4px;">
                No alerts yet</div>
              <div style="font-size:0.75rem;color:var(--text2);">
                Price changes of 5%+ trigger automatic alerts</div>
            </div>
            """, unsafe_allow_html=True)

    # ── LATEST PRICES TABLE ───────────────────────────────
    if latest:
        st.markdown('<div class="section-header">📋 LATEST TRACKED PRICES</div>', unsafe_allow_html=True)
        df = pd.DataFrame(latest)
        df = df[df["price_num"].notna()].sort_values("brand")

        if not df.empty:
            display = df[["brand","category","product","price_raw","method","scraped_at"]].copy()
            display.columns = ["Brand","Category","Product","Price","Method","Last Scanned"]
            display["Product"] = display["Product"].str[:45]
            display["Last Scanned"] = display["Last Scanned"].str[:16].str.replace("T"," ")
            st.dataframe(display, use_container_width=True, hide_index=True)

            st.markdown("")
            col_a, col_b, col_c, col_d = st.columns(4)
            with col_a:
                if st.button("🔍  Run New Scan", use_container_width=True):
                    st.session_state.page = "tracker"
                    st.rerun()
            with col_b:
                if st.button("📈  View Trends", use_container_width=True):
                    st.session_state.page = "history"
                    st.rerun()
            with col_c:
                if st.button("🧠  Pricing Strategy", use_container_width=True):
                    st.session_state.page = "strategy"
                    st.rerun()
            with col_d:
                csv = display.to_csv(index=False).encode()
                st.download_button("📥  Export CSV", csv,
                                   f"allrj_{datetime.now().strftime('%Y%m%d')}.csv",
                                   "text/csv", use_container_width=True)
