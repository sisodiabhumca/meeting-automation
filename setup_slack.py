import os
import json

print("=== Slack Setup ===")
print("\nStep 1: Create Slack App")
print("1. Go to https://api.slack.com/apps")
print("2. Click 'Create New App'")
print("3. Name your app and select a workspace")

print("\nStep 2: Add Bot User")
print("1. Go to 'OAuth & Permissions'")
print("2. Scroll to 'Bot Token Scopes'")
print("3. Add these scopes:")
print("   - channels:read")
print("   - channels:history")
print("   - groups:read")
print("   - groups:history")
print("   - users:read")
print("4. Click 'Install App' to your workspace")
print("5. Copy the Bot User OAuth Token (starts with xoxb-)")

print("\nStep 3: Add App-Level Token")
print("1. Go to 'App-Level Tokens'")
print("2. Click 'Add New Token'")
print("3. Copy the App-Level Token (starts with xapp-)")

print("\nStep 4: Update .env file")
print("Add these tokens to your .env file:")
print("SLACK_BOT_TOKEN=xoxb-your-bot-token")
print("SLACK_APP_TOKEN=xapp-your-app-token")

# Check if .env file exists
if not os.path.exists('.env'):
    print("\nError: .env file not found!")
    print("Please create a .env file with your credentials")
    exit(1)

# Read current .env file
with open('.env', 'r') as f:
    env_content = f.read()

# Check if Slack tokens are already set
if 'SLACK_BOT_TOKEN=' in env_content and 'SLACK_APP_TOKEN=' in env_content:
    print("\nSlack tokens are already set in .env file!")
else:
    print("\nPlease add your Slack tokens to the .env file.")
    print("The file should look like this:")
    print("SLACK_BOT_TOKEN=xoxb-your-bot-token")
    print("SLACK_APP_TOKEN=xapp-your-app-token")
