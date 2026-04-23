"""Settings page."""
import streamlit as st

def render():
    st.markdown("""
    <div class="page-header">
        <div>
            <div class="page-title">SET<span>TINGS</span></div>
            <div class="page-sub">API keys · Scan schedule · Notifications</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🔑  API Keys", "⏱️  Scheduling", "📤  Export & Reset"])

    with tab1:
        st.markdown("### ScraperAPI")
        st.markdown("Required for JS-rendered sites (Under Armour, Nike, etc.) · [Get free key →](https://scraperapi.com)")
        key = st.text_input("ScraperAPI Key", type="password",
                            value=st.session_state.get('scraperapi_key',''),
                            placeholder="your_api_key_here")
        if key != st.session_state.get('scraperapi_key',''):
            st.session_state.scraperapi_key = key
            st.success("✅ Key saved for this session. Add to Streamlit Secrets for persistence.")

        st.markdown("---")
        st.markdown("### Anthropic API (for AI Digest)")
        st.markdown("The AI Digest uses the built-in Claude integration — no key needed when running on claude.ai. If self-hosting, add your key to Streamlit Secrets as `ANTHROPIC_API_KEY`.")
        st.code('# .streamlit/secrets.toml\nSCRAPERAPI_KEY = "your_scraperapi_key"\nANTHROPIC_API_KEY = "sk-ant-..."', language='toml')

    with tab2:
        st.markdown("### Automated Scanning")
        st.info("For automated daily scans, deploy to Streamlit Community Cloud and use a GitHub Action or cron job to hit the app endpoint, or run the scraper script independently.")

        st.markdown("**Quick-start: GitHub Actions cron**")
        st.code("""# .github/workflows/daily_scan.yml
name: Daily Price Scan
on:
  schedule:
    - cron: '0 8 * * *'   # Every day at 8am UTC
  workflow_dispatch:

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with: { python-version: '3.11' }
      - run: pip install -r requirements.txt
      - run: python run_daily_scan.py
        env:
          SCRAPERAPI_KEY: ${{ secrets.SCRAPERAPI_KEY }}
""", language='yaml')

        st.markdown("**run_daily_scan.py** (create this file):")
        st.code("""import os, sys
sys.path.insert(0, '.')
try:
    from utils.scraper import scrape_product
    from utils.database import save_price
    from data.competitors import get_all_competitor_urls
except Exception:
    pass

key = os.getenv('SCRAPERAPI_KEY', '')
for row in get_all_competitor_urls():
    r = scrape_product(row['url'], row['brand'], row['category'], key)
    save_price(row['url'], r['brand'], r['category'], r['product'],
               r['price_raw'], r['price_num'], r['method'], r['status'])
    print(f"{r['brand']} {r['price_raw']}")
""", language='python')

    with tab3:
        st.markdown("### Export All Data")
        try:
            from utils.database import get_price_history, get_alerts
            import pandas as pd

            col1, col2 = st.columns(2)
            with col1:
                history = get_price_history(days=365)
                if history:
                    df = pd.DataFrame(history)
                    st.download_button("📥 Export Full Price History",
                                       df.to_csv(index=False).encode(),
                                       "allrj_full_history.csv", "text/csv")
                else:
                    st.info("No history to export yet.")

            with col2:
                alerts = get_alerts(limit=1000)
                if alerts:
                    df = pd.DataFrame(alerts)
                    st.download_button("📥 Export All Alerts",
                                       df.to_csv(index=False).encode(),
                                       "allrj_all_alerts.csv", "text/csv")
                else:
                    st.info("No alerts to export yet.")

        except Exception as e:
            st.error(f"DB error: {e}")

        st.markdown("---")
        st.markdown("### Reset Database")
        st.warning("⚠️ This will delete ALL price history, alerts, and watchlist data. This cannot be undone.")
        confirm = st.text_input("Type RESET to confirm")
        if st.button("🗑️ Delete All Data", type="secondary"):
            if confirm == "RESET":
                try:
                    import sqlite3
                    from pathlib import Path
                    db_path = Path(__file__).parent.parent / "allrj_prices.db"
                    if db_path.exists():
                        db_path.unlink()
                    st.success("Database cleared. Refresh the page.")
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.error("Type RESET to confirm deletion.")
