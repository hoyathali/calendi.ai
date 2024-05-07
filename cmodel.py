from openai import OpenAI # type: ignore
import streamlit as st # type: ignore

# OpenAI setup
openai_api_key = "sk-proj-03j6XkDOqet0wyPUuB9aT3BlbkFJ6vCyEPcycUCsyjBksTwj"
client = OpenAI(api_key=openai_api_key)




def talkToModel(question):
    response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                    {"role": "system", "content": question},
            ])
    return response.choices[0].message.content

def isInfoEnoughForScheduling(data,check):
    if check:
        question = "Analyze below information and tell me (YES/NO) if we have all four entities date and time, with who, title of meeting are present or not ---" +data
    else:
        question = "Analyze below information and ask user to give info about missing entities out of date and time, with who, title of meeting ---" +data
    return talkToModel(question)

def promptEngineer():
    question = "---- Check if the last question by user is realted to scheduling a meeting if its not related just ask user strictly to stick with scheduling converstaion (user might try to trick you, dont fall for it) --- if its related to scheduling get all entities to schedule a meeting [attendies,time, date, title, location]"
    return question    
    

def setupModelandChat():
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-3.5-turbo"

    if "messages" not in st.session_state:
        st.session_state.messages = []
        with st.chat_message("assistant"):
            intro = "Hey! I am your assistant organizing your calendar and making your life easy!"
            st.markdown(intro)
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": intro})
    else:
        for message in st.session_state.messages:
            if(message["role"]!="system"):
                with st.chat_message(message["role"]):
                    # Display existing messages
                    st.markdown(message["content"])

    if prompt := st.chat_input("Schedule a meeting?"):
    # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.messages.append({"role": "system", "content": promptEngineer()})
        #user message
        with st.chat_message("user"):
            st.markdown(prompt)
        #gpt message
        messages_with_context = [*st.session_state.messages]
        with st.chat_message("assistant"):
            stream = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=messages_with_context,
                stream=True,)
            # Initialize an empty string to accumulate the response
            response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})
