import json
import google_auth_oauthlib.flow
import streamlit as st # type: ignore
import datetime
from googleapiclient.discovery import build
import requests
import base64

REDIRECT_URI = 'http://localhost:8501'
CLIENT_ID = '249288731224-tjbb7680cp7t8rqqshvr4827s12hmi6o.apps.googleusercontent.com'
CLIENT_SECRET = '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'
PROJECT_ID = 'calendi-422102'

#zoom stuff
client_id="At59k9U1SHONeW9SmStETQ"
client_secret="i72FEjVJZtLfSoV9o8HVmOC220L2xubi" 
account_id="RlJmM6v3SWidlBTsvvAOUA"


# Authentication function
def authenticate():
    """Authenticate using Google as the IDP provider and store credentials."""
    json_str = json.dumps({
        "web": {
            "client_id": CLIENT_ID,
            "project_id": PROJECT_ID,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": CLIENT_SECRET,
            "redirect_uris": [REDIRECT_URI],
            "javascript_origins": [REDIRECT_URI]
        }
    })
    client_config = json.loads(json_str)
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        client_config=client_config,
        scopes=[
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile',
            'https://www.googleapis.com/auth/calendar.readonly',
            'https://www.googleapis.com/auth/calendar.events',
            'openid'],
        redirect_uri=REDIRECT_URI,
    )
    return flow


def get_events_today(credentials):
    """Fetches all events for the current day from Google Calendar."""
    # Build the service object
    service = build('calendar', 'v3', credentials=credentials)

    # Get today's date and format it for the calendar API
    now = datetime.datetime.utcnow()
    start_of_today = datetime.datetime(now.year, now.month, now.day, 0, 0, 0).isoformat() + 'Z'  # 'Z' indicates UTC time
    end_of_today = datetime.datetime(now.year, now.month, now.day, 23, 59, 59).isoformat() + 'Z'

    # Call the Calendar API to fetch the events
    events_result = service.events().list(
        calendarId='primary',  # Assuming primary calendar; can be changed to other calendar IDs
        timeMin=start_of_today,
        timeMax=end_of_today,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found for today.')
    else:
        #print(events)
        #for event in events:
        #    start = event['start'].get('dateTime', event['start'].get('date'))
        #    print(event['summary'], "at", start)
        pass
    return events



def get_zoom_oauth_token():
    credentials = f"{client_id}:{client_secret}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    headers = {
        'Authorization': f'Basic {encoded_credentials}',
        'Host': 'zoom.us'}
    data = {
        'grant_type': 'account_credentials',
        'account_id': account_id}
    response = requests.post('https://zoom.us/oauth/token', headers=headers, data=data)

    if response.status_code == 200:

        return response.json()  
    else:
        return {'error': 'Failed to retrieve token', 'status_code': response.status_code, 'details': response.text}

def create_zoom_meeting(access_token, user_id, meeting_details):

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    url = f'https://api.zoom.us/v2/users/{user_id}/meetings'
    response = requests.post(url, headers=headers, json=meeting_details)

    if response.status_code == 201:
        return json.dumps(response.json())  # Return meeting details
    else:
        return {'error': 'Failed to create meeting', 'status_code': response.status_code, 'details': response.text}

# Example usage:


# Replace 'your_access_token' and 'your_user_id' with actual values

