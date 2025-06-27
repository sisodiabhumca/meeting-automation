# Meeting Automation Assistant 🤖

A user-friendly tool that helps you manage and summarize your meetings automatically. It works with your calendar, chat platforms, and AI models to create clear, concise summaries of your meetings.

## 🚀 What It Does

1. **Reads Your Meetings**
   - Automatically fetches upcoming meetings from your calendar
   - Supports Google Calendar, Microsoft Outlook, and Webex

2. **Gathers Context**
   - Collects related emails and documents
   - Finds relevant chat messages from Slack, Microsoft Teams

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file with your credentials:
```
OPENAI_API_KEY=your_openai_api_key
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token
```

### 3. Set Up Services

#### Google Calendar Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project
3. Enable these APIs:
   - Calendar API
   - Gmail API
   - Drive API
4. Create OAuth 2.0 credentials
5. Download credentials.json

#### Slack Setup
1. Go to [Slack API](https://api.slack.com/apps)
2. Create a new app
3. Add these bot permissions:
   - channels:read
   - channels:history
   - groups:read
   - groups:history
4. Install app to workspace
5. Get Bot User OAuth Token
6. Get App-Level Token

#### OpenAI Setup
1. Go to [OpenAI Platform](https://platform.openai.com)
2. Create account
3. Get API key

## Usage

### Run Setup Scripts
```bash
python setup_google_calendar.py
python setup_slack.py
python setup_openai.py
```

### Run Main Script
```bash
python meeting_automation.py
```

## Output

The script will:
1. Process all meetings
2. Search for related information
3. Generate summaries
4. Save results in `meeting_summary.json`

## Security

- Never commit `.env` file
- Keep API keys secure
- Regularly rotate tokens
