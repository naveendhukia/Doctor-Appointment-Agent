import sys
import os

# Set paths
project_root = '/Users/naveendhukia876/Desktop/claudeji'
sys.path.insert(0, project_root)
os.chdir(project_root)

# Load .env explicitly
from dotenv import load_dotenv
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path)

# Debug: Check if values loaded
print("Testing Slack Integration...")
print("=" * 60)
print(f"SLACK_BOT_TOKEN: {'SET ✅' if os.getenv('SLACK_BOT_TOKEN') else '❌ NOT SET'}")
print(f"SLACK_CHANNEL_ID: {'SET ✅' if os.getenv('SLACK_CHANNEL_ID') else '❌ NOT SET'}")
print("=" * 60)

from src.mcp_tools.slack_tool import SlackTool
from src.mcp_tools.analytics_tool import AnalyticsTool

slack = SlackTool()

if slack.enabled:
    # Test connection
    print("\n🔧 Testing Slack connection...")
    success, message = slack.test_connection()
    print(f"Result: {message}")
    
    if success:
        print("\n📤 Sending test report to Slack...")
        
        # Generate report
        analytics = AnalyticsTool()
        report = analytics.generate_summary_report()
        analytics.close()
        
        # Send to Slack
        result = slack.send_report(
            report_title="Test Doctor Summary Report",
            report_content=report
        )
        
        if result:
            print("✅ Report sent! Check your Slack channel.")
        else:
            print("❌ Failed to send report")
    else:
        print(f"❌ Connection failed: {message}")
        print("\nTroubleshooting:")
        print("1. Check bot token is correct (starts with xoxb-)")
        print("2. Check channel ID is correct")
        print("3. Make sure bot is invited to the channel")
else:
    print("\n❌ Slack not configured")
    print("\nCurrent values:")
    print(f"  SLACK_BOT_TOKEN: {os.getenv('SLACK_BOT_TOKEN', 'NOT SET')[:20]}...")
    print(f"  SLACK_CHANNEL_ID: {os.getenv('SLACK_CHANNEL_ID', 'NOT SET')}")
    print("\nMake sure your .env has:")
    print("  SLACK_BOT_TOKEN=xoxb-your-token")
    print("  SLACK_CHANNEL_ID=C01234ABC56")