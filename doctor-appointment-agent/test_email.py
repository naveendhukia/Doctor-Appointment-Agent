import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load .env manually
def load_env():
    env_path = '/Users/naveendhukia876/Desktop/claudeji/doctor-appointment-agent/.env'
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
    else:
        print(f"❌ .env file not found at: {env_path}")

load_env()

print("Testing Gmail Setup...")
print("=" * 50)

gmail_user = os.getenv("GMAIL_USER", "")
gmail_pass = os.getenv("GMAIL_APP_PASSWORD", "")

print(f"GMAIL_USER     : {gmail_user if gmail_user else '❌ NOT SET'}")
print(f"GMAIL_PASSWORD : {'✅ SET' if gmail_pass else '❌ NOT SET'}")
print("=" * 50)

if not gmail_user or not gmail_pass:
    print("\n❌ Gmail credentials missing!")
    print("Open your .env file and add:")
    print("  GMAIL_USER=your_email@gmail.com")
    print("  GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx")
    sys.exit(1)

# Test Connection
print("\n🔧 Testing SMTP connection...")
try:
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(gmail_user, gmail_pass)
    print("✅ SMTP Connection successful!")
except smtplib.SMTPAuthenticationError:
    print("❌ Authentication failed!")
    print("   Make sure you're using an App Password, not your regular password")
    print("   Get one at: https://myaccount.google.com/apppasswords")
    sys.exit(1)
except Exception as e:
    print(f"❌ Connection failed: {e}")
    sys.exit(1)

# Send Test Email
print("\n📧 Sending test email to yourself...")

message = MIMEMultipart("alternative")
message["Subject"] = "✅ Test - Doctor Appointment Agent"
message["From"] = gmail_user
message["To"] = gmail_user

html = """
<html>
<body style="font-family: Arial, sans-serif; padding: 20px;">
    <div style="max-width: 500px; margin: 0 auto; background: white; 
                border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); 
                overflow: hidden;">
        
        <div style="background: linear-gradient(135deg, #1e3a8a, #2563eb); 
                    color: white; padding: 24px; text-align: center;">
            <h1 style="margin: 0; font-size: 22px;">🏥 Doctor Appointment System</h1>
            <p style="margin: 8px 0 0; opacity: 0.9;">Email Test Successful!</p>
        </div>
        
        <div style="padding: 24px;">
            <div style="background: #dcfce7; border: 2px solid #86efac; 
                        border-radius: 8px; padding: 16px; text-align: center;
                        color: #166534; font-size: 18px; font-weight: bold;">
                ✅ Appointment Confirmed!
            </div>
            
            <div style="margin-top: 20px; background: #f8fafc; 
                        border-radius: 8px; padding: 16px;">
                <p><strong>👨‍⚕️ Doctor:</strong> Dr. Ahuja</p>
                <p><strong>👤 Patient:</strong> Naveen Dhukia</p>
                <p><strong>📅 Time:</strong> Monday, Feb 17, 2026 at 10:00 AM</p>
            </div>
            
            <div style="margin-top: 20px; background: #fffbeb; 
                        border-radius: 8px; padding: 16px;">
                <p style="color: #92400e; font-weight: bold;">⚠️ Reminders:</p>
                <ul style="color: #78350f;">
                    <li>Arrive 10 minutes early</li>
                    <li>Bring medical records</li>
                    <li>Bring valid ID</li>
                </ul>
            </div>
        </div>
        
        <div style="background: #f8fafc; padding: 16px; text-align: center; 
                    color: #94a3b8; font-size: 12px;">
            Doctor Appointment Scheduling System
        </div>
    </div>
</body>
</html>
"""

text = """
Appointment Confirmed!
Doctor: Dr. Ahuja
Patient: Naveen Dhukia
Time: Monday, Feb 17, 2026 at 10:00 AM

Reminders:
- Arrive 10 minutes early
- Bring medical records
- Bring valid ID
"""

message.attach(MIMEText(text, "plain"))
message.attach(MIMEText(html, "html"))

try:
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(gmail_user, gmail_pass)
        server.sendmail(gmail_user, gmail_user, message.as_string())
    
    print(f"✅ Email sent to {gmail_user}")
    print("\n🎉 Check your inbox now!")
    print("=" * 50)
    print("✅ Gmail integration is working perfectly!")
    print("   Your app will now send emails when appointments are booked.")

except Exception as e:
    print(f"❌ Failed to send email: {e}")