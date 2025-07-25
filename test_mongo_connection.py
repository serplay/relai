from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# Replace <db_password> with your actual password
uri = "mongodb+srv://Johannes:<db_password>@awshack.xxdtd9n.mongodb.net/?retryWrites=true&w=majority&appName=awsHack"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("✅ Pinged your deployment. You successfully connected to MongoDB!")
    
    # Test database access
    db = client.relai  # or whatever your database name is
    collections = db.list_collection_names()
    print(f"✅ Database 'relai' accessible. Collections: {collections}")
    
except Exception as e:
    print(f"❌ Connection failed: {e}")

finally:
    client.close() 