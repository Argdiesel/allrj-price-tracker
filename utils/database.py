"""
Local SQLite database for price history, trend analysis, and alerts.
SQLite = zero setup, zero cost, works locally and on Streamlit Cloud.
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "allrj_prices.db"


def get_conn():
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create all tables if they don't exist."""
    conn = get_conn()
    c = conn.cursor()

    # Price history — core table
    c.execute("""
        CREATE TABLE IF NOT EXISTS price_history (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            url         TEXT NOT NULL,
            brand       TEXT,
            category    TEXT,
            product     TEXT,
            price_raw   TEXT,
            price_num   REAL,
            method      TEXT,
            status      TEXT,
            scraped_at  TEXT NOT NULL
        )
    """)

    # Alerts — price change events
    c.execute("""
        CREATE TABLE IF NOT EXISTS price_alerts (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            url         TEXT NOT NULL,
            brand       TEXT,
            product     TEXT,
            old_price   REAL,
            new_price   REAL,
            change_pct  REAL,
            alert_type  TEXT,   -- 'sale', 'increase', 'decrease'
            detected_at TEXT NOT NULL,
            seen        INTEGER DEFAULT 0
        )
    """)

    # Tracked URL list (user's watchlist)
    c.execute("""
        CREATE TABLE IF NOT EXISTS watchlist (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            url         TEXT UNIQUE NOT NULL,
            brand       TEXT,
            category    TEXT,
            label       TEXT,
            added_at    TEXT NOT NULL,
            active      INTEGER DEFAULT 1
        )
    """)

    conn.commit()
    conn.close()


# ── PRICE HISTORY ─────────────────────────────────────────

def save_price(url, brand, category, product, price_raw, price_num, method, status):
    conn = get_conn()
    conn.execute("""
        INSERT INTO price_history
            (url, brand, category, product, price_raw, price_num, method, status, scraped_at)
        VALUES (?,?,?,?,?,?,?,?,?)
    """, (url, brand, category, product, price_raw, price_num, method, status,
          datetime.utcnow().isoformat()))
    conn.commit()

    # Check if this is a significant price change → generate alert
    _check_and_create_alert(conn, url, brand, product, price_num)
    conn.close()


