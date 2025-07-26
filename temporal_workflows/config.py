"""
Temporal configuration and client setup for RelAI application.
"""
import os
import asyncio
from temporalio import workflow
from temporalio.client import Client
from temporalio.worker import Worker
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Temporal configuration
TEMPORAL_HOST = os.getenv("TEMPORAL_HOST", "localhost:7233")
TEMPORAL_NAMESPACE = os.getenv("TEMPORAL_NAMESPACE", "default")
TEMPORAL_TASK_QUEUE = os.getenv("TEMPORAL_TASK_QUEUE", "relai-task-queue")

class TemporalConfig:
    """Configuration class for Temporal settings."""
    
    def __init__(self):
        self.host = TEMPORAL_HOST
        self.namespace = TEMPORAL_NAMESPACE
        self.task_queue = TEMPORAL_TASK_QUEUE
        self._client = None
    
    async def get_client(self) -> Client:
        """Get or create Temporal client."""
        if self._client is None:
            try:
                self._client = await Client.connect(
                    target_host=self.host,
                    namespace=self.namespace
                )
                logger.info(f"Connected to Temporal at {self.host}")
            except Exception as e:
                logger.error(f"Failed to connect to Temporal: {e}")
                raise
        return self._client
    
    async def close_client(self):
        """Close Temporal client connection."""
        if self._client:
            # Note: In newer versions of temporalio, clients are automatically closed
            # when they go out of scope. No explicit close method is needed.
            self._client = None

# Global temporal config instance
temporal_config = TemporalConfig()
