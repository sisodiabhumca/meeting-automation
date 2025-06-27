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
Service for generating meeting summaries using AI models.
"""

from typing import Dict, Optional
from src.config.config import Config
from src.models.ai_models import AIModelFactory

class SummaryService:
    """Service for generating meeting summaries"""
    
    def __init__(self):
        self.config = Config()
        self.ai_model = AIModelFactory.get_model(self.config.ai_model)
        
    def generate_summary(self, meeting: Dict, context: Optional[Dict] = None) -> str:
        """
        Generate a summary for a meeting with optional context.
        
        Args:
            meeting: Meeting details dictionary
            context: Optional context information (emails, messages, etc.)
            
        Returns:
            Formatted summary string
        """
        try:
            # Prepare the prompt
            prompt = self._create_summary_prompt(meeting, context)
            
            # Generate summary using AI model
            summary = self.ai_model.generate(prompt)
            
            # Format the summary based on preferences
            formatted_summary = self._format_summary(summary)
            
            return formatted_summary
            
        except Exception as e:
            return f"Error generating summary: {str(e)}"
    
    def _create_summary_prompt(self, meeting: Dict, context: Optional[Dict]) -> str:
        """Create the prompt for AI model"""
        prompt = f"Meeting Summary Request:\n\n"
        prompt += f"Title: {meeting.get('title', 'No title')}\n"
        prompt += f"Date: {meeting.get('date', 'Unknown')}\n"
        prompt += f"Attendees: {', '.join(meeting.get('attendees', []))}\n\n"
        
        if context:
            prompt += "Related Context:\n"
            if context.get('emails'):
                prompt += "Emails:\n"
                for email in context['emails']:
                    prompt += f"- {email['subject']}\n"
            if context.get('messages'):
                prompt += "Messages:\n"
                for msg in context['messages']:
                    prompt += f"- {msg['content']}\n"
        
        prompt += "\nPlease create a summary that includes:\n"
        if self.config.include_action_items:
            prompt += "- Action items with responsible parties\n"
        if self.config.include_key_points:
            prompt += "- Key discussion points\n"
        if self.config.include_decisions:
            prompt += "- Important decisions and their implications\n"
        
        return prompt
    
    def _format_summary(self, summary: str) -> str:
        """Format the summary based on configuration"""
        if self.config.summary_format == 'markdown':
            formatted = f"# Meeting Summary\n\n{summary}"
        elif self.config.summary_format == 'html':
            formatted = f"<h1>Meeting Summary</h1>\n<p>{summary}</p>"
        else:  # plain
            formatted = summary
            
        # Truncate if too long
        if len(formatted) > self.config.max_summary_length:
            formatted = formatted[:self.config.max_summary_length] + "..."
            
        return formatted
