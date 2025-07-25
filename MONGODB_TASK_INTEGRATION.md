# MongoDB Task Integration

This document describes the MongoDB integration for task management in the RelAI frontend.

## Overview

The frontend has been updated to use MongoDB for persistent task storage instead of in-memory data. This provides:

- **Persistent Storage**: Tasks are saved to MongoDB and survive server restarts
- **Scalability**: Can handle large numbers of tasks efficiently
- **Data Integrity**: ACID compliance and proper indexing
- **Real-time Updates**: Tasks can be updated and retrieved in real-time

## Architecture

### Backend Components

1. **TaskService** (`mongodb/task_service.py`)
   - MongoDB client wrapper for task operations
   - Handles CRUD operations for tasks
   - Manages connections and error handling

2. **Task Routes** (`task_routes.py`)
   - FastAPI router with REST endpoints
   - Handles HTTP requests for task operations
   - Validates request/response data with Pydantic models

3. **Main App** (`main.py`)
   - Includes task routes in the FastAPI application
   - Provides `/api/tasks` endpoints

### Frontend Components

1. **API Service** (`frontend/src/services/relaiApi.ts`)
   - Updated to use MongoDB-based endpoints
   - Changed from `https://relai.es/api` to `http://localhost:8000/api`
   - Updated Task interface to use `_id` instead of `id`

2. **TaskManager Component** (`frontend/src/components/TaskManager.tsx`)
   - Updated to work with MongoDB task structure
   - Uses `_id` field for task identification

## API Endpoints

### Task Management

- `POST /api/tasks` - Create a new task
- `GET /api/tasks` - Get all tasks
- `GET /api/tasks/{task_id}` - Get a specific task
- `GET /api/tasks/user/{user_id}` - Get tasks by user
- `PUT /api/tasks/{task_id}` - Update a task
- `DELETE /api/tasks/{task_id}` - Delete a task

### Task Operations

- `PUT /api/tasks/{task_id}/assign` - Assign task to user
- `PUT /api/tasks/{task_id}/progress` - Update task progress
- `POST /api/tasks/{task_id}/relay` - Relay task between users

## Data Models

### Task Schema

```typescript
interface Task {
  _id: string;                    // MongoDB ObjectId as string
  title: string;                  // Task title
  description: string;            // Task description
  progress: number;               // Progress percentage (0-100)
  status: 'active' | 'waiting' | 'completed';
  assignedTo?: string;            // User ID assigned to task
  relayedFrom?: string;           // User who relayed the task
  estimatedHandoff?: string;      // Estimated time to handoff
  created_at: string;             // ISO timestamp
  updated_at: string;             // ISO timestamp
  relayedAt?: string;             // When task was relayed
}
```

## Setup Instructions

### 1. Environment Variables

Copy the example environment file and configure it:

```bash
cp env.example .env
```

Then edit `.env` and update the following variables:

```bash
# MongoDB Configuration (Required for task storage)
MONGODB_CONNECTION_STRING=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DATABASE=relai

# Other required services
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token-here
SLACK_APP_TOKEN=xapp-your-slack-app-token-here
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
JWT_SECRET=your-super-secret-jwt-key-here
OPENAI_API_KEY=sk-your-openai-api-key-here
```

### 2. Dependencies

Install required Python packages:

```bash
pip install pymongo python-dotenv fastapi
```

### 3. Start the Backend

```bash
python main.py
```

The server will start on `http://localhost:8000`

### 4. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

## Testing

Run the MongoDB integration test:

```bash
python test_mongodb_tasks.py
```

This will test all CRUD operations and verify the integration is working correctly.

## Migration Notes

### Breaking Changes

1. **Task ID Field**: Changed from `id` to `_id` to match MongoDB ObjectId
2. **API Base URL**: Changed from `https://relai.es/api` to `http://localhost:8000/api`
3. **Task Structure**: Added `created_at` and `updated_at` timestamps

### Frontend Updates Required

The TaskManager component has been partially updated but may need additional fixes for:

- Mock data structure compatibility
- Type definitions for task objects
- Error handling for MongoDB operations

## Troubleshooting

### Common Issues

1. **Connection Failed**: Check MongoDB connection string in `.env`
2. **CORS Errors**: Ensure frontend is running on the correct port
3. **Type Errors**: Update TypeScript interfaces to match MongoDB schema

### Debug Mode

Enable debug logging by setting:

```python
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

1. **Real-time Updates**: Implement WebSocket connections for live task updates
2. **Task History**: Add comprehensive task history and audit trails
3. **Bulk Operations**: Support for bulk task creation and updates
4. **Advanced Queries**: Add filtering, sorting, and pagination
5. **Task Templates**: Predefined task templates for common workflows 