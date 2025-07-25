from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio

from mongodb.task_service import task_service, TaskService

# Initialize router
router = APIRouter(prefix="/api", tags=["tasks"])

# Pydantic models for request/response
class TaskCreate(BaseModel):
    title: str
    description: str
    progress: int = 0
    status: str = "active"
    assignedTo: Optional[str] = None
    relayedFrom: Optional[str] = None
    estimatedHandoff: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    progress: Optional[int] = None
    status: Optional[str] = None
    assignedTo: Optional[str] = None
    relayedFrom: Optional[str] = None
    estimatedHandoff: Optional[str] = None

class TaskResponse(BaseModel):
    _id: str
    title: str
    description: str
    progress: int
    status: str
    assignedTo: Optional[str] = None
    relayedFrom: Optional[str] = None
    estimatedHandoff: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class TaskAssign(BaseModel):
    assignedTo: str

class TaskProgress(BaseModel):
    progress: int

class TaskRelay(BaseModel):
    from_user: str
    to_user: str

# Dependency to ensure MongoDB connection
async def get_task_service():
    if not task_service.db:
        if not task_service.connect():
            raise HTTPException(status_code=500, detail="Database connection failed")
    return task_service

@router.post("/tasks", response_model=TaskResponse)
async def create_task(
    task_data: TaskCreate,
    service: TaskService = Depends(get_task_service)
):
    """Create a new task."""
    try:
        task_dict = task_data.dict()
        created_task = await service.create_task(task_dict)
        
        if not created_task:
            raise HTTPException(status_code=500, detail="Failed to create task")
        
        return TaskResponse(**created_task)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating task: {str(e)}")

@router.get("/tasks", response_model=List[TaskResponse])
async def get_tasks(
    service: TaskService = Depends(get_task_service)
):
    """Get all tasks."""
    try:
        tasks = await service.get_all_tasks()
        return [TaskResponse(**task) for task in tasks]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tasks: {str(e)}")

@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    service: TaskService = Depends(get_task_service)
):
    """Get a specific task by ID."""
    try:
        task = await service.get_task_by_id(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return TaskResponse(**task)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching task: {str(e)}")

@router.get("/tasks/user/{user_id}", response_model=List[TaskResponse])
async def get_tasks_by_user(
    user_id: str,
    service: TaskService = Depends(get_task_service)
):
    """Get all tasks assigned to a specific user."""
    try:
        tasks = await service.get_tasks_by_user(user_id)
        return [TaskResponse(**task) for task in tasks]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user tasks: {str(e)}")

@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_data: TaskUpdate,
    service: TaskService = Depends(get_task_service)
):
    """Update a task."""
    try:
        # Remove None values
        update_data = {k: v for k, v in task_data.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No valid fields to update")
        
        updated_task = await service.update_task(task_id, update_data)
        
        if not updated_task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return TaskResponse(**updated_task)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating task: {str(e)}")

@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: str,
    service: TaskService = Depends(get_task_service)
):
    """Delete a task."""
    try:
        success = await service.delete_task(task_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return {"message": "Task deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting task: {str(e)}")

@router.put("/tasks/{task_id}/assign", response_model=TaskResponse)
async def assign_task(
    task_id: str,
    assign_data: TaskAssign,
    service: TaskService = Depends(get_task_service)
):
    """Assign a task to a user."""
    try:
        updated_task = await service.assign_task(task_id, assign_data.assignedTo)
        
        if not updated_task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return TaskResponse(**updated_task)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error assigning task: {str(e)}")

@router.put("/tasks/{task_id}/progress", response_model=TaskResponse)
async def update_task_progress(
    task_id: str,
    progress_data: TaskProgress,
    service: TaskService = Depends(get_task_service)
):
    """Update task progress."""
    try:
        updated_task = await service.update_task_progress(task_id, progress_data.progress)
        
        if not updated_task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return TaskResponse(**updated_task)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating task progress: {str(e)}")

@router.post("/tasks/{task_id}/relay", response_model=TaskResponse)
async def relay_task(
    task_id: str,
    relay_data: TaskRelay,
    service: TaskService = Depends(get_task_service)
):
    """Relay a task from one user to another."""
    try:
        updated_task = await service.relay_task(
            task_id, 
            relay_data.from_user, 
            relay_data.to_user
        )
        
        if not updated_task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return TaskResponse(**updated_task)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error relaying task: {str(e)}") 