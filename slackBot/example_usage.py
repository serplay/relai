#!/usr/bin/env python3
"""
Example usage of the Slack Bot API endpoint for creating tasks from natural language.
"""

import requests
import json

# Configuration
API_BASE_URL = "http://localhost:8000"  # Adjust this to your server URL
SLACK_BOT_ENDPOINT = f"{API_BASE_URL}/slack-bot"

def create_task_from_natural_language(task_description, channel=None):
    """
    Create a Slack task from natural language description.
    
    Args:
        task_description (str): Natural language task description
        channel (str, optional): Slack channel to send to (defaults to configured channel)
    
    Returns:
        dict: API response
    """
    endpoint = f"{SLACK_BOT_ENDPOINT}/create-task"
    
    payload = {
        "task": task_description
    }
    
    if channel:
        payload["channel"] = channel
    
    try:
        response = requests.post(endpoint, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return None

def check_slack_status():
    """Check if Slack integration is working."""
    endpoint = f"{SLACK_BOT_ENDPOINT}/status"
    
    try:
        response = requests.get(endpoint)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error checking status: {e}")
        return None

def main():
    """Example usage of the Slack Bot API."""
    
    print("🤖 Slack Bot Task Creator Example")
    print("=" * 40)
    
    # Check Slack status first
    print("\n1. Checking Slack connection...")
    status = check_slack_status()
    if status:
        if status["connected"]:
            print(f"✅ {status['message']}")
        else:
            print(f"❌ {status['message']}")
            print("   Please check your Slack configuration before proceeding.")
    else:
        print("❌ Could not check Slack status")
    
    # Example tasks
    example_tasks = [
        "Remind Alex to review Q3 numbers by Friday and provide a summary",
        "Ask Sarah to prepare the monthly report for next Monday",
        "Tell John to update the project timeline by tomorrow",
        "Ask the team to review the new feature proposal by Wednesday"
    ]
    
    print("\n2. Creating example tasks...")
    
    for i, task in enumerate(example_tasks, 1):
        print(f"\n--- Example {i} ---")
        print(f"Task: {task}")
        
        result = create_task_from_natural_language(task)
        
        if result:
            if result["success"]:
                print(f"✅ {result['message']}")
                if result["slack_sent"]:
                    print("📤 Message sent to Slack successfully!")
                else:
                    print("⚠️  Task parsed but not sent to Slack")
                
                # Show parsed task details
                if result["parsed_task"]:
                    parsed = result["parsed_task"]
                    print(f"   Recipient: {parsed.get('recipient', 'Unknown')}")
                    print(f"   Due Date: {parsed.get('due_date', 'Unknown')}")
                    print(f"   Response Required: {parsed.get('response_required', False)}")
            else:
                print(f"❌ Failed: {result.get('message', 'Unknown error')}")
        else:
            print("❌ Failed to make API request")
    
    print("\n3. Interactive mode")
    print("Enter your own task descriptions (or 'quit' to exit):")
    
    while True:
        try:
            user_input = input("\nEnter task: ").strip()
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            if user_input:
                result = create_task_from_natural_language(user_input)
                if result and result["success"]:
                    print(f"✅ {result['message']}")
                else:
                    print("❌ Failed to create task")
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break

if __name__ == "__main__":
    main() 