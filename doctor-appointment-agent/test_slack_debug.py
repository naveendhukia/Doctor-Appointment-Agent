import sys
sys.path.insert(0, '/Users/naveendhukia876/Desktop/claudeji')

import os
from dotenv import load_dotenv
load_dotenv('/Users/naveendhukia876/Desktop/claudeji/.env')

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

token = os.getenv('SLACK_BOT_TOKEN')
channel = os.getenv('SLACK_CHANNEL_ID')

print(f"Token: {token[:10]}...")
print(f"Channel ID: {channel}")
print(f"Channel type: {'DM' if channel.startswith('D') else 'Channel' if channel.startswith('C') else 'Group'}")

client = WebClient(token=token)

# Step 1: Test auth
print("\n--- Step 1: Auth Test ---")
try:
    auth = client.auth_test()
    print(f"✅ Bot: {auth['user']} | Team: {auth['team']}")
except SlackApiError as e:
    print(f"❌ Auth failed: {e.response['error']}")
    exit(1)

# Step 2: Test sending
print("\n--- Step 2: Send Test ---")
try:
    resp = client.chat_postMessage(channel=channel, text="🔧 Test from Doctor Appointment Bot")
    print(f"✅ Message sent! (ts: {resp['ts']})")
except SlackApiError as e:
    error = e.response['error']
    print(f"❌ Send failed: {error}")
    if error == 'not_in_channel':
        print("FIX: Type /invite @YourBotName in the Slack channel")
    elif error == 'channel_not_found':
        print("FIX: Channel ID is wrong. Get the correct one from Slack channel details.")
    elif error == 'invalid_auth':
        print("FIX: Bot token is invalid. Regenerate it in Slack API dashboard.")
