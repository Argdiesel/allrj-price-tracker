# ⚡ ALLRJ Price Intelligence Platform v2.0

Full-stack competitor price tracking for DTC activewear brands.

---

## 🚀 Run in 60 Seconds

```bash
pip install -r requirements.txt
streamlit run app.py
```
Open http://localhost:8501

---

## 📁 Project Structure

```
allrj_v2/
├── app.py                    ← Entry point + navigation + global CSS
├── requirements.txt
├── allrj_prices.db           ← Auto-created SQLite database
│
├── pages/
│   ├── dashboard.py          ← Command center (metrics, promos, alerts)
│   ├── tracker.py            ← Manual scan + competitor library + batch
│   ├── history.py            ← Trend charts + product deep dive
│   ├── competitors_page.py   ← Brand library browser
│   ├── alerts.py             ← Price change notifications
│   ├── digest.py             ← AI-generated weekly brief (Claude)
│   └── settings.py           ← API keys + scheduling + export
│
├── utils/
│   ├── scraper.py            ← 3-layer scraping engine
│   └── database.py           ← SQLite: history, alerts, watchlist
│
└── data/
    └── competitors.py        ← Pre-seeded brand library (9 brands)
```

---

## 🌐 Deploy Free (Streamlit Community Cloud)

1. Push to a public GitHub repo
2. Go to [share.streamlit.io](https://share.streamlit.io) → New App
3. Set main file: `app.py`
4. Add secrets (Settings → Secrets):
```toml
SCRAPERAPI_KEY = "your_scraperapi_key"
```
5. Deploy — live in ~60 seconds ✅

**That's it. Free forever on Community Cloud.**

---

## 💰 GO-TO-MARKET: How to Sell This

### Who to sell to
- DTC activewear brands doing £100K–£5M/year revenue
- They compete directly with Gymshark/UA/Lululemon
- They have no pricing intelligence today — they check competitor sites manually
- Budget decision: founder or head of ecom makes it in <5 min

### Where to find them
1. **Shopify ecosystem** — List on Shopify App Store (free to list, massive distribution)
2. **Twitter/X DTC community** — #DTCTwitter, follow/engage with DTC founders
3. **Sweat Equity Podcast community** — Ben Francis/fitness brand founders
4. **LinkedIn** — "Head of Ecommerce" + "activewear" / "sportswear"
5. **Reddit** — r/ecommerce, r/entrepreneur
6. **Cold email** — scrape Shopify activewear brands from BuiltWith.com

### Pricing
| Tier       | Price    | Limits                          |
|------------|----------|---------------------------------|
| Starter    | $29/mo   | 5 competitors, weekly scan      |
| Growth     | $79/mo   | 20 competitors, daily scan      |
| Pro        | $149/mo  | Unlimited, hourly, Slack alerts |
| Agency     | $299/mo  | Multi-brand, white-label        |

**Start at $29. Raise prices as you add features.**

### Your pitch (one sentence)
*"Know what Gymshark is charging before your customers do — and never lose a sale on price again."*

### Differentiation vs generic tools
- ✅ Pre-built activewear competitor library (zero setup)
- ✅ Promo/sale detection with 30d context
- ✅ AI weekly digest (nobody else does this at this price point)
- ✅ Built for DTC brands, not enterprise retailers
- ✅ 5-minute setup vs days for enterprise tools
- ✅ $29/mo vs $99–$500/mo for Prisync/Omnia

---

## ⚙️ Automated Daily Scans (Free with GitHub Actions)

Create `.github/workflows/daily_scan.yml` in your repo:

```yaml
name: Daily Price Scan
on:
  schedule:
    - cron: '0 8 * * *'
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
```

Create `run_daily_scan.py`:
```python
import os, sys
sys.path.insert(0, '.')
from utils.scraper import scrape_product
from utils.database import save_price
from data.competitors import get_all_competitor_urls

key = os.getenv('SCRAPERAPI_KEY', '')
for row in get_all_competitor_urls():
    r = scrape_product(row['url'], row['brand'], row['category'], key)
    save_price(row['url'], r['brand'], r['category'], r['product'],
               r['price_raw'], r['price_num'], r['method'], r['status'])
    print(f"{r['brand']} · {r['category']} · {r['price_raw']}")
```

---

## 🔑 ScraperAPI Setup

1. Sign up free at [scraperapi.com](https://scraperapi.com) — 1,000 req/month free
2. Get your API key from the dashboard
3. Add it to Streamlit Secrets or paste in the Settings page

---

Built for ALLRJ 💪 | [allrj.com](https://allrj.com)
