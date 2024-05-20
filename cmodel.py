from openai import OpenAI   # type: ignore
import streamlit as st      # type: ignore
from authentication import authenticate, get_events_today ,get_zoom_oauth_token , create_zoom_meeting
import datetime
import json
import sys


meeting_details = {
  'topic': '',
  'type': 2,  # Scheduled meeting
  'start_time': '',  # Use format 'YYYY-MM-DDTHH:MM:SS' in UTC
  'duration': 60,  # Duration in minutes
  'timezone': 'America/New_York',
  'agenda': '',
  'settings': {
      'host_video': True,
      'participant_video': True,
      'join_before_host': False,
      'mute_upon_entry': True,
      'watermark': True,
      'use_pmi': False,  # Personal Meeting ID
      'approval_type': 0,  # Automatically approve
      'registration_type': 1  # Attendees register once
      },
  'recipients': [] }

# OpenAI setup
openai_api_key = "sk-proj-03j6XkDOqet0wyPUuB9aT3BlbkFJ6vCyEPcycUCsyjBksTwj"
client = OpenAI(api_key=openai_api_key)
MAX_CONTEXT_LENGTH = 16385

topics=["Schedule meeting"]

#Zero Shot function - most generic one to get data from model 
def talkToModel(question):
    response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                    {"role": "system", "content": question},
            ])
    return response.choices[0].message.content

def getCurrentWorld():
    current_datetime = datetime.datetime.now()
    current_date = current_datetime.date()
    current_time = current_datetime.time()
    current_day_of_week = current_datetime.weekday()
    current_world= ','.join([str(current_date), str(current_time), str(current_day_of_week)])
    st.session_state['currentworld']=current_world

def getUserMeetings():
    st.session_state["calenderevents"]= get_events_today(st.session_state['credentials'])

def detectCurrentTopic(prompt):
    topicDetectionTemplate= f"Just tell me what topic does the prompt fall under out off given topics [{', '.join(topics)}].  \n prompt: {prompt} \n Answer: "
    topic = talkToModel(topicDetectionTemplate) 
    if topic in topics:
        st.session_state["topic"] = topic 
        print("Topic Detected :")
    print(topic)
        
def isTopicDetected():
    try:
        if not st.session_state["topic"]:
            return False
    except KeyError:
        return False
    return True

def buildContext():
    getCurrentWorld()
    st.session_state.system_messages.append({"role": "system", "content": "Current Date and Time : "+ st.session_state['currentworld']})
    getUserMeetings()
    st.session_state.system_messages.append({"role": "system", "content": "Existing User Meetings information: "+  json.dumps(st.session_state['calenderevents'])})
    st.session_state.system_messages.append({"role": "system", "content": "---Strictly Force the User to only stick to context of helping user with organizign meetings---"})

    if isTopicDetected():
        buildTopicContext(st.session_state["topic"])

def buildTopicContext(topic):
    if topic == "Schedule meeting":
        st.session_state.system_messages.append({"role": "system", "content": "Current task for Assistant : Get All required entities [agenda,attendies,date,time] to schedule a meeting"})

def validateScheduleMeetingDetails():
    if meeting_details['topic'] is None or meeting_details['topic'] == "" or meeting_details['topic'] == "null":
        return False
    if meeting_details['start_time'] is None or meeting_details['start_time'] == "" or meeting_details['start_time'] == "null":
        return False
    if meeting_details['recipients'] is None or meeting_details['recipients'] == "" or meeting_details['recipients'] == "null":
        return False
    return True

def TakeActionOnTopic(topic):
    if topic == "Schedule meeting":
        user_messages = [message for message in st.session_state.messages if message["role"] in ["user","assistant"]]

    try:
        #print(user_messages)
        scheduleMeetingTemplate = f"Extract [agenda, recipients and date_time in format(YYYY-MM-DDTHH:MM:SS) of the meeting which is to be scheduled --- (Strictly add Null if they are not present yet) from <Context>: {user_messages} </context> in json format (lower case) -- just the format so that I can parse not a word extra."
        scheduleMeetingTemplate = json.loads(talkToModel(scheduleMeetingTemplate).lower())
        print(f"--- {scheduleMeetingTemplate}")
        meeting_details['topic'] = scheduleMeetingTemplate["agenda"]
        meeting_details['start_time'] = scheduleMeetingTemplate["date_time"]
        meeting_details['recipients'] = scheduleMeetingTemplate["recipients"]
        
        access_token = st.session_state.get('zoom_credentials')  # Using .get() to avoid KeyError if 'zoom_credentials' is not in st.session_state
        if access_token is not None and validateScheduleMeetingDetails():
            user_id = 'hoyathali@gmail.com'
            print("Scheduled ")
            result = create_zoom_meeting(access_token, user_id, meeting_details)
            #print(result)
            st.session_state.system_messages.append({"role": "system", "content": " Tell user about confirmation with zoom meeting id : Scheduled on zoom - Inform User using main details of zoom " + result})
            st.session_state["topic"]= ""
        else:
            print("No enough details yet to schedule a meeting")
    except json.JSONDecodeError:
        print("Invalid JSON format.")
    except KeyError as e:
        print(f"KeyError: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


def setupModelandChat():
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-3.5-turbo"

    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.system_messages = []
        
        with st.chat_message("assistant"):
            intro = "Hey! I am your assistant organizing your calendar and making your life easy!"
            st.markdown(intro)
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": intro})
    else:
        for message in st.session_state.messages:
            #Hide System prompts and diplay other messages
            if(message["role"]!="system"):
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

    if prompt := st.chat_input("Schedule a meeting?"):
        st.session_state.system_messages=[]

    # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        #Markdown the user input on UI
        with st.chat_message("user"):
            st.markdown(prompt)

        if not isTopicDetected():
            detectCurrentTopic(prompt)
        else: 
            TakeActionOnTopic(st.session_state["topic"])

        #Talk to GPT through stream with context
        buildContext()   #Context Decider/Enhancer

        #Extract all the messages 
        messages_with_context = []
        # Add user and assistant messages

        messages_with_context.extend([message for message in st.session_state.messages if message["role"] in ["user", "assistant"]])
        messages_with_context.extend([*st.session_state.system_messages])        
        if len(messages_with_context) > MAX_CONTEXT_LENGTH:
            messages_with_context = messages_with_context[-MAX_CONTEXT_LENGTH:]
        
        #print(messages_with_context)
        
        with st.chat_message("assistant"):
            stream = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=messages_with_context,
                stream=True,)
            response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})
            
