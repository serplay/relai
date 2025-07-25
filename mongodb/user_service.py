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


class UserService:
    """MongoDB service for managing users."""
    
    def __init__(self):
        """Initialize MongoDB client with connection details."""
        self.connection_string = os.getenv("MONGODB_CONNECTION_STRING")
        self.database_name = os.getenv("MONGODB_DATABASE", "relai")
        self.collection_name = "users"
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
    
    async def create_user(self, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new user.
        
        Args:
            user_data (Dict[str, Any]): User data to create
            
        Returns:
            Optional[Dict[str, Any]]: Created user or None if failed
        """
        try:
            if self.db is None:
                logger.error("Not connected to database. Call connect() first.")
                return None
            
            collection = self.db[self.collection_name]
            
            # Add timestamps
            user_data['created_at'] = datetime.utcnow()
            user_data['updated_at'] = datetime.utcnow()
            
            # Set default avatar if not provided
            if 'avatar' not in user_data or not user_data['avatar']:
                user_data['avatar'] = '/lovable-uploads/ad7ac94b-537e-4407-8cdc-26c4a1f25f84.png'
            
            # Set default status if not provided
            if 'status' not in user_data:
                user_data['status'] = 'idle'
            
            # Insert the user
            result = collection.insert_one(user_data)
            
            # Fetch the created user
            created_user = collection.find_one({'_id': result.inserted_id})
            created_user = self._convert_object_id(created_user)
            
            logger.info(f"Created user: {created_user.get('name', 'Unknown')}")
            return created_user
            
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return None
    
    async def get_all_users(self) -> List[Dict[str, Any]]:
        """
        Fetch all users.
        
        Returns:
            List[Dict[str, Any]]: List of all users
        """
        try:
            if self.db is None:
                logger.error("Not connected to database. Call connect() first.")
                return []
            
            collection = self.db[self.collection_name]
            users = list(collection.find({}).sort('name', 1))
            users = self._convert_object_ids(users)
            
            logger.info(f"Retrieved {len(users)} users")
            return users
            
        except Exception as e:
            logger.error(f"Error fetching users: {str(e)}")
            return []
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch a specific user by ID.
        
        Args:
            user_id (str): The user's ObjectId as string
            
        Returns:
            Optional[Dict[str, Any]]: User document or None if not found
        """
        try:
            if self.db is None:
                logger.error("Not connected to database. Call connect() first.")
                return None
            
            collection = self.db[self.collection_name]
            user = collection.find_one({"_id": ObjectId(user_id)})
            
            if user:
                user = self._convert_object_id(user)
                logger.info(f"Found user: {user.get('name', 'Unknown')}")
            else:
                logger.info(f"No user found with ID: {user_id}")
            
            return user
            
        except Exception as e:
            logger.error(f"Error fetching user by ID: {str(e)}")
            return None
    
    async def get_user_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Fetch a user by name.
        
        Args:
            name (str): The user's name
            
        Returns:
            Optional[Dict[str, Any]]: User document or None if not found
        """
        try:
            if self.db is None:
                logger.error("Not connected to database. Call connect() first.")
                return None
            
            collection = self.db[self.collection_name]
            user = collection.find_one({"name": name})
            
            if user:
                user = self._convert_object_id(user)
                logger.info(f"Found user by name: {user.get('name', 'Unknown')}")
            else:
                logger.info(f"No user found with name: {name}")
            
            return user
            
        except Exception as e:
            logger.error(f"Error fetching user by name: {str(e)}")
            return None
    
    async def update_user(self, user_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update a user.
        
        Args:
            user_id (str): The user's ObjectId as string
            update_data (Dict[str, Any]): Data to update
            
        Returns:
            Optional[Dict[str, Any]]: Updated user or None if failed
        """
        try:
            if self.db is None:
                logger.error("Not connected to database. Call connect() first.")
                return None
            
            collection = self.db[self.collection_name]
            
            # Add updated timestamp
            update_data['updated_at'] = datetime.utcnow()
            
            # Update the user
            result = collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                # Fetch the updated user
                updated_user = collection.find_one({'_id': ObjectId(user_id)})
                updated_user = self._convert_object_id(updated_user)
                logger.info(f"Updated user: {updated_user.get('name', 'Unknown')}")
                return updated_user
            else:
                logger.warning(f"No user found with ID: {user_id}")
                return None
            
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            return None
    
    async def delete_user(self, user_id: str) -> bool:
        """
        Delete a user.
        
        Args:
            user_id (str): The user's ObjectId as string
            
        Returns:
            bool: True if deleted successfully, False otherwise
        """
        try:
            if self.db is None:
                logger.error("Not connected to database. Call connect() first.")
                return False
            
            collection = self.db[self.collection_name]
            result = collection.delete_one({"_id": ObjectId(user_id)})
            
            if result.deleted_count > 0:
                logger.info(f"Deleted user with ID: {user_id}")
                return True
            else:
                logger.warning(f"No user found with ID: {user_id}")
                return False
            
        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            return False
    
    async def update_user_status(self, user_id: str, status: str) -> Optional[Dict[str, Any]]:
        """
        Update user status.
        
        Args:
            user_id (str): The user's ObjectId as string
            status (str): New status ('working' or 'idle')
            
        Returns:
            Optional[Dict[str, Any]]: Updated user or None if failed
        """
        return await self.update_user(user_id, {"status": status})


# Global instance
user_service = UserService()


def main():
    """Example usage of the UserService."""
    
    # Create service instance
    service = UserService()
    
    # Connect to database
    if not service.connect():
        print("Failed to connect to MongoDB. Please check your connection string.")
        return
    
    try:
        print("=" * 50)
        print("USER SERVICE TEST")
        print("=" * 50)
        
        # Example user data
        user_data = {
            "name": "Test User",
            "avatar": "/lovable-uploads/ad7ac94b-537e-4407-8cdc-26c4a1f25f84.png",
            "status": "idle"
        }
        
        print("\n👤 Creating user...")
        # Note: This would need to be run in an async context
        # created_user = await service.create_user(user_data)
        # print(f"Created user: {created_user}")
        
    finally:
        # Always disconnect
        service.disconnect()


if __name__ == "__main__":
    main() 