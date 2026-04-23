"""
ALLRJ Price Intelligence Platform v2.0
Main entry — handles routing + global styles
"""

import streamlit as st
from auth import check_auth, render_login, logout

st.set_page_config(
    page_title="ALLRJ · Price Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Force sidebar open state
if "sidebar_open" not in st.session_state:
    st.session_state.sidebar_open = True

# ── AUTH GATE ──────────────────────────────────────────────
try:
    if not check_auth():
        render_login()
        st.stop()
except Exception:
    # If secrets not configured yet, bypass auth
    pass

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&family=Sora:wght@600;700;800&display=swap');

:root {
    --accent:      #6366F1;
    --accent-lt:   #A5B4FC;
    --accent-dim:  rgba(99,102,241,0.12);
    --accent2:     #EC4899;
    --bg:          #0A0C12;
    --bg2:         #0F1117;
    --surface:     #161926;
    --surface2:    #1E2235;
    --border:      #252840;
    --border2:     #323654;
    --text:        #F1F5F9;
    --text2:       #A8B8CC;
    --muted:       #5A6A80;
    --green:       #34D399;
    --green-dim:   rgba(52,211,153,0.1);
    --red:         #F87171;
    --red-dim:     rgba(248,113,113,0.1);
    --yellow:      #FBBF24;
    --yellow-dim:  rgba(251,191,36,0.1);
    --blue:        #60A5FA;
    --blue-dim:    rgba(96,165,250,0.1);
    --pink-dim:    rgba(236,72,153,0.1);
    --font-head:   'Sora', sans-serif;
    --font-body:   'Inter', sans-serif;
    --font-mono:   'JetBrains Mono', monospace;
    --radius:      10px;
    --radius-lg:   14px;
    --shadow:      0 4px 24px rgba(0,0,0,0.4);
}

/* ── RESET ── */
html, body, [class*="css"] {
    font-family: var(--font-body) !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-size: 15px !important;
    -webkit-font-smoothing: antialiased !important;
}
* { box-sizing: border-box; }

/* ── FORCE DARK ON ALL CONTAINERS ── */
.main, .main > div, [data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
[data-testid="block-container"],
.stApp, .stApp > div {
    background-color: var(--bg) !important;
}
[data-testid="stVerticalBlock"] {
    background-color: transparent !important;
}

/* ── SIDEBAR TOGGLE — always visible ── */
[data-testid="collapsedControl"],
[data-testid="collapsedControl"] > button,
button[aria-label="Close sidebar"],
button[aria-label="Open sidebar"],
[data-testid="baseButton-headerNoPadding"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    z-index: 9999 !important;
    position: relative !important;
}
[data-testid="collapsedControl"]:hover {
    background: var(--surface2) !important;
    border-color: var(--accent) !important;
}
/* Never hide the sidebar toggle */
[data-testid="stSidebarCollapsedControl"] {
    display: flex !important;
    visibility: visible !important;
}

/* ── MOBILE RESPONSIVE ── */
@media (max-width: 768px) {
    .block-container { padding: 0 1rem 3rem !important; }
    .top-bar { padding: 10px 16px; margin: -0rem -1rem 1rem -1rem; }
    .metric-grid { grid-template-columns: repeat(2, 1fr) !important; }
    .page-title { font-size: 1.4rem !important; }
    [data-testid="collapsedControl"] { display: flex !important; }
    .mobile-hint { display: inline !important; }
    .data-row { flex-direction: column; align-items: flex-start !important; }
    .price-display { text-align: left !important; }
}

/* ── HIDE STREAMLIT CHROME ── */
[data-testid="stSidebarNav"] { display: none !important; }
[data-testid="stHeader"] { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
[data-testid="stStatusWidget"] { display: none !important; }
.stDeployButton { display: none !important; }
#MainMenu { display: none !important; }
footer { display: none !important; }
header { display: none !important; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--muted); }

/* ── STICKY TOP BAR ── */
.top-bar {
    position: sticky;
    top: 0;
    z-index: 999;
    background: rgba(15,17,23,0.92);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-bottom: 1px solid var(--border);
    padding: 12px 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: -3rem -2rem 1.5rem -2rem;
}
.top-bar-left {
    display: flex;
    align-items: center;
    gap: 10px;
}
.top-bar-logo {
    font-family: var(--font-head);
    font-size: 1.1rem;
    font-weight: 800;
    color: var(--text);
    letter-spacing: -0.5px;
}
.top-bar-logo span { color: var(--accent-lt); }
.top-bar-divider {
    width: 1px;
    height: 18px;
    background: var(--border2);
}
.top-bar-page {
    font-size: 0.82rem;
    font-weight: 500;
    color: var(--text2);
    letter-spacing: 0.2px;
}
.top-bar-badge {
    font-size: 0.65rem;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 20px;
    background: var(--accent-dim);
    color: var(--accent-lt);
    border: 1px solid rgba(99,102,241,0.25);
}

/* ── BLOCK CONTAINER ── */
.block-container { padding: 0rem 2rem 4rem !important; max-width: 1400px; }

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
    background: var(--bg2) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] .block-container {
    padding: 1.5rem 1rem !important;
}
.sb-logo {
    font-family: var(--font-head);
    font-size: 1.25rem;
    font-weight: 800;
    color: var(--text);
    letter-spacing: -0.5px;
}
.sb-logo span { color: var(--accent-lt); }
.sb-tagline {
    font-size: 0.65rem;
    color: var(--muted);
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-top: 3px;
}
.sb-version {
    display: inline-block;
    font-size: 0.6rem;
    font-family: var(--font-mono);
    color: var(--muted);
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 1px 6px;
    margin-top: 6px;
}

/* ── PAGE HEADER ── */
.page-header {
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    padding-top: 1.5rem;
    border-bottom: 1px solid var(--border);
}
.page-title {
    font-family: var(--font-head);
    font-size: 1.9rem;
    font-weight: 800;
    color: var(--text);
    letter-spacing: -0.5px;
    line-height: 1.2;
}
.page-title span { color: var(--accent-lt); }
.page-sub {
    font-size: 0.84rem;
    color: var(--text2);
    margin-top: 6px;
    font-weight: 400;
    line-height: 1.5;
}

/* ── METRIC GRID ── */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 12px;
    margin-bottom: 1.5rem;
}
.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 18px 20px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s, transform 0.15s;
}
.metric-card:hover { border-color: var(--accent); transform: translateY(-2px); }
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    background: var(--accent);
    border-radius: var(--radius-lg) var(--radius-lg) 0 0;
}
.metric-card.green::before  { background: var(--green); }
.metric-card.alert::before  { background: var(--accent2); }
.metric-card.yellow::before { background: var(--yellow); }
.metric-icon {
    font-size: 1.1rem;
    margin-bottom: 8px;
    display: block;
}
.metric-val {
    font-family: var(--font-head);
    font-size: 2rem;
    font-weight: 700;
    color: var(--text);
    letter-spacing: -1px;
    line-height: 1;
    margin-top: 4px;
}
.metric-card.green  .metric-val { color: var(--green); }
.metric-card.alert  .metric-val { color: var(--accent2); }
.metric-card.yellow .metric-val { color: var(--yellow); }
.metric-lbl {
    font-size: 0.72rem;
    color: var(--text2);
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-top: 5px;
    font-weight: 500;
}

