import streamlit as st # type: ignore
from authentication import authenticate, get_events_today ,get_zoom_oauth_token ,create_zoom_meeting
from chatbotui import renderChatBotUi
from cmodel import getCurrentWorld
import webbrowser
import datetime

st.set_page_config(page_title="Calendi.ai")

def main():
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
                renderChatBotUi()
                st.session_state["calenderevents"]= get_events_today(credentials)
                zoomtoken = get_zoom_oauth_token()
                print(zoomtoken)
                st.session_state['zoom_credentials']=zoomtoken['access_token']
                st.session_state['currentworld'] = getCurrentWorld()

        else:
            if st.button("Authenticate with Google to begin!!"):
                authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
                webbrowser.open(authorization_url)
    else:
        #Ignore this never occurs as of now
        zoomtoken = get_zoom_oauth_token()

        st.session_state['zoom_credentials']=zoomtoken['access_token']
        st.session_state['currentworld'] = getCurrentWorld()
        credentials = st.session_state['credentials']
        renderChatBotUi()

if __name__ == "__main__":
    main()
