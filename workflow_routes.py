from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio

from mongodb.workflow_service import workflow_service, WorkflowService

# Initialize router
router = APIRouter(prefix="/api", tags=["workflows"])

# Pydantic models for request/response
class WorkflowData(BaseModel):
    activeWork: Optional[Dict[str, Any]] = None
    incoming: List[Dict[str, Any]] = []
    recentHandoffs: List[Dict[str, Any]] = []

class WorkflowStats(BaseModel):
    active_tasks: int
    waiting_tasks: int
    completed_tasks: int
    total_tasks: int
    total_users: int

# Dependency to ensure MongoDB connection
async def get_workflow_service():
    if not workflow_service.db:
        if not workflow_service.connect():
            raise HTTPException(status_code=500, detail="Database connection failed")
    return workflow_service

@router.get("/workflows/{user_id}", response_model=WorkflowData)
async def get_user_workflow(
    user_id: str,
    service: WorkflowService = Depends(get_workflow_service)
):
    """Get workflow data for a specific user."""
    try:
        workflow = await service.get_user_workflow(user_id)
        return WorkflowData(**workflow)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user workflow: {str(e)}")

@router.get("/workflows", response_model=Dict[str, WorkflowData])
async def get_all_workflows(
    service: WorkflowService = Depends(get_workflow_service)
):
    """Get workflow data for all users."""
    try:
        workflows = await service.get_all_workflows()
        # Convert to proper response format
        response = {}
        for user_id, workflow in workflows.items():
            response[user_id] = WorkflowData(**workflow)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching all workflows: {str(e)}")

@router.get("/workflows/stats", response_model=WorkflowStats)
async def get_workflow_stats(
    service: WorkflowService = Depends(get_workflow_service)
):
    """Get workflow statistics."""
    try:
        stats = await service.get_workflow_stats()
        return WorkflowStats(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching workflow stats: {str(e)}") 