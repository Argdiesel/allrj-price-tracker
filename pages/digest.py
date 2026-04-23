"""
AI Digest — uses Claude API to generate a weekly competitor intelligence brief.
This is the defensible moat: not just data, but actionable narrative.
"""
import streamlit as st
import json
from datetime import datetime

try:
    from utils.database import get_price_history, get_alerts, get_promo_detection, get_summary_stats
    DB_OK = True
except Exception:
    DB_OK = False


def render():
    st.markdown("""
    <div class="page-header">
        <div>
            <div class="page-title">AI <span>DIGEST</span></div>
            <div class="page-sub">Weekly competitor intelligence · Powered by Claude</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background:rgba(200,255,0,0.04);border:1px solid rgba(200,255,0,0.15);
                border-radius:12px;padding:16px 20px;margin-bottom:20px;">
      <div style="font-size:0.75rem;color:#666;text-transform:uppercase;letter-spacing:1px;">What this does</div>
      <div style="font-size:0.88rem;color:#ccc;margin-top:6px;line-height:1.6;">
        Analyses your last 30 days of competitor price data and generates a plain-English intelligence brief —
        what changed, which brands are running promos, and what actions you should take.
        This is what separates ALLRJ from a spreadsheet.
      </div>
    </div>
    """, unsafe_allow_html=True)

    # API key input
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("**No Anthropic API key needed** — this runs through the built-in Claude integration.")

    # Gather context data
    if DB_OK:
        history = get_price_history(days=30)
        alerts  = get_alerts(limit=30)
        promos  = get_promo_detection()
        stats   = get_summary_stats()
    else:
        history, alerts, promos, stats = [], [], [], {}

    has_data = bool(history or alerts)

    # Show data summary
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        st.metric("Price Records", len(history))
    with col_s2:
        st.metric("Alerts to Analyse", len(alerts))
    with col_s3:
        st.metric("Active Promos", len(promos))

    if not has_data:
        st.markdown("""
        <div class="empty-state">
          <div class="empty-icon">🤖</div>
          <div class="empty-title">NOT ENOUGH DATA YET</div>
          <div class="empty-sub">Run at least one price scan to generate your first AI digest</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("→ Go scan prices first"):
            st.session_state.page = 'tracker'
            st.rerun()
        return

    # Digest type selector
    digest_type = st.selectbox("Digest Type", [
        "Weekly Competitor Brief",
        "Promo Alert Analysis",
        "Pricing Strategy Recommendations",
        "Brand-Specific Deep Dive",
    ])

    brand_focus = ""
    if digest_type == "Brand-Specific Deep Dive":
        brands = list(set(r.get('brand','') for r in history if r.get('brand')))
        brand_focus = st.selectbox("Select Brand", sorted(brands))

    if st.button("🤖  GENERATE AI DIGEST", type="primary"):
        _generate_digest(history, alerts, promos, stats, digest_type, brand_focus)

    # Show previous digest if in session
    if st.session_state.get('last_digest'):
        st.markdown("---")
        st.markdown('<div class="section-header">LATEST DIGEST</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:24px;line-height:1.8;font-size:0.9rem;color:#ddd;">
        {st.session_state.last_digest.replace(chr(10), '<br>')}
        </div>
        """, unsafe_allow_html=True)

        col_copy, col_dl = st.columns([1, 1])
        with col_dl:
            st.download_button(
                "📥 Download Brief",
                st.session_state.last_digest.encode(),
                f"allrj_digest_{datetime.now().strftime('%Y%m%d')}.txt",
                "text/plain",
            )


