"""
Temporal workflows for RelAI application.
Workflows define the coordination logic for long-running business processes.
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from temporalio import workflow
from temporalio.common import RetryPolicy
import logging

from .activities import (
    create_task_activity,
    update_task_activity,
    assign_task_activity,
    relay_task_activity,
    send_notification_activity,
    check_task_deadline_activity,
    cleanup_completed_tasks_activity
)

logger = logging.getLogger(__name__)

@workflow.defn
class TaskLifecycleWorkflow:
    """Workflow to manage the complete lifecycle of a task."""
    
    def __init__(self):
        self.task_id: Optional[str] = None
        self.assigned_user: Optional[str] = None
        self.is_completed = False
        self.retry_policy = RetryPolicy(maximum_attempts=3)
    
    @workflow.run
    async def run(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main workflow execution for task lifecycle management."""
        try:
            # Step 1: Create the task
            create_result = await workflow.execute_activity(
                create_task_activity,
                task_data,
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=self.retry_policy
            )
            
            if not create_result.get("success"):
                return {"success": False, "error": "Failed to create task"}
            
            self.task_id = create_result["task_id"]
            workflow.logger.info(f"Task created: {self.task_id}")
            
            # Step 2: If task has an assignee, assign it
            if task_data.get("assignedTo"):
                assign_result = await workflow.execute_activity(
                    assign_task_activity,
                    self.task_id,
                    task_data["assignedTo"],
                    start_to_close_timeout=timedelta(seconds=30),
                    retry_policy=self.retry_policy
                )
                
                if assign_result.get("success"):
                    self.assigned_user = task_data["assignedTo"]
                    workflow.logger.info(f"Task {self.task_id} assigned to {self.assigned_user}")
                    
                    # Send notification to assigned user
                    await workflow.execute_activity(
                        send_notification_activity,
                        self.assigned_user,
                        f"New task assigned: {task_data.get('title', 'Untitled Task')}",
                        "task_assignment",
                        start_to_close_timeout=timedelta(seconds=10)
                    )
            
            # Step 3: Monitor task progress and deadlines
            await self._monitor_task_progress()
            
            return {"success": True, "task_id": self.task_id}
            
        except Exception as e:
            workflow.logger.error(f"Task lifecycle workflow failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _monitor_task_progress(self):
        """Monitor task progress and handle deadlines."""
        while not self.is_completed:
            try:
                # Check task deadline every hour
                await workflow.sleep(timedelta(hours=1))
                
                deadline_check = await workflow.execute_activity(
                    check_task_deadline_activity,
                    self.task_id,
                    start_to_close_timeout=timedelta(seconds=30)
                )
                
                if deadline_check.get("success"):
                    if deadline_check.get("is_approaching") and self.assigned_user:
                        # Send deadline warning
                        await workflow.execute_activity(
                            send_notification_activity,
                            self.assigned_user,
                            f"Task deadline approaching: {self.task_id}",
                            "deadline_warning",
                            start_to_close_timeout=timedelta(seconds=10)
                        )
                    
                    elif deadline_check.get("is_overdue") and self.assigned_user:
                        # Send overdue notification
                        await workflow.execute_activity(
                            send_notification_activity,
                            self.assigned_user,
                            f"Task overdue: {self.task_id}",
                            "deadline_overdue",
                            start_to_close_timeout=timedelta(seconds=10)
                        )
                
            except Exception as e:
                workflow.logger.error(f"Error monitoring task {self.task_id}: {e}")
                # Continue monitoring despite errors
                continue
    
    @workflow.signal
    async def task_completed_signal(self):
        """Signal to mark task as completed."""
        self.is_completed = True
        workflow.logger.info(f"Task {self.task_id} marked as completed")
    
    @workflow.signal
    async def task_reassigned_signal(self, new_user: str):
        """Signal to handle task reassignment."""
        old_user = self.assigned_user
        self.assigned_user = new_user
        workflow.logger.info(f"Task {self.task_id} reassigned from {old_user} to {new_user}")

@workflow.defn
class TaskRelayWorkflow:
    """Workflow to handle task relay between users."""
    
    @workflow.run
    async def run(
        self, 
        task_id: str, 
        from_user: str, 
        to_user: str, 
        message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute task relay workflow."""
        try:
            # Step 1: Perform the relay
            relay_result = await workflow.execute_activity(
                relay_task_activity,
                task_id,
                from_user,
                to_user,
                message,
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=RetryPolicy(maximum_attempts=3)
            )
            
            if not relay_result.get("success"):
                return {"success": False, "error": "Failed to relay task"}
            
            # Step 2: Send notifications
            # Notify the receiving user
            await workflow.execute_activity(
                send_notification_activity,
                to_user,
                f"Task relayed to you from {from_user}: {task_id}",
                "task_relay_received",
                start_to_close_timeout=timedelta(seconds=10)
            )
            
            # Notify the sender (confirmation)
            await workflow.execute_activity(
                send_notification_activity,
                from_user,
                f"Task successfully relayed to {to_user}: {task_id}",
                "task_relay_sent",
                start_to_close_timeout=timedelta(seconds=10)
            )
            
            return {"success": True, "task_id": task_id, "from_user": from_user, "to_user": to_user}
            
        except Exception as e:
            workflow.logger.error(f"Task relay workflow failed: {e}")
            return {"success": False, "error": str(e)}

@workflow.defn
class PeriodicCleanupWorkflow:
    """Workflow to periodically clean up old data."""
    
    @workflow.run
    async def run(self, cleanup_interval_days: int = 1) -> Dict[str, Any]:
        """Execute periodic cleanup workflow."""
        try:
            while True:
                # Wait for the specified interval
                await workflow.sleep(timedelta(days=cleanup_interval_days))
                
                # Perform cleanup
                cleanup_result = await workflow.execute_activity(
                    cleanup_completed_tasks_activity,
                    30,  # Clean tasks older than 30 days
                    start_to_close_timeout=timedelta(minutes=5),
                    retry_policy=RetryPolicy(maximum_attempts=2)
                )
                
                workflow.logger.info(f"Cleanup completed: {cleanup_result}")
                
        except Exception as e:
            workflow.logger.error(f"Periodic cleanup workflow failed: {e}")
            return {"success": False, "error": str(e)}

@workflow.defn
class UserOnboardingWorkflow:
    """Workflow to handle new user onboarding process."""
    
    @workflow.run
    async def run(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute user onboarding workflow."""
        try:
            user_id = user_data.get("user_id")
            
            # Step 1: Send welcome notification
            await workflow.execute_activity(
                send_notification_activity,
                user_id,
                "Welcome to RelAI! Your account has been created successfully.",
                "welcome",
                start_to_close_timeout=timedelta(seconds=10)
            )
            
            # Step 2: Create initial onboarding task
            onboarding_task = {
                "title": "Complete Your Profile",
                "description": "Please complete your profile information to get started with RelAI.",
                "status": "active",
                "assignedTo": user_id,
                "progress": 0
            }
            
            task_result = await workflow.execute_activity(
                create_task_activity,
                onboarding_task,
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=RetryPolicy(maximum_attempts=3)
            )
            
            if task_result.get("success"):
                # Send notification about the onboarding task
                await workflow.execute_activity(
                    send_notification_activity,
                    user_id,
                    "Your onboarding task has been created. Please complete your profile.",
                    "onboarding_task",
                    start_to_close_timeout=timedelta(seconds=10)
                )
            
            # Step 3: Schedule follow-up reminder after 24 hours
            await workflow.sleep(timedelta(hours=24))
            
            await workflow.execute_activity(
                send_notification_activity,
                user_id,
                "Reminder: Don't forget to complete your profile setup!",
                "onboarding_reminder",
                start_to_close_timeout=timedelta(seconds=10)
            )
            
            return {"success": True, "user_id": user_id, "onboarding_task_id": task_result.get("task_id")}
            
        except Exception as e:
            workflow.logger.error(f"User onboarding workflow failed: {e}")
            return {"success": False, "error": str(e)}
