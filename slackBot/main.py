import os
import sys
from dotenv import load_dotenv
from llm_parser import parse_task
from slack_interface import get_user_input, send_to_slack, test_slack_connection, start_socket_mode_client, handle_socket_mode_events

# Load environment variables from .env file
load_dotenv()

def main():
    """
    Simple TaskPilot AI - LLM parsing and Slack bot integration
    """
    print("🤖 TaskPilot AI - Simple LLM + Slack Bot")
    print("="*50)
    
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "socket":
        run_socket_mode()
        return
    
    # Check if OpenAI API key is available
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print(f"✅ OpenAI API Key: {'*' * (len(api_key) - 8) + api_key[-8:]}")
    else:
        print("❌ OpenAI API Key: Not found (will use stub parser)")
    
    # Test Slack connection
    print("\n🔗 Testing Slack connection...")
    slack_connected = test_slack_connection()
    
    # Get task from user
    raw_input = get_user_input()
    print(f"\n📝 Received: {raw_input}")
    
    # Parse with LLM
    print("\n🧠 Parsing task with LLM...")
    parsed = parse_task(raw_input)
    print(f"✅ Parsed: {parsed}")
    
    # Send to Slack
    print("\n📱 Sending to Slack...")
    send_to_slack(parsed)
    
    print("\n✅ Task processed successfully!")

def run_socket_mode():
    """
    Run TaskPilot AI in Socket Mode for real-time Slack integration
    """
    print("🔌 Starting TaskPilot AI in Socket Mode...")
    
    # Check environment variables
    api_key = os.getenv('OPENAI_API_KEY')
    bot_token = os.getenv('SLACK_BOT_TOKEN')
    app_token = os.getenv('SLACK_APP_TOKEN')
    
    if not all([api_key, bot_token, app_token]):
        print("❌ Missing required environment variables for Socket Mode")
        print("   Required: OPENAI_API_KEY, SLACK_BOT_TOKEN, SLACK_APP_TOKEN")
        return
    
    print(f"✅ OpenAI API Key: {'*' * (len(api_key) - 8) + api_key[-8:]}")
    print(f"✅ Slack Bot Token: {'*' * (len(bot_token) - 8) + bot_token[-8:]}")
    print(f"✅ Slack App Token: {app_token[:10]}...")
    
    # Initialize Socket Mode client
    client = start_socket_mode_client()
    if not client:
        print("❌ Failed to initialize Socket Mode client")
        return
    
    # Set up event handlers
    handle_socket_mode_events(client)
    
    print("\n🎧 TaskPilot AI is now listening for Slack events...")
    print("   Press Ctrl+C to stop")
    
    try:
        # Start the Socket Mode client
        client.connect()
    except KeyboardInterrupt:
        print("\n👋 Shutting down Socket Mode client...")
        client.close()
    except Exception as e:
        print(f"❌ Error in Socket Mode: {e}")
        client.close()

if __name__ == "__main__":
    main() 