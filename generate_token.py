"""
Run this script to generate a token for a new customer.
Usage: python3 generate_token.py "Customer Name"
"""
import secrets
import sys

def generate(name):
    token = f"tok_{secrets.token_urlsafe(16)}"
    print(f"\n✅ Token generated for: {name}")
    print(f"\n   Token: {token}")
    print(f"\n   Add this to Streamlit Secrets (share.streamlit.io → Settings → Secrets):")
    print(f"\n   [tokens]")
    print(f'   {name.lower().replace(" ","_")} = "{token}"')
    print(f"\n   Then email the customer their token: {token}")
    print(f"\n   They enter it at: https://allrj-price-tracker.streamlit.app")

if __name__ == "__main__":
    name = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "customer"
    generate(name)
