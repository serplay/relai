# MongoDB Migration from Supabase

This document outlines the migration from Supabase to MongoDB for the RelAI project.

## Overview

The project has been successfully migrated from Supabase to MongoDB, providing a more flexible and scalable database solution. The migration includes both backend services and frontend integration.

## What Was Changed

### Backend Changes

1. **New MongoDB Services**:
   - `mongodb/user_service.py` - Handles user operations
   - `mongodb/task_service.py` - Handles task operations (existing, enhanced)
   - `mongodb/workflow_service.py` - Handles workflow operations

2. **New API Routes**:
   - `user_routes.py` - User management endpoints
   - `workflow_routes.py` - Workflow management endpoints
   - `task_routes.py` - Task management endpoints (existing, enhanced)

3. **Updated Main Application**:
   - `main.py` - Now includes all new routes

### Frontend Changes

1. **New MongoDB Integration**:
   - `frontend/src/integrations/mongodb/client.ts` - MongoDB API client
   - `frontend/src/integrations/mongodb/types.ts` - TypeScript types for MongoDB

2. **New API Service**:
   - `frontend/src/services/mongodbApi.ts` - MongoDB API service

3. **Updated Components**:
   - `frontend/src/components/TaskManager.tsx` - Updated to use MongoDB API

## Database Schema

### Users Collection
```json
{
  "_id": "ObjectId",
  "name": "string",
  "avatar": "string (optional)",
  "status": "working" | "idle",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Tasks Collection
```json
{
  "_id": "ObjectId",
  "title": "string",
  "description": "string",
  "progress": "number (0-100)",
  "status": "active" | "waiting" | "completed",
  "assignedTo": "string (user ID)",
  "relayedFrom": "string (user ID, optional)",
  "estimatedHandoff": "string (optional)",
  "relayedAt": "datetime (optional)",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

## API Endpoints

### Users
- `GET /api/users` - Get all users
- `POST /api/users` - Create a new user
- `GET /api/users/{user_id}` - Get user by ID
- `GET /api/users/name/{name}` - Get user by name
- `PUT /api/users/{user_id}` - Update user
- `DELETE /api/users/{user_id}` - Delete user
- `PUT /api/users/{user_id}/status` - Update user status

### Tasks
- `GET /api/tasks` - Get all tasks
- `POST /api/tasks` - Create a new task
- `GET /api/tasks/{task_id}` - Get task by ID
- `GET /api/tasks/user/{user_id}` - Get tasks by user
- `PUT /api/tasks/{task_id}` - Update task
- `DELETE /api/tasks/{task_id}` - Delete task
- `PUT /api/tasks/{task_id}/assign` - Assign task to user
- `PUT /api/tasks/{task_id}/progress` - Update task progress
- `POST /api/tasks/{task_id}/relay` - Relay task between users

### Workflows
- `GET /api/workflows/{user_id}` - Get user workflow
- `GET /api/workflows` - Get all workflows
- `GET /api/workflows/stats` - Get workflow statistics

## Environment Variables

Make sure to set the following environment variables:

```bash
MONGODB_CONNECTION_STRING=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DATABASE=relai
```

## Testing

Run the test script to verify the MongoDB integration:

```bash
python test_mongodb_integration.py
```

## Migration Steps

1. **Set up MongoDB**:
   - Create a MongoDB Atlas cluster or local MongoDB instance
   - Set the connection string in your environment variables

2. **Install Dependencies**:
   ```bash
   pip install pymongo
   ```

3. **Start the Backend**:
   ```bash
   python main.py
   ```

4. **Test the API**:
   ```bash
   python test_mongodb_integration.py
   ```

5. **Start the Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Benefits of MongoDB Migration

1. **Flexibility**: MongoDB's document-based structure allows for more flexible data modeling
2. **Scalability**: Better horizontal scaling capabilities
3. **Performance**: Optimized for read/write operations
4. **Cost**: Potentially lower costs compared to managed Supabase
5. **Control**: Full control over the database and its configuration

## Known Issues

1. **Frontend Type Errors**: Some TypeScript errors remain in the TaskManager component due to property name mismatches between the old Supabase schema and new MongoDB schema. These need to be resolved for full functionality.

2. **Data Migration**: Existing Supabase data needs to be migrated to MongoDB if required.

## Next Steps

1. Fix remaining TypeScript errors in the frontend
2. Migrate existing data from Supabase (if needed)
3. Add comprehensive error handling
4. Implement data validation
5. Add authentication integration with MongoDB
6. Set up proper indexing for performance optimization

## Support

For issues or questions about the MongoDB migration, please refer to:
- MongoDB documentation: https://docs.mongodb.com/
- PyMongo documentation: https://pymongo.readthedocs.io/
- FastAPI documentation: https://fastapi.tiangolo.com/ 