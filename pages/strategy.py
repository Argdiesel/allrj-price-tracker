"""
Pricing Strategy page — auto-generated insights per category and brand tier.
The intelligence layer that separates ALLRJ from a simple price tracker.
"""
import streamlit as st
import pandas as pd


try:
    from utils.database import get_price_history, get_latest_price_per_url, get_promo_detection
    from data.competitors import COMPETITOR_LIBRARY, get_categories, TIER_ORDER
    DB_OK = True
except Exception as e:
    DB_OK = False
    _err = str(e)


CATEGORY_BENCHMARKS = {
    "Leggings":    {"budget": 25, "mid": 55, "premium": 90,  "insight": "Leggings are the highest-margin category. Premium brands anchor at $90–$128. DTC sweet spot is $45–$65."},
    "Sports Bras": {"budget": 20, "mid": 40, "premium": 68,  "insight": "Sports bras drive repeat purchase. Brands that win on fit own the customer long-term. $35–$55 is the volume sweet spot."},
    "Shorts":      {"budget": 20, "mid": 40, "premium": 68,  "insight": "Men's shorts are highly price-sensitive. $30–$45 drives volume. Premium brands charge $65+ on technical fabrics."},
    "Tops":        {"budget": 18, "mid": 32, "premium": 55,  "insight": "Tops are entry products — customers buy cheap then upgrade. Use tops to acquire, leggings to retain."},
    "Hoodies":     {"budget": 40, "mid": 65, "premium": 120, "insight": "Hoodies are lifestyle purchases. Strong brand equity = price inelasticity. $65–$85 is the DTC sweet spot."},
}

TIER_STRATEGIES = {
    "Major": {
        "icon": "🏢",
        "strategy": "Volume + brand equity",
        "pricing": "Mid-to-premium with frequent 20–30% sales",
        "threat": "Distribution scale and brand recognition",
        "opportunity": "They're slow to react to trends. Out-niche them on specific categories.",
        "color": "#EF4444",
    },
    "Premium DTC": {
        "icon": "💎",
        "strategy": "Premium positioning + community",
        "pricing": "High anchor prices, rare discounts (<10% frequency)",
        "threat": "Strong brand loyalty and premium perception",
        "opportunity": "Their prices are aspirational — you can position at 70% of their price with 90% of the quality story.",
        "color": "#8B5CF6",
    },
    "Rising DTC": {
        "icon": "🚀",
        "strategy": "Aggressive growth + social-first",
        "pricing": "Mid-market with frequent promos to drive acquisition",
        "threat": "Fast trend adoption and social proof",
        "opportunity": "They compete on price — you can compete on quality and service at the same price point.",
        "color": "#10B981",
    },
}