/* ── BADGES ── */
.badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 0.62rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    padding: 2px 8px;
    border-radius: 20px;
}
.badge-brand  { background: var(--accent-dim);  color: var(--accent-lt); border: 1px solid rgba(99,102,241,0.25); }
.badge-json   { background: var(--green-dim);   color: var(--green);     border: 1px solid rgba(16,185,129,0.25); }
.badge-api    { background: var(--blue-dim);    color: var(--blue);      border: 1px solid rgba(59,130,246,0.25); }
.badge-html   { background: var(--yellow-dim);  color: var(--yellow);    border: 1px solid rgba(245,158,11,0.25); }
.badge-sale   { background: var(--pink-dim);    color: var(--accent2);   border: 1px solid rgba(236,72,153,0.3); animation: pulse 2s infinite; }
.badge-up     { background: var(--red-dim);     color: var(--red);       border: 1px solid rgba(239,68,68,0.25); }
.badge-down   { background: var(--green-dim);   color: var(--green);     border: 1px solid rgba(16,185,129,0.25); }
.badge-dtc    { background: var(--blue-dim);    color: #93C5FD;          border: 1px solid rgba(59,130,246,0.2); }
.badge-major  { background: var(--surface2);    color: var(--text2);     border: 1px solid var(--border2); }

@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.55} }

/* ── DATA ROWS ── */
.data-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 14px 18px;
    margin-bottom: 8px;
    transition: border-color 0.15s, background 0.15s;
    gap: 12px;
}
.data-row:hover { border-color: var(--border2); background: var(--surface2); }
.data-row.sale-row { border-color: rgba(236,72,153,0.3); background: rgba(236,72,153,0.03); }

