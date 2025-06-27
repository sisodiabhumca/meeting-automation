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
from exchangelib import Credentials as ExchangeCredentials, Account, DELEGATE, Configuration
from exchangelib.protocol import BaseProtocol, NoVerifyHTTPAdapter
from webexteamssdk import WebexTeamsAPI
import openai
import anthropic
import google.generativeai as genai
import cohere
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers import pipeline
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
import boto3
import sagemaker
from dotenv import load_dotenv
import pandas as pd
from msal import ConfidentialClientApplication
import requests
from typing import List, Dict, Optional

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

    def get_meeting_details(self, days=1, calendar_type='all'):
        """Get meeting details from all configured calendars"""
        meetings = []
        
        if calendar_type in ['all', 'google']:
            meetings.extend(self._get_google_meetings(days))
        
        if calendar_type in ['all', 'microsoft']:
            meetings.extend(self._get_microsoft_meetings(days))
        
        return meetings

    def _get_google_meetings(self, days=1):
        """Get meetings from Google Calendar"""
        if not hasattr(self, 'google_service'):
            return []

        now = datetime.utcnow().isoformat() + 'Z'
        time_min = (datetime.utcnow() - timedelta(days=days)).isoformat() + 'Z'
        time_max = (datetime.utcnow() + timedelta(days=days)).isoformat() + 'Z'

        try:
            events_result = self.google_service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            return [{
                'source': 'google',
                'summary': event.get('summary', ''),
                'description': event.get('description', ''),
                'start': event['start'].get('dateTime', ''),
                'end': event['end'].get('dateTime', '')
            } for event in events]
        except Exception as e:
            print(f"Error getting Google Calendar meetings: {e}")
            return []

    def _get_microsoft_meetings(self, days=1):
        """Get meetings from Microsoft Calendar"""
        if not hasattr(self, 'ms_headers'):
            return []

        try:
            days_ago = (datetime.utcnow() - timedelta(days=days)).isoformat()
            days_ahead = (datetime.utcnow() + timedelta(days=days)).isoformat()
            url = f'https://graph.microsoft.com/v1.0/me/calendarView?startDateTime={days_ago}&endDateTime={days_ahead}'
            response = requests.get(url, headers=self.ms_headers)
            
            if response.status_code == 200:
                events = response.json().get('value', [])
                return [{
                    'source': 'microsoft',
                    'summary': event.get('subject', ''),
                    'description': event.get('bodyPreview', ''),
                    'start': event['start'].get('dateTime', ''),
                    'end': event['end'].get('dateTime', '')
                } for event in events]
            return []
        except Exception as e:
            print(f"Error getting Microsoft Calendar meetings: {e}")
            return []

    def get_collaboration_messages(self, search_term, days=1):
        """Search all configured collaboration tools for messages"""
        messages = []
        
        # Slack messages
        if hasattr(self, 'slack_client'):
            messages.extend(self._get_slack_messages(search_term, days))
        
        # Webex messages
        if hasattr(self, 'webex_api'):
            messages.extend(self._get_webex_messages(search_term, days))
        
        # Microsoft Teams messages
        if hasattr(self, 'ms_headers'):
            messages.extend(self._get_teams_messages(search_term, days))
        
        return messages

    def _get_slack_messages(self, search_term, days=1):
        """Search Slack channels for messages"""
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
                                'source': 'slack',
                                'channel': channel['name'],
                                'user': message.get('user', 'unknown'),
                                'text': message.get('text', ''),
                                'timestamp': message.get('ts', ''),
                                'platform': 'slack'
                            })
                except SlackApiError as e:
                    print(f"Error searching Slack channel {channel['name']}: {e}")
            
            return messages
            
        except SlackApiError as e:
            print(f"Error searching Slack: {e}")
            return []

    def _get_webex_messages(self, search_term, days=1):
        """Search Webex spaces for messages"""
        try:
            # Get all rooms
            rooms = self.webex_api.rooms.list()
            messages = []
            
            for room in rooms:
                try:
                    # Get messages from room
                    room_messages = self.webex_api.messages.list(roomId=room.id)
                    for message in room_messages:
                        if search_term.lower() in message.text.lower():
                            messages.append({
                                'source': 'webex',
                                'channel': room.title,
                                'user': message.personEmail,
                                'text': message.text,
                                'timestamp': message.created,
                                'platform': 'webex'
                            })
                except Exception as e:
                    print(f"Error searching Webex room {room.title}: {e}")
            
            return messages
        except Exception as e:
            print(f"Error searching Webex: {e}")
            return []

    def _get_teams_messages(self, search_term, days=1):
        """Search Microsoft Teams messages"""
        try:
            # Get chats
            url = 'https://graph.microsoft.com/v1.0/me/chats'
            response = requests.get(url, headers=self.ms_headers)
            
            if response.status_code == 200:
                chats = response.json().get('value', [])
                messages = []
                
                for chat in chats:
                    # Get messages from chat
                    messages_url = f'https://graph.microsoft.com/v1.0/me/chats/{chat["id"]}/messages'
                    msg_response = requests.get(messages_url, headers=self.ms_headers)
                    
                    if msg_response.status_code == 200:
                        chat_messages = msg_response.json().get('value', [])
                        for msg in chat_messages:
                            if search_term.lower() in msg.get('body', {}).get('content', '').lower():
                                messages.append({
                                    'source': 'teams',
                                    'channel': chat.get('topic', 'Chat'),
                                    'user': msg.get('from', {}).get('user', {}).get('email', 'unknown'),
                                    'text': msg.get('body', {}).get('content', ''),
                                    'timestamp': msg.get('createdDateTime', ''),
                                    'platform': 'teams'
                                })
                return messages
            return []
        except Exception as e:
            print(f"Error searching Teams: {e}")
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

    def _get_model_config(self, model_type):
        """Get configuration for a specific AI model"""
        config = {}
        
        # Common configuration
        config['max_retries'] = int(os.getenv(f'{model_type.upper()}_MAX_RETRIES', 3))
        config['timeout'] = int(os.getenv(f'{model_type.upper()}_TIMEOUT', 30))
        
        # Model-specific configuration
        if model_type == 'openai':
            config['model'] = os.getenv('OPENAI_MODEL', 'gpt-4')
            config['max_tokens'] = int(os.getenv('OPENAI_MAX_TOKENS', 2000))
            config['temperature'] = float(os.getenv('OPENAI_TEMPERATURE', 0.7))
            config['top_p'] = float(os.getenv('OPENAI_TOP_P', 0.9))
        elif model_type == 'anthropic':
            config['model'] = os.getenv('ANTHROPIC_MODEL', 'claude-3-sonnet-20240229')
            config['max_tokens'] = int(os.getenv('ANTHROPIC_MAX_TOKENS', 2000))
            config['temperature'] = float(os.getenv('ANTHROPIC_TEMPERATURE', 0.7))
            config['top_p'] = float(os.getenv('ANTHROPIC_TOP_P', 0.9))
        elif model_type == 'google':
            config['model'] = os.getenv('GOOGLE_MODEL', 'gemini-pro')
            config['max_output_tokens'] = int(os.getenv('GOOGLE_MAX_OUTPUT_TOKENS', 2000))
            config['temperature'] = float(os.getenv('GOOGLE_TEMPERATURE', 0.7))
            config['top_p'] = float(os.getenv('GOOGLE_TOP_P', 0.8))
        elif model_type == 'cohere':
            config['model'] = os.getenv('COHERE_MODEL', 'command-xlarge-nightly')
            config['max_tokens'] = int(os.getenv('COHERE_MAX_TOKENS', 500))
            config['temperature'] = float(os.getenv('COHERE_TEMPERATURE', 0.7))
            config['top_p'] = float(os.getenv('COHERE_TOP_P', 0.9))
        elif model_type == 'huggingface':
            config['model'] = os.getenv('HUGGINGFACE_MODEL', 'meta-llama/Llama-2-70b-chat')
            config['max_tokens'] = int(os.getenv('HUGGINGFACE_MAX_TOKENS', 2000))
            config['temperature'] = float(os.getenv('HUGGINGFACE_TEMPERATURE', 0.7))
            config['top_p'] = float(os.getenv('HUGGINGFACE_TOP_P', 0.9))
            config['top_k'] = int(os.getenv('HUGGINGFACE_TOP_K', 40))
            config['repetition_penalty'] = float(os.getenv('HUGGINGFACE_REPETITION_PENALTY', 1.1))
            config['do_sample'] = os.getenv('HUGGINGFACE_DO_SAMPLE', 'true').lower() == 'true'
            config['use_cache'] = os.getenv('HUGGINGFACE_USE_CACHE', 'true').lower() == 'true'
            config['num_beams'] = int(os.getenv('HUGGINGFACE_NUM_BEAMS', 1))
            config['max_time'] = int(os.getenv('HUGGINGFACE_MAX_TIME', 30))
            config['min_length'] = int(os.getenv('HUGGINGFACE_MIN_LENGTH', 100))
            config['early_stopping'] = os.getenv('HUGGINGFACE_EARLY_STOPPING', 'false').lower() == 'true'
            config['pad_token_id'] = int(os.getenv('HUGGINGFACE_PAD_TOKEN_ID', 0))
            config['eos_token_id'] = int(os.getenv('HUGGINGFACE_EOS_TOKEN_ID', 2))
            config['device'] = os.getenv('HUGGINGFACE_DEVICE', 'cuda')
            config['model_cache_dir'] = os.getenv('HUGGINGFACE_MODEL_CACHE_DIR', '~/.cache/huggingface/models')
        elif model_type == 'azure':
            config['model'] = os.getenv('AZURE_MODEL', 'gpt-4')
            config['max_tokens'] = int(os.getenv('AZURE_MAX_TOKENS', 2000))
            config['temperature'] = float(os.getenv('AZURE_TEMPERATURE', 0.7))
            config['top_p'] = float(os.getenv('AZURE_TOP_P', 0.9))
            config['top_k'] = int(os.getenv('AZURE_TOP_K', 40))
            config['presence_penalty'] = float(os.getenv('AZURE_PRESENCE_PENALTY', 0))
            config['frequency_penalty'] = float(os.getenv('AZURE_FREQUENCY_PENALTY', 0))
            config['stop_sequences'] = os.getenv('AZURE_STOP_SEQUENCES', '').split(',') if os.getenv('AZURE_STOP_SEQUENCES') else []
            config['api_version'] = os.getenv('AZURE_API_VERSION', '2023-05-15-preview')
            config['deployment_name'] = os.getenv('AZURE_DEPLOYMENT_NAME', 'deployment1')
            config['batch_size'] = int(os.getenv('AZURE_BATCH_SIZE', 1))
            config['max_concurrency'] = int(os.getenv('AZURE_MAX_CONCURRENCY', 1))
            config['enable_logging'] = os.getenv('AZURE_ENABLE_LOGGING', 'false').lower() == 'true'
            config['log_file_path'] = os.getenv('AZURE_LOG_FILE_PATH', 'azure_ai.log')
        elif model_type == 'sagemaker':
            config['model'] = os.getenv('SAGEMAKER_MODEL', 'meta-textgeneration-llama-2-70b-chat')
            config['max_tokens'] = int(os.getenv('SAGEMAKER_MAX_TOKENS', 2000))
            config['temperature'] = float(os.getenv('SAGEMAKER_TEMPERATURE', 0.7))
            config['top_p'] = float(os.getenv('SAGEMAKER_TOP_P', 0.9))
            config['top_k'] = int(os.getenv('SAGEMAKER_TOP_K', 40))
            config['repetition_penalty'] = float(os.getenv('SAGEMAKER_REPETITION_PENALTY', 1.1))
            config['do_sample'] = os.getenv('SAGEMAKER_DO_SAMPLE', 'true').lower() == 'true'
            config['num_return_sequences'] = int(os.getenv('SAGEMAKER_NUM_RETURN_SEQUENCES', 1))
            config['max_time'] = int(os.getenv('SAGEMAKER_MAX_TIME', 30))
            config['min_length'] = int(os.getenv('SAGEMAKER_MIN_LENGTH', 100))
            config['early_stopping'] = os.getenv('SAGEMAKER_EARLY_STOPPING', 'false').lower() == 'true'
            config['max_concurrency'] = int(os.getenv('SAGEMAKER_MAX_CONCURRENCY', 1))
            config['enable_logging'] = os.getenv('SAGEMAKER_ENABLE_LOGGING', 'false').lower() == 'true'
            config['log_file_path'] = os.getenv('SAGEMAKER_LOG_FILE_PATH', 'sagemaker.log')
            config['use_ssl'] = os.getenv('SAGEMAKER_USE_SSL', 'true').lower() == 'true'
            config['verify_ssl'] = os.getenv('SAGEMAKER_VERIFY_SSL', 'true').lower() == 'true'
            config['proxy_host'] = os.getenv('SAGEMAKER_PROXY_HOST', '')
            config['proxy_port'] = os.getenv('SAGEMAKER_PROXY_PORT', '')
        
        return config

    def get_ai_model(self):
        """Get the configured AI model based on environment settings"""
        model_type = os.getenv('DEFAULT_AI_MODEL', 'openai').lower()
        
        if model_type not in ['openai', 'anthropic', 'google', 'cohere', 'huggingface', 'azure', 'sagemaker']:
            raise ValueError(f"Unknown AI model type: {model_type}")
            
        try:
            if model_type == 'openai':
                return self._get_openai_model()
            elif model_type == 'anthropic':
                return self._get_anthropic_model()
            elif model_type == 'google':
                return self._get_google_model()
            elif model_type == 'cohere':
                return self._get_cohere_model()
            elif model_type == 'huggingface':
                return self._get_huggingface_model()
            elif model_type == 'azure':
                return self._get_azure_model()
            elif model_type == 'sagemaker':
                return self._get_sagemaker_model()
        except Exception as e:
            print(f"Error initializing {model_type} model: {str(e)}")
            return None

    def _get_huggingface_model(self):
        """Initialize HuggingFace model"""
        try:
            api_key = os.getenv('HUGGINGFACE_API_KEY')
            if not api_key:
                raise ValueError("HuggingFace API key not configured")
                
            config = self._get_model_config('huggingface')
            model_name = config['model']
            
            # Initialize model
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                trust_remote_code=True,
                use_auth_token=api_key
            )
            
            # Create pipeline
            pipe = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                max_new_tokens=config['max_tokens'],
                temperature=config['temperature'],
                top_p=config['top_p']
            )
            
            return {
                'client': pipe,
                'config': config
            }
        except Exception as e:
            print(f"Error configuring HuggingFace model: {str(e)}")
            return None

    def _get_azure_model(self):
        """Initialize Azure AI model"""
        try:
            api_key = os.getenv('AZURE_API_KEY')
            endpoint = os.getenv('AZURE_ENDPOINT')
            if not api_key or not endpoint:
                raise ValueError("Azure API key and endpoint not configured")
                
            config = self._get_model_config('azure')
            
            # Initialize Azure OpenAI client
            openai.api_type = "azure"
            openai.api_version = "2023-05-15-preview"
            openai.api_base = endpoint
            openai.api_key = api_key
            
            return {
                'client': openai,
                'config': config
            }
        except Exception as e:
            print(f"Error configuring Azure model: {str(e)}")
            return None

    def _get_sagemaker_model(self):
        """Initialize AWS SageMaker model"""
        try:
            access_key = os.getenv('AWS_ACCESS_KEY_ID')
            secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
            region = os.getenv('AWS_REGION', 'us-east-1')
            endpoint = os.getenv('SAGEMAKER_ENDPOINT')
            if not access_key or not secret_key or not endpoint:
                raise ValueError("AWS credentials and SageMaker endpoint not configured")
                
            config = self._get_model_config('sagemaker')
            
            # Initialize SageMaker client
            boto3.setup_default_session(
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region
            )
            
            client = boto3.client('sagemaker-runtime')
            
            return {
                'client': client,
                'endpoint': endpoint,
                'config': config
            }
        except Exception as e:
            print(f"Error configuring SageMaker model: {str(e)}")
            return None

    def _get_openai_model(self):
        """Initialize OpenAI model with configuration"""
        try:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OpenAI API key not configured")
                
            config = self._get_model_config('openai')
            openai.api_key = api_key
            return {
                'client': openai,
                'config': config
            }
        except Exception as e:
            print(f"Error configuring OpenAI model: {str(e)}")
            return None

    def _get_anthropic_model(self):
        """Initialize Anthropic model with configuration"""
        try:
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                raise ValueError("Anthropic API key not configured")
                
            config = self._get_model_config('anthropic')
            return {
                'client': anthropic.Anthropic(api_key=api_key),
                'config': config
            }
        except Exception as e:
            print(f"Error configuring Anthropic model: {str(e)}")
            return None

    def _get_google_model(self):
        """Initialize Google AI model with configuration"""
        try:
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key:
                raise ValueError("Google API key not configured")
                
            config = self._get_model_config('google')
            genai.configure(api_key=api_key)
            return {
                'client': genai.GenerativeModel(model=config['model']),
                'config': config
            }
        except Exception as e:
            print(f"Error configuring Google AI model: {str(e)}")
            return None

    def _get_cohere_model(self):
        """Initialize Cohere model with configuration"""
        try:
            api_key = os.getenv('COHERE_API_KEY')
            if not api_key:
                raise ValueError("Cohere API key not configured")
                
            config = self._get_model_config('cohere')
            return {
                'client': cohere.Client(api_key),
                'config': config
            }
        except Exception as e:
            print(f"Error configuring Cohere model: {str(e)}")
            return None

    def _retry_with_backoff(self, func, *args, **kwargs):
        """Retry function with exponential backoff"""
        max_retries = kwargs.get('max_retries', 3)
        timeout = kwargs.get('timeout', 30)
        
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                wait_time = 2 ** attempt
                print(f"Attempt {attempt + 1} failed: {str(e)}")
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)

    def _format_summary(self, summary_text):
        """Format the summary based on configuration"""
        format_type = os.getenv('SUMMARY_FORMAT', 'markdown').lower()
        max_length = int(os.getenv('MAX_SUMMARY_LENGTH', 1000))
        
        # Truncate if too long
        if len(summary_text) > max_length:
            summary_text = summary_text[:max_length] + "..."
            
        # Format based on configuration
        if format_type == 'markdown':
            formatted = f"# Meeting Summary\n\n{summary_text}"
        elif format_type == 'html':
            formatted = f"<h1>Meeting Summary</h1>\n<p>{summary_text}</p>"
        else:  # plain
            formatted = summary_text
            
        return formatted

    def _generate_summary_prompt(self, meeting_details):
        """Generate the prompt with configuration options"""
        include_action_items = os.getenv('INCLUDE_ACTION_ITEMS', 'true').lower() == 'true'
        include_key_points = os.getenv('INCLUDE_KEY_POINTS', 'true').lower() == 'true'
        include_decisions = os.getenv('INCLUDE_DECISIONS', 'true').lower() == 'true'
        
        prompt = f"Please summarize the following meeting information:\n\n{meeting_details}\n\n"
        
        if include_action_items:
            prompt += "Include a list of action items with responsible parties.\n"
        if include_key_points:
            prompt += "Highlight key discussion points and decisions made.\n"
        if include_decisions:
            prompt += "Clearly mark any important decisions and their implications.\n"
            
        prompt += "Keep the summary concise and focused on the most important information."
        return prompt

    def summarize_meeting(self, meeting_details):
        """Generate a summary using configured AI model with error handling"""
        try:
            model = self.get_ai_model()
            if not model:
                raise ValueError("No valid AI model configured")

            # Prepare prompt with configuration
            prompt = self._generate_summary_prompt(meeting_details)
            config = model['config']

            # Generate summary with retry logic
            if isinstance(model['client'], openai):
                response = self._retry_with_backoff(
                    model['client'].ChatCompletion.create,
                    model=config['model'],
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a professional meeting assistant."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=config['max_tokens'],
                    temperature=config['temperature'],
                    top_p=config['top_p'],
                    timeout=config['timeout'],
                    max_retries=config['max_retries']
                )
                summary = response.choices[0].message.content

            elif isinstance(model['client'], anthropic.Anthropic):
                response = self._retry_with_backoff(
                    model['client'].chat.completions.create,
                    model=config['model'],
                    max_tokens=config['max_tokens'],
                    temperature=config['temperature'],
                    top_p=config['top_p'],
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    timeout=config['timeout'],
                    max_retries=config['max_retries']
                )
                summary = response.content.text

            elif isinstance(model['client'], genai.GenerativeModel):
                response = self._retry_with_backoff(
                    model['client'].generate_content,
                    prompt,
                    max_output_tokens=config['max_output_tokens'],
                    temperature=config['temperature'],
                    top_p=config['top_p'],
                    timeout=config['timeout'],
                    max_retries=config['max_retries']
                )
                summary = response.text[0]

            elif isinstance(model['client'], cohere.Client):
                response = self._retry_with_backoff(
                    model['client'].generate,
                    model=config['model'],
                    prompt=prompt,
                    max_tokens=config['max_tokens'],
                    temperature=config['temperature'],
                    timeout=config['timeout'],
                    max_retries=config['max_retries']
                )
                summary = response.generations[0].text

            elif isinstance(model['client'], pipeline):
                # HuggingFace pipeline
                response = self._retry_with_backoff(
                    model['client'],
                    prompt,
                    max_new_tokens=config['max_tokens'],
                    temperature=config['temperature'],
                    top_p=config['top_p'],
                    top_k=config['top_k'],
                    repetition_penalty=config['repetition_penalty'],
                    do_sample=config['do_sample'],
                    use_cache=config['use_cache'],
                    num_beams=config['num_beams'],
                    max_time=config['max_time'],
                    min_length=config['min_length'],
                    early_stopping=config['early_stopping'],
                    pad_token_id=config['pad_token_id'],
                    eos_token_id=config['eos_token_id'],
                    timeout=config['timeout'],
                    max_retries=config['max_retries']
                )
                summary = response[0]['generated_text']

            elif isinstance(model['client'], openai):
                # Azure OpenAI client
                response = self._retry_with_backoff(
                    model['client'].ChatCompletion.create,
                    engine=config['model'],
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a professional meeting assistant."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=config['max_tokens'],
                    temperature=config['temperature'],
                    top_p=config['top_p'],
                    top_k=config['top_k'],
                    presence_penalty=config['presence_penalty'],
                    frequency_penalty=config['frequency_penalty'],
                    stop=config['stop_sequences'],
                    timeout=config['timeout'],
                    max_retries=config['max_retries']
                )
                summary = response.choices[0].message.content

            elif isinstance(model['client'], boto3.client):
                # SageMaker client
                payload = {
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": config['max_tokens'],
                        "temperature": config['temperature'],
                        "top_p": config['top_p'],
                        "top_k": config['top_k'],
                        "repetition_penalty": config['repetition_penalty'],
                        "do_sample": config['do_sample'],
                        "num_return_sequences": config['num_return_sequences'],
                        "max_time": config['max_time'],
                        "min_length": config['min_length'],
                        "early_stopping": config['early_stopping']
                    }
                }
                
                response = self._retry_with_backoff(
                    model['client'].invoke_endpoint,
                    EndpointName=model['endpoint'],
                    ContentType="application/json",
                    Body=json.dumps(payload),
                    TimeoutInSeconds=config['timeout']
                )
                
                response_body = json.loads(response['Body'].read().decode())
                summary = response_body[0]['generated_text']

            # Format and return the summary
            return self._format_summary(summary)

        except Exception as e:
            print(f"Error generating summary: {str(e)}")
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
