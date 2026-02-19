import os
import sys
from datetime import datetime, timedelta

# Fix path
project_root = '/Users/naveendhukia876/Desktop/claudeji'
sys.path.insert(0, project_root)
os.chdir(project_root)

# Load environment
from dotenv import load_dotenv
load_dotenv(os.path.join(project_root, '.env'))

# Point to the actual service account key location
os.environ['GOOGLE_CREDENTIALS_FILE'] = '/Users/naveendhukia876/Desktop/claudeji/doctor-appointment-agent/service-account-key.json'

# Now import
from src.mcp_tools.calendar_tool import CalendarTool

print("Testing Google Calendar Integration...")
print("=" * 60)

# Check if service account file exists
service_account_file = os.environ['GOOGLE_CREDENTIALS_FILE']
if os.path.exists(service_account_file):
    print(f"✅ Service account file found")
else:
    print(f"❌ Service account file NOT found at: {service_account_file}")
    print("\nPlease:")
    print("1. Download JSON key from Google Cloud Console")
    print("2. Save it as: service-account-key.json")
    print("3. Place it in: /Users/naveendhukia876/Desktop/claudeji/doctor-appointment-agent/")
    sys.exit(1)

print("=" * 60)

calendar_tool = CalendarTool()

if calendar_tool.enabled:
    # Test connection
    print("\n🔧 Testing Google Calendar connection...")
    success, message = calendar_tool.test_connection()
    print(f"Result: {message}")
    
    if success:
        print("\n📅 Creating test event...")
        
        # Create test event for tomorrow at 10 AM
        tomorrow = datetime.now() + timedelta(days=1)
        tomorrow_10am = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
        
        event_id = calendar_tool.create_event(
            doctor_email="doctor@example.com",
            patient_name="Naveen Dhukia (Test)",
            patient_email="naveen876.moodi@gmail.com",
            start_time_iso=tomorrow_10am.isoformat(),
            duration=30
        )
        
        if event_id:
            print(f"\n✅ SUCCESS! Test event created!")
            print(f"   Event ID: {event_id}")
            print(f"\n🎉 Check your Google Calendar:")
            print(f"   Date: {tomorrow.strftime('%A, %B %d, %Y')}")
            print(f"   Time: 10:00 AM")
            print(f"   Title: 📅 Appointment: Naveen Dhukia (Test)")
        else:
            print("\n❌ Event creation failed")
            print("Check that you:")
            print("1. Shared your calendar with the service account")
            print("2. Gave 'Make changes to events' permission")
    else:
        print(f"\n❌ Connection failed: {message}")
        print("\nTroubleshooting:")
        print("1. Check service-account-key.json is valid JSON")
        print("2. Enable Google Calendar API in Cloud Console")
        print("3. Wait a few minutes after enabling API")
else:
    print("\n❌ Google Calendar not configured")
    print("\nNext steps:")
    print("1. Create Google Cloud Project")
    print("2. Enable Google Calendar API")
    print("3. Create Service Account")
    print("4. Download JSON key as service-account-key.json")
    print("5. Share your calendar with service account email")