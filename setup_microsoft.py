import os
import json
from dotenv import load_dotenv
from msal import ConfidentialClientApplication
import requests

print("=== Microsoft Office 365 Setup ===")

# Load existing environment variables
load_dotenv()

print("\nStep 1: Create Microsoft Azure App Registration")
print("1. Go to https://portal.azure.com")
print("2. Navigate to Azure Active Directory")
print("3. Go to App registrations")
print("4. Click 'New registration'")
print("5. Fill in the following:")
print("   - Name: Meeting Automation Assistant")
print("   - Supported account types: Accounts in any organizational directory")
print("   - Redirect URI: None required")

print("\nStep 2: Configure API permissions")
print("1. After creating the app, go to 'API permissions'")
print("2. Click 'Add a permission'")
print("3. Select 'Microsoft Graph'")
print("4. Add these permissions:")
print("   - Calendar.Read")
print("   - Mail.Read")
print("   - Chat.Read")
print("   - Chat.ReadBasic")
print("   - Chat.ReadWrite")
print("   - ChatMessage.Read")
print("5. Click 'Grant admin consent'")

print("\nStep 3: Get Client ID and Tenant ID")
print("1. Go to 'Overview' of your app registration")
print("2. Copy these values:")
print("   - Application (client) ID")
print("   - Directory (tenant) ID")

print("\nStep 4: Create Client Secret")
print("1. Go to 'Certificates & secrets'")
print("2. Click 'New client secret'")
print("3. Add a description and select an expiration period")
print("4. Copy the secret value immediately - it won't be shown again!")

print("\nStep 5: Configure .env file")
print("Add these values to your .env file:")
print("MS_CLIENT_ID=your_client_id")
print("MS_CLIENT_SECRET=your_client_secret")
print("MS_TENANT_ID=your_tenant_id")

# Check if .env file exists
if not os.path.exists('.env'):
    print("\nError: .env file not found!")
    print("Please create a .env file with your credentials")
    exit(1)

# Test the connection
print("\nTesting Microsoft Graph connection...")

def test_microsoft_connection():
    try:
        # Get credentials from environment
        client_id = os.getenv('MS_CLIENT_ID')
        client_secret = os.getenv('MS_CLIENT_SECRET')
        tenant_id = os.getenv('MS_TENANT_ID')

        if not all([client_id, client_secret, tenant_id]):
            print("\nError: Missing Microsoft credentials in .env file")
            return False

        # Create MSAL app
        app = ConfidentialClientApplication(
            client_id,
            authority=f'https://login.microsoftonline.com/{tenant_id}',
            client_credential=client_secret
        )

        # Get token
        result = app.acquire_token_for_client(scopes=[
            'https://graph.microsoft.com/.default'
        ])

        if "access_token" not in result:
            print("\nError: Failed to get access token")
            print("Check your credentials and permissions in Azure Portal")
            return False

        # Test API call
        headers = {
            'Authorization': f'Bearer {result["access_token"]}',
            'Content-Type': 'application/json'
        }
        response = requests.get(
            'https://graph.microsoft.com/v1.0/me',
            headers=headers
        )

        if response.status_code == 200:
            print("\n✅ Connection successful!")
            print("Your Microsoft credentials are working correctly.")
            return True
        else:
            print(f"\nError: API call failed with status {response.status_code}")
            return False

    except Exception as e:
        print(f"\nError during connection test: {str(e)}")
        return False

# Run the test
if test_microsoft_connection():
    print("\nSetup complete!")
    print("You can now use the main script with Microsoft services.")
else:
    print("\nSetup failed. Please check your configuration and try again.")
