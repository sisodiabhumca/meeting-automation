import os
import json
from dotenv import load_dotenv
import requests

print("=== Webex Setup ===")

# Load existing environment variables
load_dotenv()

print("\nStep 1: Create Webex Developer Account")
print("1. Go to https://developer.webex.com")
print("2. Sign up or log in")
print("3. Accept the terms of service")

print("\nStep 2: Create an Integration")
print("1. Go to 'My Webex Apps'")
print("2. Click 'Create a New App'")
print("3. Fill in the following:")
print("   - App Name: Meeting Automation Assistant")
print("   - App Type: Integration")
print("   - Description: Meeting automation tool")
print("4. Add these scopes:")
print("   - spark:all")
print("   - spark-admin:all")
print("   - spark-compliance:all")
print("   - spark-xapi-teams")
print("   - spark-xapi-rooms")
print("   - spark-xapi-messages")

print("\nStep 3: Get Access Token")
print("1. After creating the integration, go to 'Access Token'")
print("2. Click 'Generate Access Token'")
print("3. Copy the generated token")

print("\nStep 4: Configure .env file")
print("Add this value to your .env file:")
print("WEBEX_ACCESS_TOKEN=your_access_token")

# Check if .env file exists
if not os.path.exists('.env'):
    print("\nError: .env file not found!")
    print("Please create a .env file with your credentials")
    exit(1)

# Test the connection
print("\nTesting Webex connection...")

def test_webex_connection():
    try:
        # Get access token from environment
        access_token = os.getenv('WEBEX_ACCESS_TOKEN')

        if not access_token:
            print("\nError: WEBEX_ACCESS_TOKEN not found in .env file")
            return False

        # Test API call
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Test getting user info
        response = requests.get(
            'https://webexapis.com/v1/people/me',
            headers=headers
        )

        if response.status_code == 200:
            print("\n✅ Connection successful!")
            print("Your Webex credentials are working correctly.")
            return True
        else:
            print(f"\nError: API call failed with status {response.status_code}")
            print("Check your access token and try again.")
            return False

    except Exception as e:
        print(f"\nError during connection test: {str(e)}")
        return False

# Run the test
if test_webex_connection():
    print("\nSetup complete!")
    print("You can now use the main script with Webex services.")
else:
    print("\nSetup failed. Please check your configuration and try again.")
