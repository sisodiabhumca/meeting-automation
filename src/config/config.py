# Copyright (c) 2025 Sisodia Bhumca, Inc.
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""
Configuration management for the Meeting Automation Assistant.
Handles all environment variables and configuration settings.
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration manager for the application"""
    
    def __init__(self):
        # AI Model Configuration
        self.ai_model = os.getenv('DEFAULT_AI_MODEL', 'openai').lower()
        self.model_config = self._get_ai_model_config()
        
        # Calendar Configuration
        self.calendar_config = self._get_calendar_config()
        
        # Collaboration Tools Configuration
        self.collaboration_config = self._get_collaboration_config()
        
        # Summary Preferences
        self.summary_format = os.getenv('SUMMARY_FORMAT', 'markdown').lower()
        self.max_summary_length = int(os.getenv('MAX_SUMMARY_LENGTH', 1000))
        self.include_action_items = os.getenv('INCLUDE_ACTION_ITEMS', 'true').lower() == 'true'
        self.include_key_points = os.getenv('INCLUDE_KEY_POINTS', 'true').lower() == 'true'
        self.include_decisions = os.getenv('INCLUDE_DECISIONS', 'true').lower() == 'true'
        
    def _get_ai_model_config(self):
        """Get configuration for the selected AI model"""
        model_type = self.ai_model
        config = {}
        
        # Common settings
        config['max_retries'] = int(os.getenv(f'{model_type.upper()}_MAX_RETRIES', 3))
        config['timeout'] = int(os.getenv(f'{model_type.upper()}_TIMEOUT', 30))
        
        # Model-specific settings
        if model_type == 'openai':
            config['api_key'] = os.getenv('OPENAI_API_KEY')
            config['model'] = os.getenv('OPENAI_MODEL', 'gpt-4')
        elif model_type == 'anthropic':
            config['api_key'] = os.getenv('ANTHROPIC_API_KEY')
            config['model'] = os.getenv('ANTHROPIC_MODEL', 'claude-3-sonnet-20240229')
        
        return config
    
    def _get_calendar_config(self):
        """Get calendar service configuration"""
        config = {}
        
        # Google Calendar
        config['google_enabled'] = bool(os.getenv('GOOGLE_CALENDAR_ENABLED', 'true'))
        config['google_credentials_file'] = os.getenv('GOOGLE_CREDENTIALS_FILE')
        config['google_token_file'] = os.getenv('GOOGLE_TOKEN_FILE')
        
        # Microsoft Outlook
        config['outlook_enabled'] = bool(os.getenv('OUTLOOK_CALENDAR_ENABLED', 'true'))
        config['ms_client_id'] = os.getenv('MS_CLIENT_ID')
        config['ms_client_secret'] = os.getenv('MS_CLIENT_SECRET')
        config['ms_tenant_id'] = os.getenv('MS_TENANT_ID')
        
        return config
    
    def _get_collaboration_config(self):
        """Get collaboration tool configuration"""
        config = {}
        
        # Slack
        config['slack_enabled'] = bool(os.getenv('SLACK_ENABLED', 'true'))
        config['slack_bot_token'] = os.getenv('SLACK_BOT_TOKEN')
        config['slack_app_token'] = os.getenv('SLACK_APP_TOKEN')
        
        # Microsoft Teams
        config['teams_enabled'] = bool(os.getenv('TEAMS_ENABLED', 'true'))
        config['teams_token'] = os.getenv('TEAMS_TOKEN')
        
        return config