def _build_prompt(history, alerts, promos, stats, digest_type, brand_focus):
    # Summarise data for the prompt (keep it concise)
    brands_seen = list(set(r.get('brand','') for r in history if r.get('brand')))

    # Price summary per brand
    brand_prices = {}
    for r in history:
        b = r.get('brand','')
        p = r.get('price_num')
        if b and p:
            if b not in brand_prices:
                brand_prices[b] = []
            brand_prices[b].append(p)

    brand_summary = []
    for b, prices in brand_prices.items():
        avg = sum(prices) / len(prices)
        brand_summary.append(f"{b}: avg ${avg:.2f}, min ${min(prices):.2f}, max ${max(prices):.2f} ({len(prices)} data points)")

    alert_summary = []
    for a in alerts[:15]:
        alert_summary.append(
            f"{a.get('brand')}: {a.get('product','')[:40]} went from ${a.get('old_price',0):.2f} to ${a.get('new_price',0):.2f} ({a.get('change_pct',0):+.1f}%)"
        )

    promo_summary = []
    for p in promos[:10]:
        promo_summary.append(
            f"{p.get('brand')}: {p.get('product','')[:40]} — currently ${p.get('current_price',0):.2f} vs ${p.get('avg_30d',0):.2f} 30d avg ({p.get('pct_change',0):.1f}%)"
        )

    context = f"""
PRICE INTELLIGENCE DATA (last 30 days):

BRANDS TRACKED: {', '.join(brands_seen)}
TOTAL SCANS: {stats.get('total_scrapes', 0)}

PRICE SUMMARY BY BRAND:
{chr(10).join(brand_summary) or 'No data'}

PRICE CHANGE ALERTS:
{chr(10).join(alert_summary) or 'No alerts'}

ACTIVE PROMOS (price 15%+ below 30d avg):
{chr(10).join(promo_summary) or 'None detected'}
"""

    if digest_type == "Weekly Competitor Brief":
        instruction = """Generate a sharp, executive-level weekly competitor pricing brief for a DTC activewear brand (ALLRJ).
Format it as:
1. HEADLINE (1 sentence — the single most important thing this week)
2. KEY MOVEMENTS (bullet points — what changed and why it matters)
3. ACTIVE PROMOS (which competitors are running sales right now)
4. STRATEGIC RECOMMENDATIONS (3 concrete actions ALLRJ should take this week)
5. WATCH LIST (what to monitor closely next week)

Be direct, specific, and actionable. Write like a senior market analyst, not a robot. Use dollar figures and percentages throughout."""

    elif digest_type == "Promo Alert Analysis":
        instruction = """Analyse the active competitor promotions detected and write a promo intelligence brief.
Include: which brands are on sale, estimated duration patterns based on historical data, whether ALLRJ should match/beat/ignore each promo, and timing recommendations.
Be specific and commercial in tone."""

    elif digest_type == "Pricing Strategy Recommendations":
        instruction = """Based on competitor pricing data, generate 5 specific pricing strategy recommendations for ALLRJ.
For each recommendation: state the observation, the strategic implication, and the concrete action.
Focus on margin protection, competitive positioning, and promotional timing."""

    elif digest_type == "Brand-Specific Deep Dive":
        context += f"\n\nFOCUS BRAND: {brand_focus}"
        instruction = f"""Write a deep-dive competitive analysis on {brand_focus} specifically.
Cover: their current pricing vs market average, recent price movements, promotional patterns, and what ALLRJ can learn from their strategy.
Be specific and reference the actual numbers in the data."""

    return f"""{instruction}

{context}

Write in clear, confident prose. No fluff. This is for a busy founder who reads it in 90 seconds."""


def _generate_digest(history, alerts, promos, stats, digest_type, brand_focus):
    prompt = _build_prompt(history, alerts, promos, stats, digest_type, brand_focus)

    with st.spinner("🤖 Claude is analysing your competitor data..."):
        try:
            import requests as req
            response = req.post(
                "https://api.anthropic.com/v1/messages",
                headers={"Content-Type": "application/json"},
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 1000,
                    "messages": [{"role": "user", "content": prompt}],
                },
                timeout=30,
            )
            data = response.json()
            text = "".join(
                block.get("text", "") for block in data.get("content", [])
                if block.get("type") == "text"
            )
            if text:
                st.session_state.last_digest = text
                st.rerun()
            else:
                st.error(f"No response from Claude. Raw: {str(data)[:200]}")
        except Exception as e:
            st.error(f"API error: {e}")
            # Fallback: generate a static digest from the data
            _fallback_digest(history, alerts, promos)


def _fallback_digest(history, alerts, promos):
    """Generate a basic digest without AI when API is unavailable."""
    lines = ["**WEEKLY COMPETITOR BRIEF**\n"]

    if promos:
        lines.append(f"🔥 **{len(promos)} competitor(s) currently running promotions:**")
        for p in promos[:5]:
            lines.append(f"  • {p.get('brand')}: ${p.get('current_price',0):.2f} (was ${p.get('avg_30d',0):.2f} avg, {p.get('pct_change',0):.1f}%)")

    if alerts:
        drops = [a for a in alerts if (a.get('change_pct',0)) < 0]
        rises = [a for a in alerts if (a.get('change_pct',0)) > 0]
        if drops:
            lines.append(f"\n📉 **{len(drops)} price drops detected this period**")
        if rises:
            lines.append(f"\n📈 **{len(rises)} price increases detected this period**")

    if not promos and not alerts:
        lines.append("No significant price movements detected in the tracked period.")
        lines.append("Recommendation: expand your competitor tracking list and run daily scans.")

    digest = "\n".join(lines)
    st.session_state.last_digest = digest
    st.rerun()
