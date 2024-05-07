import streamlit as st # type: ignore
from authentication import authenticate
from chatbotui import renderChatBotUi
import webbrowser



st.set_page_config(page_title="Calendi.ai")

def main():
    """Main method for handling UI and user sessions."""
    st.title("💬 Your Calendi Assistant!!")

    if 'credentials' not in st.session_state or not st.session_state['credentials'].valid:
        flow = authenticate()
        auth_code = st.query_params.get('code')

        if auth_code:
            flow.fetch_token(code=auth_code)
            credentials = flow.credentials
            st.session_state['credentials'] = credentials

            if credentials.valid:
                st.write("Login Successful!")
                #st.write(f"Token: {credentials.token}")
                renderChatBotUi()

        else:
            if st.button("Authenticate with Google to begin!!"):
                authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
                webbrowser.open_new_tab(authorization_url)
    else:
        credentials = st.session_state['credentials']
        renderChatBotUi()


if __name__ == "__main__":
    main()
