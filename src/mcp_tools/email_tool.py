import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

class EmailTool:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = os.getenv("GMAIL_USER")
        self.sender_password = os.getenv("GMAIL_APP_PASSWORD")
        self.enabled = bool(self.sender_email and self.sender_password)
        
        if not self.enabled:
            print("⚠️  Gmail not configured - skipping email notifications")
        else:
            print(f"✅ Email notifications enabled ({self.sender_email})")
    
    def send_confirmation(self, to_email: str, patient_name: str,
                         doctor_name: str, appointment_time: str):
        """Send appointment confirmation email"""
        if not self.enabled:
            print(f"⚠️  Email skipped (not configured)")
            return False
        
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = f"✅ Appointment Confirmed - {doctor_name}"
            message["From"] = f"Doctor Appointment Agent <{self.sender_email}>"
            message["To"] = to_email
            
            # Plain text version
            text = f"""
Dear {patient_name},

Your appointment has been successfully confirmed!

━━━━━━━━━━━━━━━━━━━━━━━━━━━
APPOINTMENT DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Doctor  : {doctor_name}
Patient : {patient_name}
Time    : {appointment_time}
━━━━━━━━━━━━━━━━━━━━━━━━━━━

Important Reminders:
- Please arrive 10 minutes early
- Bring any previous medical records
- Bring a valid ID

If you need to reschedule or cancel, please contact us.

Thank you,
Doctor Appointment Scheduling System
            """
            
            # HTML version
            html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f0f2f5;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #1e3a8a, #2563eb);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
        }}
        .header p {{
            margin: 8px 0 0;
            opacity: 0.9;
        }}
        .success-badge {{
            background: #dcfce7;
            border: 2px solid #86efac;
            border-radius: 50px;
            padding: 12px 24px;
            text-align: center;
            margin: 24px;
            color: #166534;
            font-size: 18px;
            font-weight: bold;
        }}
        .details-card {{
            margin: 0 24px 24px;
            background: #f8fafc;
            border-radius: 12px;
            padding: 24px;
            border: 1px solid #e2e8f0;
        }}
        .details-card h2 {{
            color: #1e293b;
            font-size: 16px;
            margin: 0 0 16px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #64748b;
        }}
        .detail-row {{
            display: flex;
            padding: 10px 0;
            border-bottom: 1px solid #e2e8f0;
        }}
        .detail-row:last-child {{
            border-bottom: none;
        }}
        .detail-label {{
            font-weight: bold;
            color: #475569;
            width: 100px;
            flex-shrink: 0;
        }}
        .detail-value {{
            color: #1e293b;
        }}
        .reminders {{
            margin: 0 24px 24px;
            padding: 20px;
            background: #fffbeb;
            border-radius: 12px;
            border: 1px solid #fde68a;
        }}
        .reminders h3 {{
            color: #92400e;
            margin: 0 0 12px;
            font-size: 14px;
        }}
        .reminders ul {{
            margin: 0;
            padding-left: 20px;
            color: #78350f;
        }}
        .reminders li {{
            margin-bottom: 6px;
            font-size: 14px;
        }}
        .footer {{
            background: #f8fafc;
            padding: 20px;
            text-align: center;
            color: #94a3b8;
            font-size: 12px;
            border-top: 1px solid #e2e8f0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>🏥 Doctor Appointment System</h1>
            <p>Your appointment has been confirmed</p>
        </div>
        
        <!-- Success Badge -->
        <div class="success-badge">
            ✅ Appointment Confirmed!
        </div>
        
        <!-- Appointment Details -->
        <div class="details-card">
            <h2>Appointment Details</h2>
            <div class="detail-row">
                <span class="detail-label">👨‍⚕️ Doctor</span>
                <span class="detail-value">{doctor_name}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">👤 Patient</span>
                <span class="detail-value">{patient_name}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">📅 Date & Time</span>
                <span class="detail-value">{appointment_time}</span>
            </div>
        </div>
        
        <!-- Reminders -->
        <div class="reminders">
            <h3>⚠️ Important Reminders</h3>
            <ul>
                <li>Please arrive 10 minutes early</li>
                <li>Bring any previous medical records</li>
                <li>Bring a valid ID</li>
                <li>Contact us if you need to reschedule</li>
            </ul>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            <p>This is an automated confirmation email.</p>
            <p>Doctor Appointment Scheduling System</p>
        </div>
    </div>
</body>
</html>
            """
            
            part1 = MIMEText(text, "plain")
            part2 = MIMEText(html, "html")
            message.attach(part1)
            message.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(
                    self.sender_email,
                    to_email,
                    message.as_string()
                )
            
            print(f"✅ Confirmation email sent to {to_email}")
            return True
            
        except smtplib.SMTPAuthenticationError:
            print("❌ Gmail authentication failed!")
            print("   Check your GMAIL_USER and GMAIL_APP_PASSWORD in .env")
            return False
        except smtplib.SMTPException as e:
            print(f"❌ SMTP error: {e}")
            return False
        except Exception as e:
            print(f"❌ Email error: {e}")
            return False
    
    def test_connection(self):
        """Test if Gmail connection works"""
        if not self.enabled:
            return False, "Gmail not configured"
        
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
            return True, "Connection successful"
        except smtplib.SMTPAuthenticationError:
            return False, "Authentication failed - check credentials"
        except Exception as e:
            return False, str(e)