def render():
    st.markdown("""
    <div class="page-header">
        <div>
            <div class="page-title">PRICING <span>STRATEGY</span></div>
            <div class="page-sub">Category benchmarks · Tier analysis · Actionable intelligence</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not DB_OK:
        st.error(f"Database error: {_err}")
        return

    history = get_price_history(days=30)
    latest  = get_latest_price_per_url()
    promos  = get_promo_detection()

    has_data = bool(latest)

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊  Category Benchmarks",
        "🏆  Tier Analysis",
        "🔥  Live Opportunities",
        "💡  Your Playbook",
    ])

    # ── TAB 1: Category Benchmarks ────────────────────────────────────────
    with tab1:
        st.markdown("**Where does each category sit in the market — and where should YOU price?**")
        st.markdown("")

        cats = get_categories()
        if has_data:
            df_latest = pd.DataFrame(latest)
            df_valid  = df_latest[df_latest['price_num'].notna()]

        for cat in cats:
            bench = CATEGORY_BENCHMARKS.get(cat)
            if not bench:
                continue

            st.markdown(f'<div class="section-header">👕 {cat.upper()}</div>', unsafe_allow_html=True)

            col_bench, col_live = st.columns([2, 1])

            with col_bench:
                # Price tier bar
                st.markdown(f"""
                <div style="background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:16px 20px;margin-bottom:8px;">
                  <div style="display:flex;justify-content:space-between;margin-bottom:10px;">
                    <span style="font-size:0.72rem;color:var(--text2);font-weight:600;text-transform:uppercase;letter-spacing:0.8px;">Market Price Range</span>
                  </div>
                  <div style="display:flex;gap:8px;align-items:center;margin-bottom:12px;">
                    <div style="background:var(--green-dim);border:1px solid rgba(16,185,129,0.2);border-radius:6px;padding:8px 14px;text-align:center;flex:1;">
                      <div style="font-family:var(--font-head);font-size:1.3rem;font-weight:700;color:var(--green);">${bench['budget']}</div>
                      <div style="font-size:0.62rem;color:var(--text2);text-transform:uppercase;letter-spacing:0.8px;">Budget floor</div>
                    </div>
                    <div style="color:var(--muted);font-size:1.2rem;">→</div>
                    <div style="background:var(--accent-dim);border:1px solid rgba(99,102,241,0.2);border-radius:6px;padding:8px 14px;text-align:center;flex:1;">
                      <div style="font-family:var(--font-head);font-size:1.3rem;font-weight:700;color:var(--accent-lt);">${bench['mid']}</div>
                      <div style="font-size:0.62rem;color:var(--text2);text-transform:uppercase;letter-spacing:0.8px;">DTC sweet spot</div>
                    </div>
                    <div style="color:var(--muted);font-size:1.2rem;">→</div>
                    <div style="background:var(--yellow-dim);border:1px solid rgba(245,158,11,0.2);border-radius:6px;padding:8px 14px;text-align:center;flex:1;">
                      <div style="font-family:var(--font-head);font-size:1.3rem;font-weight:700;color:var(--yellow);">${bench['premium']}+</div>
                      <div style="font-size:0.62rem;color:var(--text2);text-transform:uppercase;letter-spacing:0.8px;">Premium ceiling</div>
                    </div>
                  </div>
                  <div style="font-size:0.78rem;color:var(--text2);line-height:1.6;padding:10px 14px;background:var(--bg2);border-radius:6px;">
                    💡 {bench['insight']}
                  </div>
                </div>
                """, unsafe_allow_html=True)

            with col_live:
                if has_data and not df_valid.empty:
                    cat_data = df_valid[df_valid['category'] == cat]
                    if not cat_data.empty:
                        avg = cat_data['price_num'].mean()
                        low = cat_data['price_num'].min()
                        high = cat_data['price_num'].max()
                        count = len(cat_data)
                        # Position vs sweet spot
                        sweet = bench['mid']
                        diff = avg - sweet
                        diff_pct = (diff / sweet) * 100
                        arrow = "▲" if diff > 0 else "▼"
                        color = "var(--red)" if diff > 5 else ("var(--green)" if diff < -5 else "var(--accent-lt)")
                        st.markdown(f"""
                        <div style="background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:16px;height:100%;">
                          <div style="font-size:0.68rem;color:var(--text2);text-transform:uppercase;letter-spacing:0.8px;font-weight:600;margin-bottom:10px;">Live Market Data</div>
                          <div style="font-family:var(--font-head);font-size:1.6rem;font-weight:700;color:var(--text);">${avg:.0f}</div>
                          <div style="font-size:0.72rem;color:var(--text2);">avg across {count} products</div>
                          <div style="margin-top:8px;font-size:0.72rem;color:{color};">{arrow} {abs(diff_pct):.0f}% vs sweet spot</div>
                          <div style="margin-top:6px;font-size:0.68rem;color:var(--muted);">Range: ${low:.0f} – ${high:.0f}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="background:var(--surface);border:1px dashed var(--border2);border-radius:var(--radius);padding:16px;text-align:center;">
                          <div style="font-size:0.72rem;color:var(--muted);">No live data yet<br>Run a scan to populate</div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background:var(--surface);border:1px dashed var(--border2);border-radius:var(--radius);padding:16px;text-align:center;">
                      <div style="font-size:0.72rem;color:var(--muted);">Run a scan to see<br>live market prices</div>
                    </div>
                    """, unsafe_allow_html=True)

    # ── TAB 2: Tier Analysis ──────────────────────────────────────────────
    with tab2:
        st.markdown("**How each competitive tier prices — and how to respond.**")
        st.markdown("")

        for tier in TIER_ORDER:
            info = TIER_STRATEGIES[tier]
            brands_in_tier = [b for b, d in COMPETITOR_LIBRARY.items() if d["tier"] == tier]

            # Avg price for this tier from live data
            tier_avg = None
            if has_data:
                df_l = pd.DataFrame(latest)
                df_l = df_l[df_l['price_num'].notna()]
                tier_brands = [b for b, d in COMPETITOR_LIBRARY.items() if d["tier"] == tier]
                tier_data = df_l[df_l['brand'].isin(tier_brands)]
                if not tier_data.empty:
                    tier_avg = tier_data['price_num'].mean()

            st.markdown(f"""
            <div style="background:var(--surface);border:1px solid var(--border);border-radius:var(--radius-lg);padding:20px 24px;margin-bottom:14px;position:relative;overflow:hidden;">
              <div style="position:absolute;top:0;left:0;bottom:0;width:3px;background:{info['color']};border-radius:var(--radius-lg) 0 0 var(--radius-lg);"></div>
              <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:16px;">
                <div style="flex:1;">
                  <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">
                    <span style="font-size:1.3rem;">{info['icon']}</span>
                    <div>
                      <div style="font-family:var(--font-head);font-size:1.1rem;font-weight:700;color:var(--text);">{tier}</div>
                      <div style="font-size:0.7rem;color:var(--text2);">{len(brands_in_tier)} brands tracked</div>
                    </div>
                  </div>
                  <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px;">
                    <div>
                      <div style="font-size:0.65rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.8px;margin-bottom:3px;">Strategy</div>
                      <div style="font-size:0.8rem;color:var(--text2);">{info['strategy']}</div>
                    </div>
                    <div>
                      <div style="font-size:0.65rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.8px;margin-bottom:3px;">Pricing Behaviour</div>
                      <div style="font-size:0.8rem;color:var(--text2);">{info['pricing']}</div>
                    </div>
                    <div>
                      <div style="font-size:0.65rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.8px;margin-bottom:3px;">⚠️ Threat</div>
                      <div style="font-size:0.8rem;color:var(--red);">{info['threat']}</div>
                    </div>
                    <div>
                      <div style="font-size:0.65rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.8px;margin-bottom:3px;">✅ Your Opportunity</div>
                      <div style="font-size:0.8rem;color:var(--green);">{info['opportunity']}</div>
                    </div>
                  </div>
                  <div style="display:flex;flex-wrap:wrap;gap:6px;">
                    {"".join([f'<span class="badge badge-brand">{b}</span>' for b in brands_in_tier])}
                  </div>
                </div>
                {f'<div style="text-align:right;min-width:100px;"><div style="font-size:0.65rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.8px;margin-bottom:4px;">Live Avg</div><div style="font-family:var(--font-head);font-size:2rem;font-weight:700;color:var(--text);">${tier_avg:.0f}</div></div>' if tier_avg else ''}
              </div>
            </div>
            """, unsafe_allow_html=True)

    # ── TAB 3: Live Opportunities ─────────────────────────────────────────
    with tab3:
        st.markdown("**Real-time pricing gaps and opportunities based on your live data.**")
        st.markdown("")

        if not has_data:
            st.markdown("""
            <div class="empty-state">
              <div class="empty-icon">🔥</div>
              <div class="empty-title">RUN A SCAN FIRST</div>
              <div class="empty-sub">Track competitor prices to unlock live opportunity detection</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("→ Go Track Prices"):
                st.session_state.page = 'tracker'
                st.rerun()
            return

        df_l = pd.DataFrame(latest)
        df_valid = df_l[df_l['price_num'].notna()]

        # Active promos
        if promos:
            st.markdown('<div class="section-header">🔥 COMPETITORS CURRENTLY ON SALE — ACT NOW</div>', unsafe_allow_html=True)
            for p in promos:
                pct = p.get('pct_change', 0)
                st.markdown(f"""
                <div class="data-row sale-row">
                  <div style="flex:1;">
                    <span class="badge badge-brand">{p['brand']}</span>
                    <span class="badge badge-sale" style="margin-left:6px;">SALE {pct:.0f}%</span>
                    <div class="product-name">{(p.get('product') or '')[:60]}</div>
                    <div style="font-size:0.75rem;color:var(--green);margin-top:4px;">
                      💡 Opportunity: They're discounting. Hold your price and emphasise value — or match for 72hrs to capture the traffic.
                    </div>
                  </div>
                  <div style="text-align:right;min-width:110px;">
                    <div class="price-display sale">${p['current_price']:.2f}</div>
                    <div class="price-change down">was ${p['avg_30d']:.2f}</div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

        # Price gaps by category
        st.markdown('<div class="section-header">📊 CATEGORY PRICE GAPS</div>', unsafe_allow_html=True)
        st.markdown("Categories where you can undercut premium brands without going below mid-market.")

        for cat in get_categories():
            cat_data = df_valid[df_valid['category'] == cat]
            if cat_data.empty or len(cat_data) < 2:
                continue
            bench = CATEGORY_BENCHMARKS.get(cat, {})
            if not bench:
                continue

            premium_brands = [b for b, d in COMPETITOR_LIBRARY.items() if d["tier"] in ["Major", "Premium DTC"]]
            rising_brands  = [b for b, d in COMPETITOR_LIBRARY.items() if d["tier"] == "Rising DTC"]

            premium_data = cat_data[cat_data['brand'].isin(premium_brands)]
            rising_data  = cat_data[cat_data['brand'].isin(rising_brands)]

            if premium_data.empty or rising_data.empty:
                continue

            premium_avg = premium_data['price_num'].mean()
            rising_avg  = rising_data['price_num'].mean()
            gap = premium_avg - rising_avg
            sweet = bench['mid']

            if gap > 10:
                st.markdown(f"""
                <div class="data-row">
                  <div style="flex:1;">
                    <div style="font-weight:600;font-size:0.9rem;color:var(--text);">{cat}</div>
                    <div style="font-size:0.75rem;color:var(--text2);margin-top:3px;">
                      Premium avg <strong style="color:var(--text)">${premium_avg:.0f}</strong> vs Rising DTC avg <strong style="color:var(--text)">${rising_avg:.0f}</strong> — gap of <strong style="color:var(--green)">${gap:.0f}</strong>
                    </div>
                    <div style="font-size:0.72rem;color:var(--accent-lt);margin-top:5px;">
                      💡 Price at ${sweet:.0f} — above rising DTC, below premium. Maximum volume, strong margin.
                    </div>
                  </div>
                  <div style="text-align:right;min-width:90px;">
                    <div style="font-size:0.65rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.8px;">Suggested price</div>
                    <div style="font-family:var(--font-head);font-size:1.5rem;font-weight:700;color:var(--accent-lt);">${sweet}</div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

    # ── TAB 4: Your Playbook ──────────────────────────────────────────────
    with tab4:
        st.markdown("**Concrete pricing plays for ALLRJ — based on market structure and competitor behaviour.**")
        st.markdown("")

        plays = [
            {
                "title": "The Premium Undercut",
                "badge": "High Impact",
                "badge_color": "badge-json",
                "description": "Price 15–25% below Lululemon and Alo on your hero legging. You capture the shopper who wants premium quality but can't justify $128. This is Gymshark's founding strategy.",
                "action": "Pick your best legging. Price it at $65–$75. Shoot content next to a Lululemon product. Let the quality speak.",
                "metric": "Expected: 2–3x conversion rate vs budget positioning",
            },
            {
                "title": "The Promo Timing Play",
                "badge": "Quick Win",
                "badge_color": "badge-api",
                "description": "Gymshark runs sales every 6–8 weeks. When they do, customers are primed to buy activewear. Run your promo 1 week BEFORE theirs ends — catch the buyers who missed out.",
                "action": "Set a Gymshark sale alert in this app. When it fires, prep a 72-hour counter-promo at 10–15% off.",
                "metric": "Expected: 40–60% uplift in promo period vs baseline",
            },
            {
                "title": "The Category Leader",
                "badge": "Long Term",
                "badge_color": "badge-html",
                "description": "Rising DTC brands scatter across every category. Own ONE category completely — be the brand that everyone associates with the best seamless legging under $60, for example.",
                "action": "Pick the category with the biggest premium gap. Invest 60% of your product budget there. Build depth, not breadth.",
                "metric": "Expected: 3–5x repeat purchase rate in owned category",
            },
            {
                "title": "The Anchor & Decoy",
                "badge": "Margin Play",
                "badge_color": "badge-brand",
                "description": "Introduce a premium tier product at $95–$110. Even if it sells slowly, it makes your $55 product look like incredible value — and lifts AOV across the board.",
                "action": "Launch one 'hero' product at premium price with premium branding. Measure how it affects conversion on your mid-tier.",
                "metric": "Expected: 8–15% AOV increase across range",
            },
            {
                "title": "The Rising Brand Signal",
                "badge": "Watch List",
                "badge_color": "badge-down",
                "description": "YoungLA, NVGTN, and AYBL are pricing aggressively to grow. When they raise prices, it signals confidence — and creates a gap you can fill with similar positioning.",
                "action": "Track their prices weekly. Any increase of 10%+ is a signal. Position within 5% of their new price immediately.",
                "metric": "Expected: Capture displaced price-sensitive customers",
            },
        ]

        for play in plays:
            st.markdown(f"""
            <div style="background:var(--surface);border:1px solid var(--border);border-radius:var(--radius-lg);padding:20px 24px;margin-bottom:12px;">
              <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
                <div style="font-family:var(--font-head);font-size:1.05rem;font-weight:700;color:var(--text);">{play['title']}</div>
                <span class="badge {play['badge_color']}">{play['badge']}</span>
              </div>
              <div style="font-size:0.82rem;color:var(--text2);line-height:1.7;margin-bottom:12px;">{play['description']}</div>
              <div style="background:var(--bg2);border-radius:8px;padding:12px 16px;margin-bottom:10px;">
                <div style="font-size:0.65rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.8px;margin-bottom:4px;font-weight:600;">→ Action</div>
                <div style="font-size:0.8rem;color:var(--text);line-height:1.6;">{play['action']}</div>
              </div>
              <div style="font-size:0.72rem;color:var(--accent-lt);font-style:italic;">{play['metric']}</div>
            </div>
            """, unsafe_allow_html=True)
