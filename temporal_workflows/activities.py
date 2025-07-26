"""
Temporal activities for RelAI application.
Activities are the building blocks of workflows that perform actual work.
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from temporalio import activity
import logging

from mongodb.task_service import task_service
from mongodb.user_service import user_service
from mongodb.workflow_service import workflow_service

logger = logging.getLogger(__name__)

@activity.defn
async def create_task_activity(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """Activity to create a new task in MongoDB."""
    try:
        # Ensure database connection
        if not task_service.db:
            task_service.connect()
        
        # Create the task
        task_id = await task_service.create_task(task_data)
        
        logger.info(f"Task created with ID: {task_id}")
        return {"success": True, "task_id": task_id}
    except Exception as e:
        logger.error(f"Failed to create task: {e}")
        return {"success": False, "error": str(e)}

@activity.defn
async def update_task_activity(task_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
    """Activity to update a task in MongoDB."""
    try:
        # Ensure database connection
        if not task_service.db:
            task_service.connect()
        
        # Update the task
        success = await task_service.update_task(task_id, update_data)
        
        logger.info(f"Task {task_id} updated: {success}")
        return {"success": success, "task_id": task_id}
    except Exception as e:
        logger.error(f"Failed to update task {task_id}: {e}")
        return {"success": False, "error": str(e)}

@activity.defn
async def assign_task_activity(task_id: str, user_id: str) -> Dict[str, Any]:
    """Activity to assign a task to a user."""
    try:
        # Ensure database connection
        if not task_service.db:
            task_service.connect()
        
        # Assign the task
        success = await task_service.assign_task(task_id, user_id)
        
        # Update workflow data
        if workflow_service.db or workflow_service.connect():
            await workflow_service.update_user_workflow(user_id, {
                "activeWork": {"task_id": task_id, "assigned_at": datetime.utcnow().isoformat()}
            })
        
        logger.info(f"Task {task_id} assigned to user {user_id}")
        return {"success": success, "task_id": task_id, "user_id": user_id}
    except Exception as e:
        logger.error(f"Failed to assign task {task_id} to user {user_id}: {e}")
        return {"success": False, "error": str(e)}

@activity.defn
async def relay_task_activity(task_id: str, from_user: str, to_user: str, message: Optional[str] = None) -> Dict[str, Any]:
    """Activity to relay a task from one user to another."""
    try:
        # Ensure database connection
        if not task_service.db:
            task_service.connect()
        
        # Relay the task
        result = await task_service.relay_task(task_id, from_user, to_user, message)
        
        # Update workflow data for both users
        if workflow_service.db or workflow_service.connect():
            # Update from_user workflow (remove from active work)
            await workflow_service.add_handoff(from_user, {
                "task_id": task_id,
                "to_user": to_user,
                "message": message,
                "relayed_at": datetime.utcnow().isoformat()
            })
            
            # Update to_user workflow (add to incoming)
            await workflow_service.add_incoming_task(to_user, {
                "task_id": task_id,
                "from_user": from_user,
                "message": message,
                "received_at": datetime.utcnow().isoformat()
            })
        
        logger.info(f"Task {task_id} relayed from {from_user} to {to_user}")
        return {"success": True, "task_id": task_id, "from_user": from_user, "to_user": to_user}
    except Exception as e:
        logger.error(f"Failed to relay task {task_id}: {e}")
        return {"success": False, "error": str(e)}

@activity.defn
async def send_notification_activity(user_id: str, message: str, notification_type: str = "info") -> Dict[str, Any]:
    """Activity to send notifications to users (could be email, Slack, etc.)."""
    try:
        # This is a placeholder for notification logic
        # You could integrate with email services, Slack API, etc.
        logger.info(f"Notification sent to {user_id}: {message} (type: {notification_type})")
        
        # For now, just log the notification
        # In a real implementation, you'd integrate with your notification services
        return {"success": True, "user_id": user_id, "message": message}
    except Exception as e:
        logger.error(f"Failed to send notification to {user_id}: {e}")
        return {"success": False, "error": str(e)}

@activity.defn
async def check_task_deadline_activity(task_id: str) -> Dict[str, Any]:
    """Activity to check if a task is approaching its deadline."""
    try:
        # Ensure database connection
        if not task_service.db:
            task_service.connect()
        
        # Get task details
        task = await task_service.get_task_by_id(task_id)
        if not task:
            return {"success": False, "error": "Task not found"}
        
        # Check if task has a deadline and if it's approaching
        estimated_handoff = task.get("estimatedHandoff")
        if estimated_handoff:
            # Parse the deadline and check if it's within 24 hours
            try:
                deadline = datetime.fromisoformat(estimated_handoff.replace('Z', '+00:00'))
                now = datetime.utcnow()
                time_remaining = deadline - now
                
                is_approaching = time_remaining <= timedelta(hours=24) and time_remaining > timedelta(0)
                is_overdue = time_remaining <= timedelta(0)
                
                return {
                    "success": True,
                    "task_id": task_id,
                    "deadline": estimated_handoff,
                    "is_approaching": is_approaching,
                    "is_overdue": is_overdue,
                    "time_remaining_hours": time_remaining.total_seconds() / 3600
                }
            except ValueError:
                return {"success": False, "error": "Invalid deadline format"}
        
        return {"success": True, "task_id": task_id, "has_deadline": False}
    except Exception as e:
        logger.error(f"Failed to check deadline for task {task_id}: {e}")
        return {"success": False, "error": str(e)}

@activity.defn
async def cleanup_completed_tasks_activity(days_old: int = 30) -> Dict[str, Any]:
    """Activity to clean up old completed tasks."""
    try:
        # Ensure database connection
        if not task_service.db:
            task_service.connect()
        
        # Calculate cutoff date
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        # This would be implemented in your task service
        # For now, just return a placeholder
        logger.info(f"Cleanup activity would remove completed tasks older than {days_old} days")
        
        return {"success": True, "cutoff_date": cutoff_date.isoformat(), "cleaned_count": 0}
    except Exception as e:
        logger.error(f"Failed to cleanup tasks: {e}")
        return {"success": False, "error": str(e)}
