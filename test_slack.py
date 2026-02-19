import sys
sys.path.insert(0, '/Users/naveendhukia876/Desktop/claudeji')

from dotenv import load_dotenv
from src.mcp_tools.slack_tool import SlackTool
from src.mcp_tools.analytics_tool import AnalyticsTool

load_dotenv()

print("Testing Slack Integration...")
print("=" * 60)

slack = SlackTool()

if slack.enabled:
    # Test connection
    success, message = slack.test_connection()
    print(f"Connection: {message}")
    
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
    print("❌ Slack not configured")
    print("Add SLACK_BOT_TOKEN and SLACK_CHANNEL_ID to .env")