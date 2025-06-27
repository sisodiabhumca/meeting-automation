import os

print("=== OpenAI Setup ===")
print("\nStep 1: Create OpenAI Account")
print("1. Go to https://platform.openai.com")
print("2. Sign up or log in to your account")

print("\nStep 2: Get API Key")
print("1. Click on your profile picture")
print("2. Go to 'API Keys'")
print("3. Click 'Create new secret key'")
print("4. Copy the API key that starts with 'sk-'")

print("\nStep 3: Update .env file")
print("Add your API key to the .env file:")
print("OPENAI_API_KEY=sk-your-api-key-here")

# Check if .env file exists
if not os.path.exists('.env'):
    print("\nError: .env file not found!")
    print("Please create a .env file with your credentials")
    exit(1)

# Read current .env file
with open('.env', 'r') as f:
    env_content = f.read()

# Check if OpenAI API key is already set
if 'OPENAI_API_KEY=' in env_content:
    print("\nOpenAI API key is already set in .env file!")
else:
    print("\nPlease add your OpenAI API key to the .env file.")
    print("The file should look like this:")
    print("OPENAI_API_KEY=sk-your-api-key-here")
