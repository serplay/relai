import os
from pymongo import MongoClient
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import logging
from datetime import datetime
from bson import ObjectId

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskService:
    """MongoDB service for managing tasks."""
    
    def __init__(self):
        """Initialize MongoDB client with connection details."""
        self.connection_string = os.getenv("MONGODB_CONNECTION_STRING")
        self.database_name = os.getenv("MONGODB_DATABASE", "relai")
        self.collection_name = "tasks"
        self.client = None
        self.db = None
        
        if not self.connection_string:
            logger.warning("MongoDB connection string not found in environment variables")
            logger.info("Please set MONGODB_CONNECTION_STRING in your .env file")
    
    def connect(self) -> bool:
        """
        Connect to MongoDB Atlas.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            if not self.connection_string:
                logger.error("No MongoDB connection string provided")
                return False
                
            self.client = MongoClient(self.connection_string)
            # Test the connection
            self.client.admin.command('ping')
            self.db = self.client[self.database_name]
            logger.info(f"Successfully connected to MongoDB database: {self.database_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            return False
    
    def disconnect(self):
        """Close the MongoDB connection."""
        if self.client is not None:
            self.client.close()
            logger.info("MongoDB connection closed")
    
    def _convert_object_id(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Convert ObjectId to string for JSON serialization."""
        if document and '_id' in document:
            document['_id'] = str(document['_id'])
        return document
    
    def _convert_object_ids(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert ObjectIds to strings for JSON serialization."""
        for doc in documents:
            self._convert_object_id(doc)
        return documents
    
    async def create_task(self, task_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new task.
        
        Args:
            task_data (Dict[str, Any]): Task data to create
            
        Returns:
            Optional[Dict[str, Any]]: Created task or None if failed
        """
        try:
            if self.db is None:
                logger.error("Not connected to database. Call connect() first.")
                return None
            
            collection = self.db[self.collection_name]
            
            # Add timestamps
            task_data['created_at'] = datetime.utcnow()
            task_data['updated_at'] = datetime.utcnow()
            
            # Insert the task
            result = collection.insert_one(task_data)
            
            # Fetch the created task
            created_task = collection.find_one({'_id': result.inserted_id})
            created_task = self._convert_object_id(created_task)
            
            logger.info(f"Created task: {created_task.get('title', 'Unknown')}")
            return created_task
            
        except Exception as e:
            logger.error(f"Error creating task: {str(e)}")
            return None
    
    async def get_all_tasks(self) -> List[Dict[str, Any]]:
        """
        Fetch all tasks.
        
        Returns:
            List[Dict[str, Any]]: List of all tasks
        """
        try:
            if self.db is None:
                logger.error("Not connected to database. Call connect() first.")
                return []
            
            collection = self.db[self.collection_name]
            tasks = list(collection.find({}).sort('created_at', -1))
            tasks = self._convert_object_ids(tasks)
            
            logger.info(f"Retrieved {len(tasks)} tasks")
            return tasks
            
        except Exception as e:
            logger.error(f"Error fetching tasks: {str(e)}")
            return []
    
    async def get_task_by_id(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch a specific task by ID.
        
        Args:
            task_id (str): The task's ObjectId as string
            
        Returns:
            Optional[Dict[str, Any]]: Task document or None if not found
        """
        try:
            if self.db is None:
                logger.error("Not connected to database. Call connect() first.")
                return None
            
            collection = self.db[self.collection_name]
            task = collection.find_one({"_id": ObjectId(task_id)})
            
            if task:
                task = self._convert_object_id(task)
                logger.info(f"Found task: {task.get('title', 'Unknown')}")
            else:
                logger.info(f"No task found with ID: {task_id}")
            
            return task
            
        except Exception as e:
            logger.error(f"Error fetching task by ID: {str(e)}")
            return None
    
    async def get_tasks_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Fetch tasks assigned to a specific user.
        
        Args:
            user_id (str): The user's ID
            
        Returns:
            List[Dict[str, Any]]: List of tasks assigned to the user
        """
        try:
            if self.db is None:
                logger.error("Not connected to database. Call connect() first.")
                return []
            
            collection = self.db[self.collection_name]
            tasks = list(collection.find({"assignedTo": user_id}).sort('created_at', -1))
            tasks = self._convert_object_ids(tasks)
            
            logger.info(f"Retrieved {len(tasks)} tasks for user: {user_id}")
            return tasks
            
        except Exception as e:
            logger.error(f"Error fetching tasks by user: {str(e)}")
            return []
    
    async def update_task(self, task_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update a task.
        
        Args:
            task_id (str): The task's ObjectId as string
            update_data (Dict[str, Any]): Data to update
            
        Returns:
            Optional[Dict[str, Any]]: Updated task or None if failed
        """
        try:
            if self.db is None:
                logger.error("Not connected to database. Call connect() first.")
                return None
            
            collection = self.db[self.collection_name]
            
            # Add updated timestamp
            update_data['updated_at'] = datetime.utcnow()
            
            # Update the task
            result = collection.update_one(
                {"_id": ObjectId(task_id)},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                # Fetch the updated task
                updated_task = collection.find_one({'_id': ObjectId(task_id)})
                updated_task = self._convert_object_id(updated_task)
                logger.info(f"Updated task: {updated_task.get('title', 'Unknown')}")
                return updated_task
            else:
                logger.warning(f"No task found with ID: {task_id}")
                return None
            
        except Exception as e:
            logger.error(f"Error updating task: {str(e)}")
            return None
    
    async def delete_task(self, task_id: str) -> bool:
        """
        Delete a task.
        
        Args:
            task_id (str): The task's ObjectId as string
            
        Returns:
            bool: True if deleted successfully, False otherwise
        """
        try:
            if self.db is None:
                logger.error("Not connected to database. Call connect() first.")
                return False
            
            collection = self.db[self.collection_name]
            result = collection.delete_one({"_id": ObjectId(task_id)})
            
            if result.deleted_count > 0:
                logger.info(f"Deleted task with ID: {task_id}")
                return True
            else:
                logger.warning(f"No task found with ID: {task_id}")
                return False
            
        except Exception as e:
            logger.error(f"Error deleting task: {str(e)}")
            return False
    
    async def assign_task(self, task_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Assign a task to a user.
        
        Args:
            task_id (str): The task's ObjectId as string
            user_id (str): The user's ID to assign to
            
        Returns:
            Optional[Dict[str, Any]]: Updated task or None if failed
        """
        return await self.update_task(task_id, {"assignedTo": user_id})
    
    async def update_task_progress(self, task_id: str, progress: int) -> Optional[Dict[str, Any]]:
        """
        Update task progress.
        
        Args:
            task_id (str): The task's ObjectId as string
            progress (int): Progress percentage (0-100)
            
        Returns:
            Optional[Dict[str, Any]]: Updated task or None if failed
        """
        return await self.update_task(task_id, {"progress": progress})
    
    async def relay_task(self, task_id: str, from_user: str, to_user: str) -> Optional[Dict[str, Any]]:
        """
        Relay a task from one user to another.
        
        Args:
            task_id (str): The task's ObjectId as string
            from_user (str): The user relaying the task
            to_user (str): The user receiving the task
            
        Returns:
            Optional[Dict[str, Any]]: Updated task or None if failed
        """
        relay_data = {
            "relayedFrom": from_user,
            "assignedTo": to_user,
            "relayedAt": datetime.utcnow()
        }
        return await self.update_task(task_id, relay_data)


# Global instance
task_service = TaskService()


def main():
    """Example usage of the TaskService."""
    
    # Create service instance
    service = TaskService()
    
    # Connect to database
    if not service.connect():
        print("Failed to connect to MongoDB. Please check your connection string.")
        return
    
    try:
        print("=" * 50)
        print("TASK SERVICE TEST")
        print("=" * 50)
        
        # Example task data
        task_data = {
            "title": "Design System Components",
            "description": "Building reusable UI components for the platform",
            "progress": 0,
            "status": "active",
            "assignedTo": "yazide",
            "relayedFrom": None,
            "estimatedHandoff": "2h"
        }
        
        print("\n📝 Creating task...")
        # Note: This would need to be run in an async context
        # created_task = await service.create_task(task_data)
        # print(f"Created task: {created_task}")
        
    finally:
        # Always disconnect
        service.disconnect()


if __name__ == "__main__":
    main() 