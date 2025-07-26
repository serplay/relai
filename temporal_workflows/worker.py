"""
Temporal worker for RelAI application.
The worker runs workflows and activities.
"""
import asyncio
import logging
from temporalio.client import Client
from temporalio.worker import Worker

from .config import temporal_config
from .workflows import (
    TaskLifecycleWorkflow,
    TaskRelayWorkflow,
    PeriodicCleanupWorkflow,
    UserOnboardingWorkflow
)
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

class TemporalWorker:
    """Temporal worker manager for RelAI."""
    
    def __init__(self):
        self.worker = None
        self.client = None
    
    async def start(self):
        """Start the Temporal worker."""
        try:
            # Get Temporal client
            self.client = await temporal_config.get_client()
            
            # Create worker
            self.worker = Worker(
                client=self.client,
                task_queue=temporal_config.task_queue,
                workflows=[
                    TaskLifecycleWorkflow,
                    TaskRelayWorkflow,
                    PeriodicCleanupWorkflow,
                    UserOnboardingWorkflow
                ],
                activities=[
                    create_task_activity,
                    update_task_activity,
                    assign_task_activity,
                    relay_task_activity,
                    send_notification_activity,
                    check_task_deadline_activity,
                    cleanup_completed_tasks_activity
                ]
            )
            
            logger.info(f"Starting Temporal worker on task queue: {temporal_config.task_queue}")
            await self.worker.run()
            
        except Exception as e:
            logger.error(f"Failed to start Temporal worker: {e}")
            raise
    
    async def stop(self):
        """Stop the Temporal worker."""
        if self.worker:
            await self.worker.shutdown()
        if self.client:
            await temporal_config.close_client()

async def run_worker():
    """Run the Temporal worker."""
    worker = TemporalWorker()
    try:
        await worker.start()
    except KeyboardInterrupt:
        logger.info("Shutting down worker...")
        await worker.stop()
    except Exception as e:
        logger.error(f"Worker error: {e}")
        await worker.stop()
        raise

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Run the worker
    asyncio.run(run_worker())
