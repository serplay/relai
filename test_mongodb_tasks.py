#!/usr/bin/env python3
"""
Test script for MongoDB task integration
"""

import asyncio
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mongodb.task_service import TaskService


async def test_task_service():
    """Test the MongoDB task service functionality."""
    
    print("🧪 Testing MongoDB Task Service")
    print("=" * 50)
    
    # Create service instance
    service = TaskService()
    
    # Connect to database
    if not service.connect():
        print("❌ Failed to connect to MongoDB. Please check your connection string.")
        return False
    
    try:
        print("✅ Connected to MongoDB successfully")
        
        # Test 1: Create a task
        print("\n📝 Test 1: Creating a task...")
        task_data = {
            "title": "Design System Components",
            "description": "Building reusable UI components for the platform",
            "progress": 0,
            "status": "active",
            "assignedTo": "yazide",
            "relayedFrom": None,
            "estimatedHandoff": "2h"
        }
        
        created_task = await service.create_task(task_data)
        if created_task:
            print(f"✅ Task created successfully: {created_task['title']}")
            task_id = created_task['_id']
        else:
            print("❌ Failed to create task")
            return False
        
        # Test 2: Get all tasks
        print("\n📋 Test 2: Getting all tasks...")
        all_tasks = await service.get_all_tasks()
        print(f"✅ Retrieved {len(all_tasks)} tasks")
        
        # Test 3: Get task by ID
        print("\n🔍 Test 3: Getting task by ID...")
        task = await service.get_task_by_id(task_id)
        if task:
            print(f"✅ Task found: {task['title']}")
        else:
            print("❌ Task not found")
            return False
        
        # Test 4: Update task progress
        print("\n📈 Test 4: Updating task progress...")
        updated_task = await service.update_task_progress(task_id, 50)
        if updated_task and updated_task['progress'] == 50:
            print(f"✅ Task progress updated to {updated_task['progress']}%")
        else:
            print("❌ Failed to update task progress")
            return False
        
        # Test 5: Assign task to different user
        print("\n👤 Test 5: Assigning task to different user...")
        assigned_task = await service.assign_task(task_id, "elliott")
        if assigned_task and assigned_task['assignedTo'] == "elliott":
            print(f"✅ Task assigned to {assigned_task['assignedTo']}")
        else:
            print("❌ Failed to assign task")
            return False
        
        # Test 6: Get tasks by user
        print("\n👥 Test 6: Getting tasks by user...")
        user_tasks = await service.get_tasks_by_user("elliott")
        print(f"✅ Found {len(user_tasks)} tasks for elliott")
        
        # Test 7: Relay task
        print("\n🔄 Test 7: Relaying task...")
        relayed_task = await service.relay_task(task_id, "elliott", "relai")
        if relayed_task:
            print(f"✅ Task relayed from {relayed_task['relayedFrom']} to {relayed_task['assignedTo']}")
        else:
            print("❌ Failed to relay task")
            return False
        
        # Test 8: Delete task
        print("\n🗑️ Test 8: Deleting task...")
        deleted = await service.delete_task(task_id)
        if deleted:
            print("✅ Task deleted successfully")
        else:
            print("❌ Failed to delete task")
            return False
        
        print("\n🎉 All tests passed! MongoDB task integration is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        return False
        
    finally:
        # Always disconnect
        service.disconnect()
        print("\n🔌 Disconnected from MongoDB")


if __name__ == "__main__":
    # Run the async test
    success = asyncio.run(test_task_service())
    
    if success:
        print("\n✅ MongoDB Task Integration Test: PASSED")
        sys.exit(0)
    else:
        print("\n❌ MongoDB Task Integration Test: FAILED")
        sys.exit(1) 