import streamlit as st
import msal
import requests

CLIENT_ID = st.secrets["CLIENT_ID"]
CLIENT_SECRET = st.secrets["CLIENT_SECRET"]
TENANT_ID = st.secrets["TENANT_ID"]
AUTHORITY = st.secrets["AUTHORITY"]
REDIRECT_URI = st.secrets["REDIRECT_URI"]
SCOPE = st.secrets["SCOPE"]

def login_screen():
    if "token" not in st.session_state:
        st.session_state.token = None

    st.title("Microsoft Login Generate Token")

    msal_app = msal.ConfidentialClientApplication(
        client_id=CLIENT_ID,
        client_credential=CLIENT_SECRET,
        authority=AUTHORITY
    )

    query_params = st.experimental_get_query_params()
    auth_code = query_params.get("code", [None])[0]

    if auth_code and not st.session_state.get("token"):
        try:
            result = msal_app.acquire_token_by_authorization_code(
                code=auth_code,
                scopes=SCOPE,
                redirect_uri=REDIRECT_URI
            )
            token = result.get("access_token")
            if token:
                st.session_state.token = token
                st.success("✅ Login successful!")
                st.experimental_set_query_params()  # Clear ?code= from URL
                st.rerun()  # Reload app without the code in URL
            else:
                error_msg = result.get("error_description", "Unknown error")
                st.error(f"❌ Login failed: {error_msg}")
                st.experimental_set_query_params()  # Important to clear reused code!
        except Exception as e:
            st.error(f"❌ Exception occurred: {e}")
            st.experimental_set_query_params()

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