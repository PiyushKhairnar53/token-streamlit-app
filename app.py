import streamlit as st
import msal
 
# -----------------------------
# 🔐 Configuration (replace with your actual values)
# -----------------------------
CLIENT_ID = "97daf6d6-e5a7-47ba-8127-567b290c4df5"
CLIENT_SECRET = "RpO8Q~2fvSvffhwTUNNYdzyzqTsf6h_jmw4CeabO"
TENANT_ID = "5d41fd7c-b291-4130-ac2b-9170e1c4c03e"
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
REDIRECT_URI = "http://localhost:8501"
SCOPE = ["https://orgb0732c8b.crm8.dynamics.com/.default"]
 
# -----------------------------
# � Fetch and display leads
# -----------------------------
import requests
import pandas as pd

def get_all_leads(token):
    url = "https://orgb0732c8b.crm8.dynamics.com/api/data/v9.2/leads"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        leads = data.get('value', []) if 'value' in data else data.get('leads', [])
        return leads
    else:
        st.error(f"Failed to fetch leads: {response.status_code} {response.text}")
        return []

def login_screen():
    if "token" not in st.session_state:
        st.session_state.token = None

    st.title("Microsoft Login for Dynamics 365")

    msal_app = msal.ConfidentialClientApplication(
        client_id=CLIENT_ID,
        client_credential=CLIENT_SECRET,
        authority=AUTHORITY
    )

    query_params = st.experimental_get_query_params()
    auth_code = query_params.get("code", [None])[0]

    if auth_code and not st.session_state.token:
        result = msal_app.acquire_token_by_authorization_code(
            code=auth_code,
            scopes=SCOPE,
            redirect_uri=REDIRECT_URI
        )
        token = result.get("access_token")
        if token:
            st.session_state.token = token
            st.success("✅ Login successful!")
            st.experimental_set_query_params()
            st.rerun()
        else:
            st.error("❌ Login failed: " + result.get("error_description", "Unknown error"))

    elif st.session_state.token:
        st.success("✅ Already logged in")
        st.text_area("Access Token", st.session_state.token, height=300)
        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()
    else:
        auth_url = msal_app.get_authorization_request_url(
                scopes=SCOPE,
                redirect_uri=REDIRECT_URI
            )
        st.markdown(f"""
            <a href="{auth_url}" target="_self">
                <button style="background-color:#0078D4; color:white; padding:10px 20px; border:none; border-radius:5px; font-size:16px;">
                    Login with Microsoft
                </button>
            </a>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    login_screen()