from __future__ import annotations
"""
ALLRJ Authentication — Token-based access control.
Each paying customer gets a unique token.
Tokens are stored in Streamlit Secrets.
Revoke access by removing a token from secrets.
"""
import streamlit as st
import hashlib
import time


def get_valid_tokens():
    """
    Load valid tokens from Streamlit Secrets.
    Add tokens in your Streamlit dashboard under Secrets:
    
    [tokens]
    customer1 = "tok_abc123"
    customer2 = "tok_xyz789"
    """
    try:
        tokens = dict(st.secrets.get("tokens", {}))
        # Also check for a master password
        master = st.secrets.get("master_password", "")
        return tokens, master
    except Exception:
        return {}, ""


def hash_token(token: str) -> str:
    return hashlib.sha256(token.strip().encode()).hexdigest()


def check_auth() -> bool:
    """
    Returns True if user is authenticated.
    Call this at the top of app.py before rendering anything.
    """
    # Already authenticated this session
    if st.session_state.get("authenticated"):
        return True

    # Check if token stored in session
    stored = st.session_state.get("access_token", "")
    if stored:
        tokens, master = get_valid_tokens()
        valid_hashes = [hash_token(t) for t in tokens.values()]
        if master:
            valid_hashes.append(hash_token(master))
        if hash_token(stored) in valid_hashes:
            st.session_state.authenticated = True
            return True

    return False


def render_login():
    """Render the login gate UI."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Sora:wght@700;800&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
        background-color: #0A0C12 !important;
        color: #F1F5F9 !important;
    }
    .main, .stApp, [data-testid="stAppViewContainer"] {
        background-color: #0A0C12 !important;
    }
    [data-testid="stHeader"]       { display: none !important; }
    [data-testid="stToolbar"]      { display: none !important; }
    [data-testid="stDecoration"]   { display: none !important; }
    .stDeployButton                { display: none !important; }
    #MainMenu                      { display: none !important; }
    footer                         { display: none !important; }
    header                         { display: none !important; }
    .block-container {
        max-width: 420px !important;
        margin: 0 auto !important;
        padding: 4rem 1.5rem !important;
    }
    .stTextInput input {
        background: #161926 !important;
        border: 1px solid #252840 !important;
        border-radius: 10px !important;
        color: #F1F5F9 !important;
        font-size: 0.95rem !important;
        padding: 12px 16px !important;
    }
    .stTextInput input:focus {
        border-color: #6366F1 !important;
        box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
    }
    .stButton > button {
        background: #6366F1 !important;
        color: #fff !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 24px !important;
        width: 100% !important;
        box-shadow: 0 2px 12px rgba(99,102,241,0.3) !important;
    }
    .stButton > button:hover { opacity: 0.9 !important; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;margin-bottom:2rem;">
      <div style="font-family:'Sora',sans-serif;font-size:1.8rem;font-weight:800;
                  color:#F1F5F9;letter-spacing:-0.5px;margin-bottom:6px;">
        ALL<span style="color:#A5B4FC;">RJ</span>
      </div>
      <div style="font-size:0.82rem;color:#5A6A80;text-transform:uppercase;
                  letter-spacing:1.5px;">Price Intelligence</div>
    </div>

    <div style="background:#161926;border:1px solid #252840;border-radius:14px;
                padding:28px 24px;margin-bottom:1.5rem;">
      <div style="font-size:1.1rem;font-weight:700;color:#F1F5F9;
                  margin-bottom:6px;">Welcome back</div>
      <div style="font-size:0.84rem;color:#A8B8CC;margin-bottom:20px;line-height:1.6;">
        Enter your access token to continue. Don't have one?
        <a href="https://allrj-demo.streamlit.app" target="_blank"
           style="color:#A5B4FC;text-decoration:none;">Start your free trial →</a>
      </div>
    </div>
    """, unsafe_allow_html=True)

    token_input = st.text_input(
        "Access token",
        type="password",
        placeholder="tok_xxxxxxxxxxxxxxxx",
        label_visibility="collapsed",
    )

    if st.button("Access Platform", type="primary"):
        if token_input.strip():
            tokens, master = get_valid_tokens()
            valid_hashes = [hash_token(t) for t in tokens.values()]
            if master:
                valid_hashes.append(hash_token(master))

            if hash_token(token_input.strip()) in valid_hashes:
                st.session_state.authenticated = True
                st.session_state.access_token = token_input.strip()
                # Find which customer this token belongs to
                for name, tok in tokens.items():
                    if hash_token(tok) == hash_token(token_input.strip()):
                        st.session_state.customer_name = name
                        break
                st.rerun()
            else:
                st.markdown("""
                <div style="background:rgba(248,113,113,0.08);border:1px solid rgba(248,113,113,0.2);
                            border-radius:8px;padding:12px 16px;margin-top:8px;
                            font-size:0.84rem;color:#F87171;">
                  Invalid token. Check your email or
                  <a href="https://allrj-demo.streamlit.app" target="_blank"
                     style="color:#F87171;">start a free trial</a>.
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("Please enter your access token.")

    st.markdown("""
    <div style="text-align:center;margin-top:1.5rem;">
      <div style="font-size:0.72rem;color:#3A4A60;line-height:1.8;">
        No account yet? Try the free demo at<br>
        <a href="https://allrj-demo.streamlit.app" target="_blank"
           style="color:#6366F1;text-decoration:none;">allrj-demo.streamlit.app</a>
      </div>
    </div>
    """, unsafe_allow_html=True)


def generate_token(customer_name: str) -> str:
    """Generate a unique token for a new customer."""
    import secrets
    token = f"tok_{secrets.token_urlsafe(16)}"
    print(f"\nNew token for {customer_name}:")
    print(f"  {token}")
    print(f"\nAdd to Streamlit Secrets:")
    print(f'  [tokens]')
    print(f'  {customer_name.lower().replace(" ","_")} = "{token}"')
    return token


def logout():
    """Clear authentication state."""
    st.session_state.authenticated = False
    st.session_state.access_token = ""
    st.session_state.customer_name = ""
    st.rerun()