.product-name {
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--text);
    margin: 4px 0 2px;
    line-height: 1.5;
}
.url-chip {
    font-family: var(--font-mono);
    font-size: 0.68rem;
    color: var(--text2);
    max-width: 340px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    opacity: 0.7;
}
.price-display {
    font-family: var(--font-head);
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--text);
    text-align: right;
    letter-spacing: -0.5px;
}
.price-display.sale  { color: var(--accent2); }
.price-display.error { color: var(--red); font-family: var(--font-body); font-size: 0.75rem; font-weight: 400; }
.price-change {
    font-family: var(--font-mono);
    font-size: 0.68rem;
    text-align: right;
    margin-top: 2px;
}
.price-change.up   { color: var(--red); }
.price-change.down { color: var(--green); }

/* ── SECTION HEADERS ── */
.section-header {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    color: var(--text2);
    margin: 1.5rem 0 0.9rem;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-header::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
}

/* ── BUTTONS ── */
.stButton > button {
    background: var(--accent) !important;
    color: #fff !important;
    font-family: var(--font-body) !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.2px !important;
    border: none !important;
    border-radius: var(--radius) !important;
    padding: 10px 20px !important;
    transition: all 0.15s !important;
    width: 100% !important;
    box-shadow: 0 2px 8px rgba(99,102,241,0.25) !important;
}
.stButton > button:hover {
    opacity: 0.9 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(99,102,241,0.4) !important;
}
.stButton > button[kind="secondary"] {
    background: var(--surface) !important;
    color: var(--text2) !important;
    border: 1px solid var(--border2) !important;
    box-shadow: none !important;
}

/* ── INPUTS ── */
.stTextInput input, .stTextArea textarea {
    background: var(--surface2) !important;
    border: 1px solid var(--border2) !important;
    color: var(--text) !important;
    border-radius: var(--radius) !important;
    font-family: var(--font-body) !important;
    font-size: 0.84rem !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px var(--accent-dim) !important;
}
div[data-baseweb="select"] > div {
    background: var(--surface2) !important;
    border-color: var(--border2) !important;
    border-radius: var(--radius) !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface) !important;
    border-radius: var(--radius) !important;
    border: 1px solid var(--border) !important;
    gap: 2px;
    padding: 3px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text2) !important;
    border-radius: 7px !important;
    font-family: var(--font-body) !important;
    font-weight: 500 !important;
    font-size: 0.82rem !important;
}
.stTabs [aria-selected="true"] {
    background: var(--accent-dim) !important;
    color: var(--accent-lt) !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.3) !important;
    border-bottom: 2px solid var(--accent) !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 1rem !important; }

/* ── MISC ── */
.stAlert { border-radius: var(--radius) !important; }
hr { border-color: var(--border) !important; margin: 1.25rem 0 !important; }
.stProgress > div > div { background: var(--accent) !important; border-radius: 4px !important; }
.stProgress > div { background: var(--border) !important; border-radius: 4px !important; }
.stDataFrame { border: 1px solid var(--border) !important; border-radius: var(--radius) !important; overflow: hidden; }
[data-testid="stDataFrame"] { background: var(--surface) !important; }
[data-testid="stDataFrame"] td, [data-testid="stDataFrame"] th {
    background: var(--surface) !important;
    color: var(--text) !important;
    border-color: var(--border) !important;
}

/* ── EMPTY STATE ── */
.empty-state {
    background: var(--surface);
    border: 1px dashed var(--border2);
    border-radius: var(--radius-lg);
    padding: 48px 32px;
    text-align: center;
}
.empty-icon  { font-size: 2.2rem; margin-bottom: 10px; }
.empty-title { font-family: var(--font-head); font-size: 1.1rem; font-weight: 700; color: var(--text2); }
.empty-sub   { font-size: 0.78rem; color: var(--muted); margin-top: 6px; line-height: 1.6; }

