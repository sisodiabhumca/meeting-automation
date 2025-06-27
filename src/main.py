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
Main entry point for the Meeting Automation Assistant.
"""

import argparse
from src.services.meeting_service import MeetingService

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Meeting Automation Assistant - Manage and summarize your meetings')
    
    parser.add_argument(
        '--meeting-id',
        help='Process a specific meeting by ID')
    parser.add_argument(
        '--list',
        action='store_true',
        help='List upcoming meetings')
    parser.add_argument(
        '--summary',
        action='store_true',
        help='Generate summary for a meeting')
    
    args = parser.parse_args()
    service = MeetingService()
    
    if args.list:
        meetings = service.get_upcoming_meetings()
        print("\nUpcoming Meetings:")
        for meeting in meetings:
            print(f"\nTitle: {meeting.get('title', 'No title')}")
            print(f"Time: {meeting.get('start_time')}")
            print(f"Attendees: {', '.join(meeting.get('attendees', []))}")
            print(f"ID: {meeting.get('id')}")
    
    elif args.meeting_id:
        if args.summary:
            result = service.get_meeting_summary(args.meeting_id)
            print("\nMeeting Summary:")
            print(result.get('summary', 'Failed to generate summary'))
        else:
            result = service.process_meeting(args.meeting_id)
            print("\nMeeting Details:")
            print(result)
    
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
