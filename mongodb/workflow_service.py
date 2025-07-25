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


class WorkflowService:
    """MongoDB service for managing workflows (combining users and tasks)."""
    
    def __init__(self):
        """Initialize MongoDB client with connection details."""
        self.connection_string = os.getenv("MONGODB_CONNECTION_STRING")
        self.database_name = os.getenv("MONGODB_DATABASE", "relai")
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
    
    async def get_user_workflow(self, user_id: str) -> Dict[str, Any]:
        """
        Get workflow data for a specific user.
        
        Args:
            user_id (str): The user's ID
            
        Returns:
            Dict[str, Any]: Workflow data containing activeWork, incoming, and recentHandoffs
        """
        try:
            if self.db is None:
                logger.error("Not connected to database. Call connect() first.")
                return {
                    "activeWork": None,
                    "incoming": [],
                    "recentHandoffs": []
                }
            
            tasks_collection = self.db["tasks"]
            
            # Get active work (tasks assigned to this user with status 'active')
            active_work = tasks_collection.find_one({
                "assignedTo": user_id,
                "status": "active"
            })
            
            if active_work:
                active_work = self._convert_object_id(active_work)
            
            # Get incoming tasks (tasks with status 'waiting' assigned to this user)
            incoming_tasks = list(tasks_collection.find({
                "assignedTo": user_id,
                "status": "waiting"
            }).sort("created_at", -1))
            
            incoming_tasks = self._convert_object_ids(incoming_tasks)
            
            # Get recent handoffs (completed tasks that were relayed from this user)
            recent_handoffs = list(tasks_collection.find({
                "relayedFrom": user_id,
                "status": "completed"
            }).sort("updated_at", -1).limit(5))
            
            recent_handoffs = self._convert_object_ids(recent_handoffs)
            
            workflow_data = {
                "activeWork": active_work,
                "incoming": incoming_tasks,
                "recentHandoffs": recent_handoffs
            }
            
            logger.info(f"Retrieved workflow for user: {user_id}")
            return workflow_data
            
        except Exception as e:
            logger.error(f"Error fetching user workflow: {str(e)}")
            return {
                "activeWork": None,
                "incoming": [],
                "recentHandoffs": []
            }
    
    async def get_all_workflows(self) -> Dict[str, Dict[str, Any]]:
        """
        Get workflow data for all users.
        
        Returns:
            Dict[str, Dict[str, Any]]: Workflow data for all users
        """
        try:
            if self.db is None:
                logger.error("Not connected to database. Call connect() first.")
                return {}
            
            users_collection = self.db["users"]
            users = list(users_collection.find({}))
            users = self._convert_object_ids(users)
            
            workflows = {}
            for user in users:
                user_id = user["_id"]
                workflow = await self.get_user_workflow(user_id)
                workflows[user_id] = workflow
            
            logger.info(f"Retrieved workflows for {len(users)} users")
            return workflows
            
        except Exception as e:
            logger.error(f"Error fetching all workflows: {str(e)}")
            return {}
    
    async def get_workflow_stats(self) -> Dict[str, Any]:
        """
        Get workflow statistics.
        
        Returns:
            Dict[str, Any]: Workflow statistics
        """
        try:
            if self.db is None:
                logger.error("Not connected to database. Call connect() first.")
                return {}
            
            tasks_collection = self.db["tasks"]
            
            # Count tasks by status
            active_count = tasks_collection.count_documents({"status": "active"})
            waiting_count = tasks_collection.count_documents({"status": "waiting"})
            completed_count = tasks_collection.count_documents({"status": "completed"})
            
            # Count users
            users_collection = self.db["users"]
            user_count = users_collection.count_documents({})
            
            stats = {
                "active_tasks": active_count,
                "waiting_tasks": waiting_count,
                "completed_tasks": completed_count,
                "total_tasks": active_count + waiting_count + completed_count,
                "total_users": user_count
            }
            
            logger.info(f"Retrieved workflow stats: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error fetching workflow stats: {str(e)}")
            return {}


# Global instance
workflow_service = WorkflowService()


def main():
    """Example usage of the WorkflowService."""
    
    # Create service instance
    service = WorkflowService()
    
    # Connect to database
    if not service.connect():
        print("Failed to connect to MongoDB. Please check your connection string.")
        return
    
    try:
        print("=" * 50)
        print("WORKFLOW SERVICE TEST")
        print("=" * 50)
        
        print("\n📊 Workflow Statistics:")
        # Note: This would need to be run in an async context
        # stats = await service.get_workflow_stats()
        # print(f"Stats: {stats}")
        
    finally:
        # Always disconnect
        service.disconnect()


if __name__ == "__main__":
    main() 