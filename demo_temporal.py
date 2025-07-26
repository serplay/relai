#!/usr/bin/env python3
"""
Example script demonstrating Temporal integration with RelAI.
This script shows how to interact with Temporal workflows programmatically.
"""
import asyncio
import os
import sys
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from temporal_workflows.service import temporal_service

async def main():
    """Main function demonstrating Temporal workflows."""
    print("🚀 RelAI Temporal Integration Demo")
    print("=" * 50)
    
    try:
        # Example 1: Start a task lifecycle workflow
        print("\n1. Creating a task with lifecycle workflow...")
        task_data = {
            "title": "Demo Task: Review Documentation",
            "description": "Please review the Temporal integration documentation",
            "assignedTo": "demo-user-123",
            "status": "active",
            "progress": 0,
            "estimatedHandoff": "2025-01-30T12:00:00Z"
        }
        
        task_workflow_id = await temporal_service.start_task_lifecycle_workflow(task_data)
        print(f"✅ Task lifecycle workflow started: {task_workflow_id}")
        
        # Example 2: Start a user onboarding workflow
        print("\n2. Starting user onboarding workflow...")
        user_data = {
            "user_id": "new-user-456",
            "name": "Demo User",
            "created_at": datetime.utcnow().isoformat()
        }
        
        onboarding_workflow_id = await temporal_service.start_user_onboarding_workflow(user_data)
        print(f"✅ User onboarding workflow started: {onboarding_workflow_id}")
        
        # Example 3: Start a task relay workflow
        print("\n3. Starting task relay workflow...")
        relay_workflow_id = await temporal_service.start_task_relay_workflow(
            task_id="demo-task-789",
            from_user="user-a",
            to_user="user-b",
            message="Please take over this task, it's urgent!"
        )
        print(f"✅ Task relay workflow started: {relay_workflow_id}")
        
        # Example 4: Start periodic cleanup (singleton)
        print("\n4. Starting periodic cleanup workflow...")
        cleanup_workflow_id = await temporal_service.start_periodic_cleanup_workflow()
        print(f"✅ Periodic cleanup workflow: {cleanup_workflow_id}")
        
        # Example 5: Check workflow status
        print("\n5. Checking workflow statuses...")
        for wf_id in [task_workflow_id, onboarding_workflow_id, relay_workflow_id]:
            status = await temporal_service.get_workflow_status(wf_id)
            print(f"📊 Workflow {wf_id[:20]}... status: {status.get('status', 'Unknown')}")
        
        # Example 6: Send signals (commented out as they need existing workflows)
        # print("\n6. Sending workflow signals...")
        # await temporal_service.signal_task_completed(task_workflow_id)
        # print(f"📤 Sent task completed signal to: {task_workflow_id}")
        
        print("\n" + "=" * 50)
        print("🎉 Demo completed successfully!")
        print("\nNext steps:")
        print("1. Check the Temporal Web UI at http://localhost:8233")
        print("2. Monitor workflow execution in real-time")
        print("3. Start the Temporal worker to see activities execute")
        print("4. Start your FastAPI app to trigger workflows via API")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure Temporal server is running: temporal server start-dev")
        print("2. Check your .env file for correct Temporal configuration")
        print("3. Ensure MongoDB is accessible")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
