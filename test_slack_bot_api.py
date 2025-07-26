#!/usr/bin/env python3
"""
Test script for the Slack Bot API endpoint.
"""

import requests
import json
import time

# Configuration
API_BASE_URL = "http://localhost:8000"
SLACK_BOT_ENDPOINT = f"{API_BASE_URL}/slack-bot"

def test_health_check():
    """Test if the server is running."""
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Server is running")
            return True
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on http://localhost:8000")
        return False

def test_slack_status():
    """Test Slack connection status."""
    try:
        response = requests.get(f"{SLACK_BOT_ENDPOINT}/status")
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Slack Status: {data['message']}")
            return data['connected']
        else:
            print(f"❌ Failed to get Slack status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing Slack status: {e}")
        return False

def test_create_task(task_description, channel=None):
    """Test the create-task endpoint."""
    endpoint = f"{SLACK_BOT_ENDPOINT}/create-task"
    
    payload = {
        "task": task_description
    }
    
    if channel:
        payload["channel"] = channel
    
    try:
        print(f"\n📝 Testing task: {task_description}")
        response = requests.post(endpoint, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: {data['message']}")
            print(f"📤 Slack sent: {data['slack_sent']}")
            
            if data.get('parsed_task'):
                parsed = data['parsed_task']
                print(f"   Recipient: {parsed.get('recipient', 'Unknown')}")
                print(f"   Due Date: {parsed.get('due_date', 'Unknown')}")
                print(f"   Response Required: {parsed.get('response_required', False)}")
            
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing create-task: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Slack Bot API")
    print("=" * 40)
    
    # Test 1: Health check
    if not test_health_check():
        print("\n❌ Server is not running. Please start it with:")
        print("   python main.py")
        return
    
    # Test 2: Slack status
    slack_connected = test_slack_status()
    
    # Test 3: Create tasks
    test_tasks = [
        "Remind Alex to review Q3 numbers by Friday",
        "Ask Sarah to prepare the monthly report for next Monday",
        "Tell John to update the project timeline by tomorrow"
    ]
    
    print(f"\n📋 Testing {len(test_tasks)} example tasks...")
    
    success_count = 0
    for task in test_tasks:
        if test_create_task(task):
            success_count += 1
        time.sleep(1)  # Small delay between requests
    
    print(f"\n📊 Test Results:")
    print(f"   Server: ✅ Running")
    print(f"   Slack: {'✅ Connected' if slack_connected else '❌ Not connected'}")
    print(f"   Tasks: {success_count}/{len(test_tasks)} successful")
    
    if success_count == len(test_tasks):
        print("\n🎉 All tests passed! The Slack Bot API is working correctly.")
    else:
        print(f"\n⚠️  {len(test_tasks) - success_count} tests failed. Check your configuration.")

if __name__ == "__main__":
    main() 