/* ── NAV BUTTON OVERRIDE ── */
.stButton > button[data-testid*="nav_"] {
    background: transparent !important;
    color: var(--text2) !important;
    border: none !important;
    text-align: left !important;
    justify-content: flex-start !important;
    padding: 9px 14px !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    border-radius: 8px !important;
    letter-spacing: 0.1px !important;
}
.stButton > button[data-testid*="nav_"]:hover {
    background: var(--surface) !important;
    color: var(--text) !important;
    transform: none !important;
    border-left: 2px solid var(--accent) !important;
}
</style>
""", unsafe_allow_html=True)


# ── SESSION STATE ───────────────────────────────────────────────────────────
if 'page' not in st.session_state:
    st.session_state.page = 'dashboard'
if 'scraperapi_key' not in st.session_state:
    st.session_state.scraperapi_key = ''
if 'last_scan_results' not in st.session_state:
    st.session_state.last_scan_results = []

PAGE_LABELS = {
    'dashboard':   'Dashboard',
    'tracker':     'Track Prices',
    'history':     'Price History',
    'competitors': 'Competitors',
    'comparison':  'Brand Comparison',
    'strategy':    'Pricing Strategy',
    'alerts':      'Alerts',
    'digest':      'AI Digest',
    'settings':    'Settings',
}

# ── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sb-logo">ALL<span>RJ</span></div>
    <div class="sb-tagline">Price Intelligence</div>
    <div class="sb-version">v2.0</div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    pages = [
        ("dashboard",   "📊", "Dashboard"),
        ("tracker",     "🔍", "Track Prices"),
        ("history",     "📈", "Price History"),
        ("competitors", "🏷️",  "Competitors"),
        ("comparison",  "⚖️",  "Brand Comparison"),
        ("strategy",    "🧠", "Pricing Strategy"),
        ("alerts",      "🔔", "Alerts"),
        ("digest",      "🤖", "AI Digest"),
        ("settings",    "⚙️",  "Settings"),
    ]

    for key, icon, label in pages:
        is_active = st.session_state.page == key
        btn_label = f"{'●  ' if is_active else '○  '}{icon}  {label}"
        if st.button(btn_label, key=f"nav_{key}", use_container_width=True):
            st.session_state.page = key
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<div style="font-size:0.68rem;color:var(--muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;font-weight:600;">ScraperAPI Key</div>', unsafe_allow_html=True)
    key_input = st.text_input("api_key_sb", label_visibility="collapsed",
                               type="password",
                               value=st.session_state.scraperapi_key,
                               placeholder="Paste key for JS sites")
    if key_input != st.session_state.scraperapi_key:
        st.session_state.scraperapi_key = key_input
    st.markdown('<div style="font-size:0.62rem;color:var(--muted);margin-top:4px;">Free: 1,000 req/mo · scraperapi.com</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    # Customer info
    customer = st.session_state.get("customer_name", "")
    if customer:
        st.markdown(f'<div style="font-size:0.68rem;color:var(--muted);text-align:center;margin-bottom:6px;">Logged in as {customer}</div>', unsafe_allow_html=True)
    if st.button("Sign Out", key="logout_btn"):
        logout()
    st.markdown('<div style="font-size:0.6rem;color:var(--muted);text-align:center;margin-top:8px;">Built for ALLRJ 💪</div>', unsafe_allow_html=True)


# ── STICKY TOP BAR ──────────────────────────────────────────────────────────
current_page = st.session_state.page
page_label = PAGE_LABELS.get(current_page, '')

try:
    from utils.database import get_unseen_alert_count
    unseen = get_unseen_alert_count()
except Exception:
    unseen = 0

alert_badge = f'<span class="top-bar-badge">🔔 {unseen} new</span>' if unseen > 0 else ''

st.markdown(f"""
<div class="top-bar">
  <div class="top-bar-left">
    <div class="top-bar-logo">ALL<span>RJ</span></div>
    <div class="top-bar-divider"></div>
    <div class="top-bar-page">{page_label}</div>
  </div>
  <div style="display:flex;align-items:center;gap:8px;">
    {alert_badge}
  </div>
</div>
""", unsafe_allow_html=True)


# ── PAGE ROUTING ─────────────────────────────────────────────────────────────
page = st.session_state.page

if page == 'dashboard':
    from pages import dashboard; dashboard.render()
elif page == 'tracker':
    from pages import tracker; tracker.render()
elif page == 'history':
    from pages import history; history.render()
elif page == 'competitors':
    from pages import competitors_page; competitors_page.render()
elif page == 'alerts':
    from pages import alerts; alerts.render()
elif page == 'digest':
    from pages import digest; digest.render()
elif page == 'comparison':
    from pages import comparison; comparison.render()
elif page == 'strategy':
    from pages import strategy; strategy.render()
elif page == 'settings':
    from pages import settings; settings.render()
