import msal_streamlit

ENV = "production"

oauth_client = msal_streamlit.oauth_client_prod if ENV == "production" else msal_streamlit.oauth_client_test

oauth_scopes = oauth_client.ScopesPRD if ENV == "production" else oauth_client.ScopesTST
