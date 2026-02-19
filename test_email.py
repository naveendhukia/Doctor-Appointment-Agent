import os
from dotenv import load_dotenv
from src.mcp_tools.email_tool import EmailTool

load_dotenv()

print("Testing Gmail connection...")
print("=" * 50)

email_tool = EmailTool()

if email_tool.enabled:
    # Test connection
    success, message = email_tool.test_connection()
    
    if success:
        print(f"✅ Gmail connection works!")
        
        # Send test email to yourself
        print("\nSending test email...")
        result = email_tool.send_confirmation(
            to_email=os.getenv("GMAIL_USER"),  # Send to yourself
            patient_name="Naveen Dhukia",
            doctor_name="Dr. Ahuja",
            appointment_time="Monday, February 17, 2026 at 10:00 AM"
        )
        
        if result:
            print("✅ Test email sent! Check your inbox.")
        else:
            print("❌ Email sending failed")
    else:
        print(f"❌ Connection failed: {message}")
else:
    print("❌ Gmail not configured in .env file")
    print("Add GMAIL_USER and GMAIL_APP_PASSWORD to .env")