# Meeting Automation Credentials Setup Guide

## OpenAI API Key
1. Go to https://platform.openai.com/api-keys
2. Generate a new API key
3. Copy the key and paste it in your `.env` file as `OPENAI_API_KEY`

## Slack Setup
1. Create a new Slack App at https://api.slack.com/apps
2. Install the app to your workspace
3. Get the Bot User OAuth Token (starts with `xoxb-`)
4. Get the App-Level Token (starts with `xapp-`)
5. Add both tokens to your `.env` file

## Google Calendar Setup
1. Go to Google Cloud Console (https://console.cloud.google.com)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Calendar API
   - Gmail API
   - Drive API
4. Create credentials:
   - Go to "Credentials"
   - Click "Create Credentials" -> "OAuth client ID"
   - Select "Desktop app" as application type
   - Download the credentials JSON file and save it as `credentials.json`
5. The first time you run the script, it will create a `token.json` file automatically

## Environment Variables
Create a `.env` file in the project root directory and add the following variables:

```
OPENAI_API_KEY=your_openai_api_key_here
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token
GOOGLE_CREDENTIALS_FILE=credentials.json
GOOGLE_TOKEN_FILE=token.json
```

## Security Note
- Never commit your `.env` file to version control
- Add `.env` to your `.gitignore` file
- Keep your API keys and tokens secure
- Regularly rotate your API keys and tokens

## Troubleshooting
1. If you encounter authentication errors:
   - Delete the `token.json` file
   - Run the script again to re-authenticate
2. If Slack integration fails:
   - Ensure your Slack app has the required permissions:
     - channels:read
     - channels:history
     - groups:read
     - groups:history
3. If Google Calendar integration fails:
   - Check if all required APIs are enabled in Google Cloud Console
   - Verify that your credentials.json file is valid
   - Make sure you have the correct scope permissions
