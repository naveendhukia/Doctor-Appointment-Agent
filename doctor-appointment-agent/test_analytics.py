import sys
sys.path.insert(0, '/Users/naveendhukia876/Desktop/claudeji')

from dotenv import load_dotenv
from src.mcp_tools.analytics_tool import AnalyticsTool

load_dotenv()

print("Testing Analytics Tool...")
print("=" * 60)

analytics = AnalyticsTool()

# Test 1: Today's appointments
print("\n📅 Today's Appointments:")
result = analytics.get_today_appointments()
print(f"  Count: {result['count']}")

# Test 2: Tomorrow's appointments  
print("\n📅 Tomorrow's Appointments:")
result = analytics.get_tomorrow_appointments()
print(f"  Count: {result['count']}")

# Test 3: Yesterday's visits
print("\n📅 Yesterday's Unique Patients:")
result = analytics.get_yesterday_visits()
print(f"  Count: {result['unique_patients']}")

# Test 4: Summary report
print("\n📊 Full Summary Report:")
print("-" * 60)
report = analytics.generate_summary_report()
print(report)

analytics.close()
print("\n✅ Analytics test complete!")