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
Main service class that orchestrates meeting automation tasks.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from src.config.config import Config

class MeetingService:
    """Main service class for meeting automation"""
    
    def __init__(self):
        self.config = Config()
        self.summary_service = SummaryService()
        self.calendar_service = CalendarService()
        self.collaboration_service = CollaborationService()
        
    def process_meeting(self, meeting_id: str) -> Dict:
        """
        Process a meeting by:
        1. Fetching meeting details
        2. Gathering related context
        3. Generating summary
        """
        try:
            # Get meeting details
            meeting = self.calendar_service.get_meeting_details(meeting_id)
            if not meeting:
                return {"error": "Meeting not found"}
                
            # Gather related context
            context = self.collaboration_service.get_meeting_context(meeting)
            
            # Generate summary
            summary = self.summary_service.generate_summary(meeting, context)
            
            return {
                "meeting": meeting,
                "context": context,
                "summary": summary
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_upcoming_meetings(self) -> List[Dict]:
        """Get all upcoming meetings within the next 24 hours"""
        now = datetime.now()
        tomorrow = now + timedelta(days=1)
        return self.calendar_service.get_meetings_between(now, tomorrow)
    
    def get_meeting_summary(self, meeting_id: str) -> Dict:
        """Generate summary for a specific meeting"""
        meeting = self.calendar_service.get_meeting_details(meeting_id)
        if not meeting:
            return {"error": "Meeting not found"}
            
        return self.summary_service.generate_summary(meeting)
    
    def search_meeting_context(self, meeting_id: str) -> Dict:
        """Search for context related to a meeting"""
        meeting = self.calendar_service.get_meeting_details(meeting_id)
        if not meeting:
            return {"error": "Meeting not found"}
            
        return self.collaboration_service.get_meeting_context(meeting)
