from dotenv import load_dotenv
from src.mcp_tools.database import DatabaseTool

load_dotenv()

print("Testing database connection...")
try:
    db = DatabaseTool()
    print("✅ Database connected successfully!")
    
    # Test getting a doctor
    result = db.get_doctor_by_name("Dr. Ahuja")
    if result:
        print(f"✅ Found doctor: {result['name']} - {result['specialization']}")
    else:
        print("❌ Doctor not found - check if you ran the SQL insert statements")
    
    db.close()
    print("\n✅ All tests passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nTroubleshooting:")
    print("1. Check PostgreSQL is running")
    print("2. Verify .env file has correct DB_PASSWORD")
    print("3. Ensure 'appointments' database exists")