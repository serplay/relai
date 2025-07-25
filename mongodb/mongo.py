import os
from pymongo import MongoClient
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MongoDBClient:
    """MongoDB client for connecting to MongoDB Atlas and managing collections."""
    
    def __init__(self):
        """Initialize MongoDB client with connection details."""
        self.connection_string = os.getenv("MONGODB_CONNECTION_STRING")
        self.database_name = os.getenv("MONGODB_DATABASE", "test")
        self.client = None
        self.db = None
        
        if not self.connection_string:
            logger.warning("MongoDB connection string not found in environment variables")
            logger.info("Please set MONGODB_CONNECTION_STRING in your .env file")
            logger.info("Example: MONGODB_CONNECTION_STRING=mongodb+srv://username:password@cluster.mongodb.net/")
    
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
    
    def get_all_users(self, collection_name: str = "testcol") -> List[Dict[str, Any]]:
        """
        Fetch all user documents from the specified collection.
        
        Args:
            collection_name (str): Name of the collection to query (default: "testcol")
            
        Returns:
            List[Dict[str, Any]]: List of all user documents
        """
        try:
            if self.db is None:
                logger.error("Not connected to database. Call connect() first.")
                return []
            
            collection = self.db[collection_name]
            
            # Fetch all documents
            users = list(collection.find({}))
            
            # Convert ObjectId to string for JSON serialization
            for user in users:
                if '_id' in user:
                    user['_id'] = str(user['_id'])
            
            logger.info(f"Retrieved {len(users)} users from {collection_name}")
            return users
            
        except Exception as e:
            logger.error(f"Error fetching users: {str(e)}")
            return []
    
    def get_user_by_id(self, user_id: str, collection_name: str = "testcol") -> Optional[Dict[str, Any]]:
        """
        Fetch a specific user by their ID.
        
        Args:
            user_id (str): The user's ObjectId as string
            collection_name (str): Name of the collection to query
            
        Returns:
            Optional[Dict[str, Any]]: User document or None if not found
        """
        try:
            from bson import ObjectId
            
            if self.db is None:
                logger.error("Not connected to database. Call connect() first.")
                return None
            
            collection = self.db[collection_name]
            user = collection.find_one({"_id": ObjectId(user_id)})
            
            if user:
                user['_id'] = str(user['_id'])
                logger.info(f"Found user: {user.get('name', 'Unknown')}")
            else:
                logger.info(f"No user found with ID: {user_id}")
            
            return user
            
        except Exception as e:
            logger.error(f"Error fetching user by ID: {str(e)}")
            return None
    
    def get_users_by_profession(self, profession: str, collection_name: str = "testcol") -> List[Dict[str, Any]]:
        """
        Fetch users by their profession.
        
        Args:
            profession (str): The profession to search for
            collection_name (str): Name of the collection to query
            
        Returns:
            List[Dict[str, Any]]: List of matching user documents
        """
        try:
            if self.db is None:
                logger.error("Not connected to database. Call connect() first.")
                return []
            
            collection = self.db[collection_name]
            
            # Case-insensitive search
            users = list(collection.find({"profession": {"$regex": profession, "$options": "i"}}))
            
            # Convert ObjectId to string
            for user in users:
                if '_id' in user:
                    user['_id'] = str(user['_id'])
            
            logger.info(f"Found {len(users)} users with profession: {profession}")
            return users
            
        except Exception as e:
            logger.error(f"Error fetching users by profession: {str(e)}")
            return []
    
    def get_collection_stats(self, collection_name: str = "testcol") -> Dict[str, Any]:
        """
        Get statistics about the collection.
        
        Args:
            collection_name (str): Name of the collection
            
        Returns:
            Dict[str, Any]: Collection statistics
        """
        try:
            if self.db is None:
                logger.error("Not connected to database. Call connect() first.")
                return {}
            
            collection = self.db[collection_name]
            
            # Get collection stats
            stats = {
                "total_documents": collection.count_documents({}),
                "collection_name": collection_name,
                "database_name": self.database_name
            }
            
            # Get unique professions
            professions = collection.distinct("profession")
            stats["unique_professions"] = professions
            stats["profession_count"] = len(professions)
            
            # Get unique specialties
            specialties = collection.distinct("specialty")
            stats["unique_specialties"] = specialties
            stats["specialty_count"] = len(specialties)
            
            logger.info(f"Collection stats: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}")
            return {}


def main():
    """Example usage of the MongoDB client."""
    
    # Create client instance
    mongo_client = MongoDBClient()
    
    # Connect to database
    if not mongo_client.connect():
        print("Failed to connect to MongoDB. Please check your connection string.")
        return
    
    try:
        print("=" * 50)
        print("MONGODB DATA RETRIEVAL")
        print("=" * 50)
        
        # Get collection statistics
        print("\n📊 Collection Statistics:")
        stats = mongo_client.get_collection_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # Fetch all users
        print(f"\n👥 All Users:")
        users = mongo_client.get_all_users()
        
        if users:
            for i, user in enumerate(users, 1):
                print(f"\n  User {i}:")
                print(f"    ID: {user.get('_id', 'N/A')}")
                print(f"    Name: {user.get('name', 'N/A')}")
                print(f"    Slack Name: {user.get('slackname', 'N/A')}")
                print(f"    Profession: {user.get('profession', 'N/A')}")
                print(f"    Specialty: {user.get('specialty', 'N/A')}")
        else:
            print("  No users found.")
        
        # Example: Get users by profession
        print(f"\n🎨 Designers:")
        designers = mongo_client.get_users_by_profession("designer")
        for designer in designers:
            print(f"  - {designer.get('name', 'N/A')} ({designer.get('slackname', 'N/A')})")
        
        print(f"\n💻 Programmers:")
        programmers = mongo_client.get_users_by_profession("programmer")
        for programmer in programmers:
            print(f"  - {programmer.get('name', 'N/A')} ({programmer.get('slackname', 'N/A')})")
        
    finally:
        # Always disconnect
        mongo_client.disconnect()


if __name__ == "__main__":
    main()
