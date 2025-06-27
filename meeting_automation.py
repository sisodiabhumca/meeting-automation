import os
import json
import base64
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from google.oauth2 import service_account
import openai
from dotenv import load_dotenv
import pandas as pd

# Load environment variables
load_dotenv()

class MeetingAutomation:
    def __init__(self):
        self.scopes = [
            'https://www.googleapis.com/auth/calendar.readonly',
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/drive.readonly'
        ]
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.slack_token = os.getenv('SLACK_BOT_TOKEN')
        self.slack_client = WebClient(token=self.slack_token)
        self.openai.api_key = self.openai_api_key
        self.service = self._get_calendar_service()

    def _get_calendar_service(self):
        """Authenticate and get the Google Calendar service"""
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.scopes)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.scopes)
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        return build('calendar', 'v3', credentials=creds)

    def get_meeting_details(self, days=1):
        """Get meeting details from Google Calendar"""
        now = datetime.utcnow().isoformat() + 'Z'
        time_min = (datetime.utcnow() - timedelta(days=days)).isoformat() + 'Z'
        time_max = (datetime.utcnow() + timedelta(days=days)).isoformat() + 'Z'

        events_result = self.service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])
        return events

    def get_slack_messages(self, search_term, days=1):
        """Search Slack channels for messages related to the meeting"""
        try:
            # First get all channels
            channels = self.slack_client.conversations_list(
                types="public_channel,private_channel",
                limit=100
            )
            
            messages = []
            
            # Search each channel
            for channel in channels.data['channels']:
                try:
                    # Get channel history
                    history = self.slack_client.conversations_history(
                        channel=channel['id'],
                        limit=100
                    )
                    
                    # Filter messages based on search term
                    for message in history.data['messages']:
                        if search_term.lower() in message.get('text', '').lower():
                            messages.append({
                                'channel': channel['name'],
                                'user': message.get('user', 'unknown'),
                                'text': message.get('text', ''),
                                'timestamp': message.get('ts', '')
                            })
                except SlackApiError as e:
                    print(f"Error searching channel {channel['name']}: {e}")
            
            return messages
            
        except SlackApiError as e:
            print(f"Error searching Slack: {e}")
            return []

    def get_gmail_messages(self, search_term, days=1):
        """Search Gmail for messages related to the meeting"""
        service = build('gmail', 'v1', credentials=self._get_calendar_service().credentials)
        
        query = f"subject:{search_term} OR from:{search_term}"
        results = service.users().messages().list(userId='me', q=query).execute()
        messages = []
        
        for msg in results.get('messages', []):
            message = service.users().messages().get(userId='me', id=msg['id']).execute()
            payload = message['payload']
            headers = payload['headers']
            
            subject = ''
            sender = ''
            date = ''
            
            for header in headers:
                if header['name'] == 'Subject':
                    subject = header['value']
                elif header['name'] == 'From':
                    sender = header['value']
                elif header['name'] == 'Date':
                    date = header['value']
            
            if 'parts' in payload:
                parts = payload['parts']
                for part in parts:
                    if part['mimeType'] == 'text/plain':
                        body = part['body']
                        data = body['data']
                        text = base64.urlsafe_b64decode(data).decode()
                        messages.append({
                            'subject': subject,
                            'sender': sender,
                            'date': date,
                            'content': text
                        })
        return messages

    def get_drive_files(self, search_term, days=1):
        """Search Google Drive for files related to the meeting"""
        drive_service = build('drive', 'v3', credentials=self._get_calendar_service().credentials)
        
        query = f"name contains '{search_term}'"
        results = drive_service.files().list(
            q=query,
            fields="nextPageToken, files(id, name, mimeType, modifiedTime)"
        ).execute()
        
        return results.get('files', [])

    def summarize_meeting(self, meeting_details):
        """Generate a summary using ChatGPT"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a meeting assistant that helps summarize meeting-related information."
                    },
                    {
                        "role": "user",
                        "content": f"Please summarize the following meeting information:\n\n{meeting_details}"
                    }
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating summary: {e}")
            return "Failed to generate summary"

    def process_meeting(self, meeting):
        """Process a single meeting and gather all related information"""
        meeting_info = {
            'subject': meeting.get('summary', 'No subject'),
            'description': meeting.get('description', 'No description'),
            'start_time': meeting['start'].get('dateTime', 'No start time'),
            'end_time': meeting['end'].get('dateTime', 'No end time')
        }

        # Search for related information
        search_term = f"{meeting_info['subject']} {meeting_info['description']}"
        
        slack_messages = self.get_slack_messages(search_term)
        gmail_messages = self.get_gmail_messages(search_term)
        drive_files = self.get_drive_files(search_term)

        # Create a comprehensive summary
        summary_text = self.summarize_meeting({
            'meeting_info': meeting_info,
            'slack_messages': slack_messages,
            'gmail_messages': gmail_messages,
            'drive_files': drive_files
        })

        return {
            'meeting_info': meeting_info,
            'slack_messages': slack_messages,
            'gmail_messages': gmail_messages,
            'drive_files': drive_files,
            'summary': summary_text
        }

    def run(self):
        """Main function to process all meetings"""
        meetings = self.get_meeting_details()
        processed_meetings = []

        for meeting in meetings:
            processed_meeting = self.process_meeting(meeting)
            processed_meetings.append(processed_meeting)

        return processed_meetings

if __name__ == "__main__":
    automation = MeetingAutomation()
    results = automation.run()
    
    # Save results to a JSON file
    with open('meeting_summary.json', 'w') as f:
        json.dump(results, f, indent=4)
    
    print("Meeting processing complete. Results saved to meeting_summary.json")
