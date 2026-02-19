import os
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build

class CalendarTool:
    def __init__(self):
        SCOPES = ['https://www.googleapis.com/auth/calendar']
        credentials_file = os.getenv("GOOGLE_CREDENTIALS_FILE")
        
        # Calendar ID = your Gmail (the calendar you shared with the service account)
        self.calendar_id = os.getenv("GOOGLE_CALENDAR_ID")
        
        # Build full path
        if not credentials_file.startswith('/'):
            credentials_file = os.path.join(
                os.path.dirname(__file__), 
                '..', 
                '..', 
                credentials_file
            )
        
        if os.path.exists(credentials_file):
            try:
                creds = service_account.Credentials.from_service_account_file(
                    credentials_file, scopes=SCOPES)
                self.service = build('calendar', 'v3', credentials=creds)
                self.enabled = True
                print(f"✅ Google Calendar integration enabled")
            except Exception as e:
                print(f"⚠️  Google Calendar setup failed: {e}")
                self.enabled = False
        else:
            print(f"⚠️  Google Calendar not configured - file not found: {credentials_file}")
            self.enabled = False
    
    def create_event(self, doctor_email: str, patient_name: str, 
                     patient_email: str, start_time_iso: str, duration: int = 30):
        """Create a calendar event"""
        if not self.enabled:
            print("⚠️  Calendar event skipped (not configured)")
            return None
        
        try:
            start = datetime.fromisoformat(start_time_iso)
            end = start + timedelta(minutes=duration)
            
            event = {
                'summary': f'📅 Appointment: {patient_name}',
                'description': f'Medical appointment with {patient_name}\n\nPatient Email: {patient_email}\nDoctor Email: {doctor_email}',
                'start': {
                    'dateTime': start.isoformat(),
                    'timeZone': 'Asia/Kolkata',
                },
                'end': {
                    'dateTime': end.isoformat(),
                    'timeZone': 'Asia/Kolkata',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},
                        {'method': 'popup', 'minutes': 30},
                    ],
                },
                'colorId': '2',  # Green color for appointments
            }
            
            event_result = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event
            ).execute()
            
            event_id = event_result.get('id')
            event_link = event_result.get('htmlLink')
            
            print(f"✅ Calendar event created: {event_link}")
            return event_id
            
        except Exception as e:
            print(f"⚠️  Calendar event creation failed: {e}")
            return None
    
    def test_connection(self):
        """Test if Google Calendar connection works"""
        if not self.enabled:
            return False, "Calendar not configured"
        
        try:
            # Try to list events on the shared calendar (more reliable than calendars().get)
            now = datetime.utcnow().isoformat() + 'Z'
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=now,
                maxResults=1,
                singleEvents=True
            ).execute()
            return True, f"Connected to calendar: {self.calendar_id}"
                
        except Exception as e:
            error_msg = str(e)
            if '404' in error_msg:
                return False, (
                    f"Cannot access calendar '{self.calendar_id}'. "
                    f"Please share your Google Calendar with:\n"
                    f"   appointment-scheduler@dulcet-streamer-487813-b3.iam.gserviceaccount.com\n"
                    f"   (Permission: 'Make changes to events')"
                )
            return False, error_msg