def get_price_history(url=None, brand=None, days=30):
    conn = get_conn()
    since = (datetime.utcnow() - timedelta(days=days)).isoformat()
    if url:
        rows = conn.execute("""
            SELECT * FROM price_history
            WHERE url = ? AND scraped_at >= ?
            ORDER BY scraped_at DESC
        """, (url, since)).fetchall()
    elif brand:
        rows = conn.execute("""
            SELECT * FROM price_history
            WHERE brand = ? AND scraped_at >= ?
            ORDER BY scraped_at DESC
        """, (brand, since)).fetchall()
    else:
        rows = conn.execute("""
            SELECT * FROM price_history
            WHERE scraped_at >= ?
            ORDER BY scraped_at DESC
        """, (since,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_latest_price_per_url():
    """Get the most recent price for every tracked URL."""
    conn = get_conn()
    rows = conn.execute("""
        SELECT ph.*
        FROM price_history ph
        INNER JOIN (
            SELECT url, MAX(scraped_at) AS max_date
            FROM price_history
            GROUP BY url
        ) latest ON ph.url = latest.url AND ph.scraped_at = latest.max_date
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_price_trend(url, days=30):
    """Return list of {date, price} for sparkline charts."""
    conn = get_conn()
    since = (datetime.utcnow() - timedelta(days=days)).isoformat()
    rows = conn.execute("""
        SELECT DATE(scraped_at) as day, AVG(price_num) as avg_price
        FROM price_history
        WHERE url = ? AND price_num IS NOT NULL AND scraped_at >= ?
        GROUP BY DATE(scraped_at)
        ORDER BY day ASC
    """, (url, since)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_brand_price_trends(brand, days=30):
    """Return average daily price per brand for trend charts."""
    conn = get_conn()
    since = (datetime.utcnow() - timedelta(days=days)).isoformat()
    rows = conn.execute("""
        SELECT DATE(scraped_at) as day, brand, AVG(price_num) as avg_price
        FROM price_history
        WHERE brand = ? AND price_num IS NOT NULL AND scraped_at >= ?
        GROUP BY DATE(scraped_at), brand
        ORDER BY day ASC
    """, (brand, since)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_brand_trends(days=30):
    conn = get_conn()
    since = (datetime.utcnow() - timedelta(days=days)).isoformat()
    rows = conn.execute("""
        SELECT DATE(scraped_at) as day, brand, AVG(price_num) as avg_price, COUNT(*) as n
        FROM price_history
        WHERE price_num IS NOT NULL AND scraped_at >= ?
        GROUP BY DATE(scraped_at), brand
        ORDER BY day ASC
    """, (since,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── ALERTS ───────────────────────────────────────────────

def _check_and_create_alert(conn, url, brand, product, new_price):
    """Detect price changes > 5% and log as alerts."""
    if new_price is None:
        return
    prev = conn.execute("""
        SELECT price_num FROM price_history
        WHERE url = ? AND price_num IS NOT NULL
        ORDER BY scraped_at DESC
        LIMIT 1 OFFSET 1
    """, (url,)).fetchone()

    if not prev or prev['price_num'] is None:
        return

    old_price = prev['price_num']
    if old_price == 0:
        return

    change_pct = ((new_price - old_price) / old_price) * 100

    if abs(change_pct) >= 5:
        alert_type = 'sale' if change_pct <= -15 else ('decrease' if change_pct < 0 else 'increase')
        conn.execute("""
            INSERT INTO price_alerts
                (url, brand, product, old_price, new_price, change_pct, alert_type, detected_at)
            VALUES (?,?,?,?,?,?,?,?)
        """, (url, brand, product, old_price, new_price, change_pct,
              alert_type, datetime.utcnow().isoformat()))
        conn.commit()


def get_alerts(unseen_only=False, limit=50):
    conn = get_conn()
    if unseen_only:
        rows = conn.execute("""
            SELECT * FROM price_alerts WHERE seen = 0
            ORDER BY detected_at DESC LIMIT ?
        """, (limit,)).fetchall()
    else:
        rows = conn.execute("""
            SELECT * FROM price_alerts
            ORDER BY detected_at DESC LIMIT ?
        """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def mark_alerts_seen():
    conn = get_conn()
    conn.execute("UPDATE price_alerts SET seen = 1 WHERE seen = 0")
    conn.commit()
    conn.close()


def get_unseen_alert_count():
    conn = get_conn()
    n = conn.execute("SELECT COUNT(*) FROM price_alerts WHERE seen = 0").fetchone()[0]
    conn.close()
    return n


# ── WATCHLIST ─────────────────────────────────────────────

def add_to_watchlist(url, brand="", category="", label=""):
    conn = get_conn()
    try:
        conn.execute("""
            INSERT OR IGNORE INTO watchlist (url, brand, category, label, added_at)
            VALUES (?,?,?,?,?)
        """, (url, brand, category, label, datetime.utcnow().isoformat()))
        conn.commit()
    except Exception:
        pass
    conn.close()


def get_watchlist():
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM watchlist WHERE active = 1 ORDER BY brand, category"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def remove_from_watchlist(url):
    conn = get_conn()
    conn.execute("UPDATE watchlist SET active = 0 WHERE url = ?", (url,))
    conn.commit()
    conn.close()


# ── ANALYTICS ────────────────────────────────────────────

def get_summary_stats():
    conn = get_conn()
    total_scrapes  = conn.execute("SELECT COUNT(*) FROM price_history").fetchone()[0]
    brands_tracked = conn.execute("SELECT COUNT(DISTINCT brand) FROM price_history WHERE brand != ''").fetchone()[0]
    urls_tracked   = conn.execute("SELECT COUNT(DISTINCT url) FROM price_history").fetchone()[0]
    total_alerts   = conn.execute("SELECT COUNT(*) FROM price_alerts").fetchone()[0]
    unseen_alerts  = conn.execute("SELECT COUNT(*) FROM price_alerts WHERE seen=0").fetchone()[0]
    sales_detected = conn.execute("SELECT COUNT(*) FROM price_alerts WHERE alert_type='sale'").fetchone()[0]
    conn.close()
    return {
        "total_scrapes":  total_scrapes,
        "brands_tracked": brands_tracked,
        "urls_tracked":   urls_tracked,
        "total_alerts":   total_alerts,
        "unseen_alerts":  unseen_alerts,
        "sales_detected": sales_detected,
    }


def get_promo_detection():
    """
    Detect ongoing promos: products whose latest price is 15%+ below
    their 30-day average.
    """
    conn = get_conn()
    rows = conn.execute("""
        SELECT
            ph.brand,
            ph.product,
            ph.url,
            ph.price_num AS current_price,
            avg30.avg_price AS avg_30d,
            ROUND(((ph.price_num - avg30.avg_price) / avg30.avg_price) * 100, 1) AS pct_change
        FROM price_history ph
        INNER JOIN (
            SELECT url, MAX(scraped_at) AS max_date
            FROM price_history GROUP BY url
        ) latest ON ph.url = latest.url AND ph.scraped_at = latest.max_date
        INNER JOIN (
            SELECT url, AVG(price_num) AS avg_price
            FROM price_history
            WHERE scraped_at >= datetime('now', '-30 days')
              AND price_num IS NOT NULL
            GROUP BY url
            HAVING COUNT(*) >= 2
        ) avg30 ON ph.url = avg30.url
        WHERE ph.price_num IS NOT NULL
          AND ((ph.price_num - avg30.avg_price) / avg30.avg_price) * 100 <= -15
        ORDER BY pct_change ASC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# Init on import
init_db()
