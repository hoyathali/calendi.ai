from streamlit_option_menu import option_menu # type: ignore
import streamlit as st # type: ignore
from cmodel import setupModelandChat
def renderChatBotUi():
    st.markdown('<p style="color: cream; opacity:0.6">Made to make your life easy and your calendar clean.</p>', unsafe_allow_html=True)
    # Navigation
    with st.sidebar:
        selected = option_menu("", ["Home", 'About'], 
            icons=['house', 'person'], menu_icon="cast", default_index=0)
    if selected == "Home":
        pass
    if selected == "About":
        pass
    setupModelandChat()
    
