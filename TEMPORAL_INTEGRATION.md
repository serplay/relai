# Temporal Integration for RelAI

This document explains how Temporal.io is integrated into the RelAI application for workflow orchestration and task management.

## Overview

Temporal is integrated to handle:
- **Task Lifecycle Management**: Automated task creation, assignment, and monitoring
- **Task Relay Workflows**: Coordinated task handoffs between users
- **User Onboarding**: Automated onboarding process for new users
- **Periodic Cleanup**: Scheduled maintenance tasks
- **Notifications**: Reliable delivery of notifications and reminders

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │────│ Temporal Client │────│ Temporal Server │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                                              │
         │                                              │
         ▼                                              ▼
┌─────────────────┐                           ┌─────────────────┐
│   MongoDB       │                           │ Temporal Worker │
│   (Data Store)  │                           │ (Workflows &    │
└─────────────────┘                           │ Activities)     │
                                               └─────────────────┘
```

## Workflows

### 1. TaskLifecycleWorkflow
- **Purpose**: Manages the complete lifecycle of a task
- **Duration**: Up to 30 days
- **Features**:
  - Automated task creation
  - User assignment and notifications
  - Deadline monitoring and alerts
  - Progress tracking

**Usage**:
```python
workflow_id = await temporal_service.start_task_lifecycle_workflow({
    "title": "Complete project documentation",
    "description": "Write comprehensive docs",
    "assignedTo": "user123",
    "estimatedHandoff": "2025-01-30T00:00:00Z"
})
```

### 2. TaskRelayWorkflow
- **Purpose**: Handles task handoffs between users
- **Duration**: ~10 minutes
- **Features**:
  - Automated task reassignment
  - Notification to both users
  - Workflow state tracking

**Usage**:
```python
workflow_id = await temporal_service.start_task_relay_workflow(
    task_id="task123",
    from_user="user1",
    to_user="user2",
    message="Please handle this urgent task"
)
```

### 3. UserOnboardingWorkflow
- **Purpose**: Automates new user onboarding
- **Duration**: Up to 7 days
- **Features**:
  - Welcome notifications
  - Onboarding task creation
  - Follow-up reminders

**Usage**:
```python
workflow_id = await temporal_service.start_user_onboarding_workflow({
    "user_id": "user123",
    "name": "John Doe",
    "created_at": "2025-01-25T00:00:00Z"
})
```

### 4. PeriodicCleanupWorkflow
- **Purpose**: Scheduled maintenance and cleanup
- **Duration**: Runs indefinitely
- **Features**:
  - Daily execution
  - Old task cleanup
  - System maintenance

## Activities

Activities are the building blocks that perform actual work:

- `create_task_activity`: Creates tasks in MongoDB
- `update_task_activity`: Updates task information
- `assign_task_activity`: Assigns tasks to users
- `relay_task_activity`: Handles task relays
- `send_notification_activity`: Sends notifications
- `check_task_deadline_activity`: Monitors deadlines
- `cleanup_completed_tasks_activity`: Cleanup operations

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start Temporal Server (Development)
```bash
# Install Temporal CLI first:
# brew install temporal (macOS)
# or download from https://github.com/temporalio/cli

temporal server start-dev
```

### 3. Configure Environment
Copy `.env.example` to `.env` and configure:
```bash
TEMPORAL_HOST=localhost:7233
TEMPORAL_NAMESPACE=default
TEMPORAL_TASK_QUEUE=relai-task-queue
```

### 4. Start Temporal Worker
```bash
./start_temporal_worker.sh
```

### 5. Start FastAPI Application
```bash
python main.py
```

## API Integration

The FastAPI routes automatically trigger Temporal workflows:

### Task Creation
```bash
POST /api/tasks
{
  "title": "New Task",
  "description": "Task description",
  "assignedTo": "user123"
}
```
→ Triggers `TaskLifecycleWorkflow`

### Task Relay
```bash
POST /api/tasks/{task_id}/relay
{
  "from_user": "user1",
  "to_user": "user2",
  "message": "Relay message"
}
```
→ Triggers `TaskRelayWorkflow`

### User Creation
```bash
POST /api/users
{
  "name": "John Doe",
  "status": "active"
}
```
→ Triggers `UserOnboardingWorkflow`

## Monitoring

### Health Check
```bash
GET /health
```
Returns Temporal integration status.

### Workflow Status
```python
status = await temporal_service.get_workflow_status("workflow-id")
```

### Temporal Web UI
Access the Temporal Web UI at: http://localhost:8233

## Signals

Workflows can receive signals for dynamic updates:

### Mark Task Complete
```python
await temporal_service.signal_task_completed("workflow-id")
```

### Task Reassignment
```python
await temporal_service.signal_task_reassigned("workflow-id", "new-user")
```

## Production Considerations

### 1. Temporal Server
- Use Temporal Cloud or self-hosted cluster
- Configure proper authentication
- Set up monitoring and alerts

### 2. Database
- Ensure MongoDB connection pooling
- Configure proper indexes for performance
- Set up database monitoring

### 3. Error Handling
- Configure retry policies
- Set up proper logging
- Monitor workflow failures

### 4. Scaling
- Run multiple worker instances
- Configure task queue partitioning
- Monitor worker capacity

## Development

### Running Tests
```bash
# Test MongoDB integration
python test_mongodb_integration.py

# Test Temporal workflows (requires running Temporal server)
python -m pytest temporal_workflows/tests/
```

### Adding New Workflows
1. Create workflow in `temporal_workflows/workflows.py`
2. Add activities in `temporal_workflows/activities.py`
3. Register in `temporal_workflows/worker.py`
4. Add service methods in `temporal_workflows/service.py`
5. Integrate with FastAPI routes

### Debugging
- Use Temporal Web UI for workflow visualization
- Check worker logs for activity execution
- Monitor FastAPI logs for integration issues

## Troubleshooting

### Common Issues

1. **"Connection refused" errors**: Ensure Temporal server is running
2. **"Task queue not found"**: Check task queue configuration in .env
3. **Workflow not starting**: Verify worker is running and registered
4. **Activity timeouts**: Adjust timeout configurations in workflows

### Logs
- FastAPI: Check application logs
- Temporal: Check worker output and Web UI
- MongoDB: Check database connection logs
