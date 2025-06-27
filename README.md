# Meeting Automation Assistant

This script automates the process of gathering meeting information from various sources and generating summaries.

## Features

- Reads meeting details from Google Calendar
- Searches Slack for related messages
- Searches Gmail for related emails
- Searches Google Drive for related files
- Generates comprehensive summaries using ChatGPT

## Setup Instructions

1. Install required packages:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
Create a `.env` file with the following variables:
```
OPENAI_API_KEY=your_openai_api_key
SLACK_BOT_TOKEN=your_slack_bot_token
```

3. Google Calendar Setup:
- Go to Google Cloud Console and create a new project
- Enable Calendar API, Gmail API, and Drive API
- Download credentials.json and place it in the project directory
- Run the script once to authenticate and create token.json

4. Slack Setup:
- Create a Slack app
- Install the app to your workspace
- Get the Bot User OAuth Token
- Add the token to your .env file

## Usage

Run the script:
```bash
python meeting_automation.py
```

The script will process all meetings in the past and future day by default and save the results in `meeting_summary.json`.
