import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import json

print("=== Google Calendar Setup ===")
print("\nStep 1: Create Google Cloud Project")
print("1. Go to https://console.cloud.google.com")
print("2. Create a new project or select an existing one")
print("3. Enable the following APIs:")
print("   - Calendar API")
print("   - Gmail API")
print("   - Drive API")

print("\nStep 2: Create OAuth 2.0 Credentials")
print("1. Go to API & Services -> Credentials")
print("2. Click 'Create Credentials' -> 'OAuth client ID'")
print("3. Select 'Desktop app' as application type")
print("4. Download the credentials JSON file")
print("5. Save it as 'credentials.json' in this directory")

print("\nStep 3: Run this script to authenticate")
print("The script will guide you through the authentication process")

# Check if credentials.json exists
if not os.path.exists('credentials.json'):
    print("\nError: credentials.json not found!")
    print("Please download the credentials JSON file from Google Cloud Console")
    exit(1)

# Define the scopes
SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/drive.readonly'
]

creds = None
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)

    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

print("\nAuthentication complete!")
print("Your token.json has been created.")
print("You can now use the main script.")
