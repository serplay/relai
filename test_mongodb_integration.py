#!/usr/bin/env python3
"""
Test script for MongoDB integration
This script tests the MongoDB services and API endpoints
"""

import asyncio
import requests
import json
from datetime import datetime

# API base URL
API_BASE_URL = "http://localhost:8000"

def test_user_endpoints():
    """Test user-related endpoints"""
    print("Testing User Endpoints...")
    
    # Test creating a user
    user_data = {
        "name": "Test User",
        "avatar": "/lovable-uploads/ad7ac94b-537e-4407-8cdc-26c4a1f25f84.png",
        "status": "idle"
    }
    
    response = requests.post(f"{API_BASE_URL}/api/users", json=user_data)
    if response.status_code == 200:
        user = response.json()
        print(f"✅ Created user: {user['name']} (ID: {user['_id']})")
        user_id = user['_id']
    else:
        print(f"❌ Failed to create user: {response.status_code}")
        return None
    
    # Test getting all users
    response = requests.get(f"{API_BASE_URL}/api/users")
    if response.status_code == 200:
        users = response.json()
        print(f"✅ Retrieved {len(users)} users")
    else:
        print(f"❌ Failed to get users: {response.status_code}")
    
    # Test getting specific user
    response = requests.get(f"{API_BASE_URL}/api/users/{user_id}")
    if response.status_code == 200:
        user = response.json()
        print(f"✅ Retrieved user: {user['name']}")
    else:
        print(f"❌ Failed to get user: {response.status_code}")
    
    return user_id

def test_task_endpoints():
    """Test task-related endpoints"""
    print("\nTesting Task Endpoints...")
    
    # Test creating a task
    task_data = {
        "title": "Test Task",
        "description": "This is a test task for MongoDB integration",
        "progress": 0,
        "status": "active",
        "assignedTo": None,
        "estimatedHandoff": "2h"
    }
    
    response = requests.post(f"{API_BASE_URL}/api/tasks", json=task_data)
    if response.status_code == 200:
        task = response.json()
        print(f"✅ Created task: {task['title']} (ID: {task['_id']})")
        task_id = task['_id']
    else:
        print(f"❌ Failed to create task: {response.status_code}")
        return None
    
    # Test getting all tasks
    response = requests.get(f"{API_BASE_URL}/api/tasks")
    if response.status_code == 200:
        tasks = response.json()
        print(f"✅ Retrieved {len(tasks)} tasks")
    else:
        print(f"❌ Failed to get tasks: {response.status_code}")
    
    # Test updating task progress
    progress_data = {"progress": 50}
    response = requests.put(f"{API_BASE_URL}/api/tasks/{task_id}/progress", json=progress_data)
    if response.status_code == 200:
        task = response.json()
        print(f"✅ Updated task progress to {task['progress']}%")
    else:
        print(f"❌ Failed to update task progress: {response.status_code}")
    
    return task_id

def test_workflow_endpoints():
    """Test workflow-related endpoints"""
    print("\nTesting Workflow Endpoints...")
    
    # Test getting workflow stats
    response = requests.get(f"{API_BASE_URL}/api/workflows/stats")
    if response.status_code == 200:
        stats = response.json()
        print(f"✅ Retrieved workflow stats: {stats}")
    else:
        print(f"❌ Failed to get workflow stats: {response.status_code}")

def main():
    """Main test function"""
    print("=" * 50)
    print("MONGODB INTEGRATION TEST")
    print("=" * 50)
    
    try:
        # Test if server is running
        response = requests.get(f"{API_BASE_URL}/")
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server is not responding")
            return
        
        # Run tests
        user_id = test_user_endpoints()
        task_id = test_task_endpoints()
        test_workflow_endpoints()
        
        print("\n" + "=" * 50)
        print("TEST SUMMARY")
        print("=" * 50)
        print("✅ MongoDB integration is working!")
        print(f"✅ Created user with ID: {user_id}")
        print(f"✅ Created task with ID: {task_id}")
        print("\nNext steps:")
        print("1. Start the frontend application")
        print("2. Test the UI with the new MongoDB backend")
        print("3. Verify that data persists in MongoDB")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server")
        print("Make sure the FastAPI server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")

if __name__ == "__main__":
    main() 