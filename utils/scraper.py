"""
3-layer scraping engine:
  1. Shopify JSON   — instant, no bot detection
  2. ScraperAPI     — JS-rendered sites (free tier 1k/mo)
  3. Smart HTML     — JSON-LD → OG → CSS selectors → regex
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import time
from urllib.parse import urlparse


HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/122.0.0.0 Safari/537.36'
    ),
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

BRAND_DOMAINS = {
    'gymshark': 'Gymshark', 'underarmour': 'Under Armour',
    'nike': 'Nike', 'adidas': 'Adidas', 'lululemon': 'Lululemon',
    'alphalete': 'Alphalete', 'aybl': 'AYBL', 'gymking': 'Gym King',
    'vuori': 'Vuori', 'puma': 'Puma', 'reebok': 'Reebok',
    'newbalance': 'New Balance', 'allbirds': 'Allbirds',
}


def detect_brand(url):
    domain = urlparse(url).netloc.lower()
    for key, name in BRAND_DOMAINS.items():
        if key in domain:
            return name
    return domain.replace('www.', '').split('.')[0].title()


def try_shopify_json(url):
    try:
        parsed = urlparse(url)
        path = parsed.path.rstrip('/').split('?')[0]
        json_url = f"{parsed.scheme}://{parsed.netloc}{path}.json"
        resp = requests.get(json_url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            product = data.get('product', {})
            variants = product.get('variants', [])
            if variants:
                prices = [float(v['price']) for v in variants if v.get('available', True)]
                if not prices:
                    prices = [float(v['price']) for v in variants]
                price = min(prices)
                return {
                    'title': product.get('title', 'Unknown'),
                    'price_raw': f"${price:.2f}",
                    'price_num': price,
                    'method': 'Shopify JSON',
                    'method_class': 'method-json',
                }
    except Exception:
        pass
    return None


def try_scraperapi(url, api_key):
    try:
        api_url = f"http://api.scraperapi.com?api_key={api_key}&url={url}&render=true"
        resp = requests.get(api_url, timeout=35)
        if resp.status_code == 200:
            price_num, price_raw = extract_price(resp.text)
            if price_num:
                return {
                    'title': extract_title(resp.text),
                    'price_raw': price_raw,
                    'price_num': price_num,
                    'method': 'ScraperAPI',
                    'method_class': 'method-api',
                }
    except Exception:
        pass
    return None


def try_direct(url, retries = 2):
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=13)
            if resp.status_code == 200:
                price_num, price_raw = extract_price(resp.text)
                if price_num:
                    return {
                        'title': extract_title(resp.text),
                        'price_raw': price_raw,
                        'price_num': price_num,
                        'method': 'HTML Scrape',
                        'method_class': 'method-html',
                    }
            elif resp.status_code == 429 and attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
        except Exception:
            if attempt < retries - 1:
                time.sleep(1)
    return None


def extract_price(html):
    """Returns (float, '$XX.XX') or (None, None)."""
    soup = BeautifulSoup(html, 'html.parser')

    # 1. JSON-LD structured data
    for script in soup.find_all('script', type='application/ld+json'):
        try:
            data = json.loads(script.string or '')
            items = data if isinstance(data, list) else [data]
            for item in items:
                offers = item.get('offers') or item.get('Offers')
                if offers:
                    if isinstance(offers, list):
                        offers = offers[0]
                    p = offers.get('price') or offers.get('lowPrice')
                    if p:
                        n = float(str(p).replace(',', ''))
                        return n, f"${n:.2f}"
        except Exception:
            continue

    # 2. Open Graph
    og = soup.find('meta', property='product:price:amount')
    if og and og.get('content'):
        try:
            n = float(og['content'])
            return n, f"${n:.2f}"
        except Exception:
            pass

    # 3. Semantic selectors
    for sel in ['[itemprop="price"]', '[class*="price"]', '[class*="Price"]',
                '[data-price]', '[class*="amount"]', '.product-price', '#price']:
        for tag in soup.select(sel):
            text = tag.get_text(strip=True)
            m = re.search(r'\$\s*(\d{1,4}(?:[.,]\d{2,3})*)', text)
            if m:
                n = float(m.group(1).replace(',', ''))
                if 0.99 < n < 9999:
                    return n, f"${n:.2f}"

    # 4. Keyword-anchored regex
    text = soup.get_text()
    m = re.search(r'(?:price|buy|USD|cost)[^\$\d]{0,30}\$\s*(\d{1,4}(?:\.\d{2})?)',
                  text, re.IGNORECASE)
    if m:
        n = float(m.group(1))
        if 0.99 < n < 9999:
            return n, f"${n:.2f}"

    # 5. Last resort
    m = re.search(r'\$\s*(\d{1,4}(?:\.\d{2})?)', text)
    if m:
        n = float(m.group(1))
        if 0.99 < n < 9999:
            return n, f"${n:.2f}"

    return None, None


def extract_title(html):
    soup = BeautifulSoup(html, 'html.parser')
    og = soup.find('meta', property='og:title')
    if og and og.get('content'):
        return og['content'].strip()[:100]
    for script in soup.find_all('script', type='application/ld+json'):
        try:
            data = json.loads(script.string or '')
            items = data if isinstance(data, list) else [data]
            for item in items:
                if item.get('name'):
                    return item['name'][:100]
        except Exception:
            continue
    title = soup.find('title')
    if title:
        return title.get_text(strip=True)[:80]
    return 'Unknown Product'


def scrape_product(url, brand = '', category = '',
                   scraperapi_key = ''):
    brand = brand or detect_brand(url)
    result = {
        'brand': brand, 'category': category, 'url': url,
        'product': 'Unknown', 'price_raw': 'Not found',
        'price_num': None, 'method': '—', 'method_class': '',
        'status': '❌',
    }

    for strategy in [
        lambda: try_shopify_json(url),
        lambda: try_scraperapi(url, scraperapi_key) if scraperapi_key.strip() else None,
        lambda: try_direct(url),
    ]:
        data = strategy()
        if data:
            result.update({
                'product':    data['title'],
                'price_raw':  data['price_raw'],
                'price_num':  data['price_num'],
                'method':     data['method'],
                'method_class': data['method_class'],
                'status':     '✅',
            })
            break

    return result
