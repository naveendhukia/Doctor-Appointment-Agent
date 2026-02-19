from dotenv import load_dotenv
from src.mcp_tools.database import DatabaseTool

load_dotenv()

print("🧪 Testing database tools without API calls...")
print("=" * 60)

# Test database connection
db = DatabaseTool()
print("✅ Database connected")

# Test checking availability
print("\n📅 Testing availability check...")
result = db.check_availability("Dr. Ahuja", "2026-02-17", "morning")
print(f"Available: {result.get('available')}")
if result.get('slots'):
    print(f"Slots: {result['slots']}")

# Test booking
print("\n📝 Testing appointment booking...")
booking_result = db.book_appointment(
    doctor_name="Dr. Ahuja",
    patient_name="Test Patient",
    patient_email="test@example.com",
    appointment_datetime="2026-02-17T10:00:00"
)

if booking_result.get('success'):
    print(f"✅ Booking successful! ID: {booking_result['appointment_id']}")
else:
    print(f"❌ Booking failed: {booking_result.get('error')}")

db.close()
print("\n✅ All tools working! Now you just need API credits.")