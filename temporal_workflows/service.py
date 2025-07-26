"""
Temporal service integration for FastAPI routes.
This service provides methods to start workflows from your API endpoints.
"""
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from temporalio.client import WorkflowHandle
import logging

from .config import temporal_config
from .workflows import (
    TaskLifecycleWorkflow,
    TaskRelayWorkflow,
    PeriodicCleanupWorkflow,
    UserOnboardingWorkflow
)

logger = logging.getLogger(__name__)

class TemporalService:
    """Service for interacting with Temporal workflows from FastAPI."""
    
    def __init__(self):
        self.client = None
    
    async def _get_client(self):
        """Get or create Temporal client."""
        if self.client is None:
            self.client = await temporal_config.get_client()
        return self.client
    
    async def start_task_lifecycle_workflow(
        self, 
        task_data: Dict[str, Any],
        workflow_id: Optional[str] = None
    ) -> str:
        """
        Start a task lifecycle workflow.
        
        Args:
            task_data: Task data dictionary
            workflow_id: Optional custom workflow ID
            
        Returns:
            str: Workflow ID
        """
        try:
            client = await self._get_client()
            
            if not workflow_id:
                workflow_id = f"task-lifecycle-{datetime.utcnow().isoformat()}"
            
            handle = await client.start_workflow(
                TaskLifecycleWorkflow.run,
                task_data,
                id=workflow_id,
                task_queue=temporal_config.task_queue,
                execution_timeout=timedelta(days=30)  # Tasks can run for up to 30 days
            )
            
            logger.info(f"Started task lifecycle workflow: {workflow_id}")
            return workflow_id
            
        except Exception as e:
            logger.error(f"Failed to start task lifecycle workflow: {e}")
            raise
    
    async def start_task_relay_workflow(
        self,
        task_id: str,
        from_user: str,
        to_user: str,
        message: Optional[str] = None
    ) -> str:
        """
        Start a task relay workflow.
        
        Args:
            task_id: ID of the task to relay
            from_user: User relaying the task
            to_user: User receiving the task
            message: Optional relay message
            
        Returns:
            str: Workflow ID
        """
        try:
            client = await self._get_client()
            
            workflow_id = f"task-relay-{task_id}-{datetime.utcnow().isoformat()}"
            
            handle = await client.start_workflow(
                TaskRelayWorkflow.run,
                task_id,
                from_user,
                to_user,
                message,
                id=workflow_id,
                task_queue=temporal_config.task_queue,
                execution_timeout=timedelta(minutes=10)
            )
            
            logger.info(f"Started task relay workflow: {workflow_id}")
            return workflow_id
            
        except Exception as e:
            logger.error(f"Failed to start task relay workflow: {e}")
            raise
    
    async def start_user_onboarding_workflow(
        self,
        user_data: Dict[str, Any]
    ) -> str:
        """
        Start a user onboarding workflow.
        
        Args:
            user_data: User data dictionary
            
        Returns:
            str: Workflow ID
        """
        try:
            client = await self._get_client()
            
            user_id = user_data.get("user_id")
            workflow_id = f"user-onboarding-{user_id}"
            
            handle = await client.start_workflow(
                UserOnboardingWorkflow.run,
                user_data,
                id=workflow_id,
                task_queue=temporal_config.task_queue,
                execution_timeout=timedelta(days=7)  # Onboarding can take up to a week
            )
            
            logger.info(f"Started user onboarding workflow: {workflow_id}")
            return workflow_id
            
        except Exception as e:
            logger.error(f"Failed to start user onboarding workflow: {e}")
            raise
    
    async def start_periodic_cleanup_workflow(self) -> str:
        """
        Start the periodic cleanup workflow.
        This should only be started once and will run indefinitely.
        
        Returns:
            str: Workflow ID
        """
        try:
            client = await self._get_client()
            
            workflow_id = "periodic-cleanup-singleton"
            
            # Try to start the workflow, but don't fail if it already exists
            try:
                handle = await client.start_workflow(
                    PeriodicCleanupWorkflow.run,
                    1,  # Run every day
                    id=workflow_id,
                    task_queue=temporal_config.task_queue,
                    execution_timeout=timedelta(days=365)  # Run for a year
                )
                logger.info(f"Started periodic cleanup workflow: {workflow_id}")
            except Exception as e:
                if "already exists" in str(e).lower():
                    logger.info(f"Periodic cleanup workflow already running: {workflow_id}")
                else:
                    raise
            
            return workflow_id
            
        except Exception as e:
            logger.error(f"Failed to start periodic cleanup workflow: {e}")
            raise
    
    async def signal_task_completed(self, workflow_id: str):
        """
        Send a signal to mark a task as completed in its lifecycle workflow.
        
        Args:
            workflow_id: The workflow ID of the task lifecycle workflow
        """
        try:
            client = await self._get_client()
            
            handle = client.get_workflow_handle(workflow_id)
            await handle.signal(TaskLifecycleWorkflow.task_completed_signal)
            
            logger.info(f"Sent task completed signal to workflow: {workflow_id}")
            
        except Exception as e:
            logger.error(f"Failed to send task completed signal: {e}")
            raise
    
    async def signal_task_reassigned(self, workflow_id: str, new_user: str):
        """
        Send a signal to handle task reassignment in its lifecycle workflow.
        
        Args:
            workflow_id: The workflow ID of the task lifecycle workflow
            new_user: The new user assigned to the task
        """
        try:
            client = await self._get_client()
            
            handle = client.get_workflow_handle(workflow_id)
            await handle.signal(TaskLifecycleWorkflow.task_reassigned_signal, new_user)
            
            logger.info(f"Sent task reassigned signal to workflow: {workflow_id}")
            
        except Exception as e:
            logger.error(f"Failed to send task reassigned signal: {e}")
            raise
    
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """
        Get the status of a workflow.
        
        Args:
            workflow_id: The workflow ID to check
            
        Returns:
            Dict containing workflow status information
        """
        try:
            client = await self._get_client()
            
            handle = client.get_workflow_handle(workflow_id)
            description = await handle.describe()
            
            return {
                "workflow_id": workflow_id,
                "status": description.status.name,
                "start_time": description.start_time.isoformat() if description.start_time else None,
                "close_time": description.close_time.isoformat() if description.close_time else None,
                "execution_time": description.execution_time.isoformat() if description.execution_time else None,
                "workflow_type": description.workflow_type
            }
            
        except Exception as e:
            logger.error(f"Failed to get workflow status for {workflow_id}: {e}")
            return {"error": str(e)}

# Global temporal service instance
temporal_service = TemporalService()
