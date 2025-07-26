from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio

from mongodb.user_service import user_service, UserService
from temporal_workflows.service import temporal_service

# Initialize router
router = APIRouter(prefix="/api", tags=["users"])

# Pydantic models for request/response
class UserCreate(BaseModel):
    name: str
    avatar: Optional[str] = None
    status: str = "idle"

class UserUpdate(BaseModel):
    name: Optional[str] = None
    avatar: Optional[str] = None
    status: Optional[str] = None

class UserResponse(BaseModel):
    _id: str
    name: str
    avatar: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

class UserStatusUpdate(BaseModel):
    status: str

# Dependency to ensure MongoDB connection
async def get_user_service():
    if not user_service.db:
        if not user_service.connect():
            raise HTTPException(status_code=500, detail="Database connection failed")
    return user_service

@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service)
):
    """Create a new user with onboarding workflow integration."""
    try:
        user_dict = user_data.dict()
        created_user = await service.create_user(user_dict)
        
        if not created_user:
            raise HTTPException(status_code=500, detail="Failed to create user")
        
        # Start user onboarding workflow
        user_id = str(created_user["_id"])
        onboarding_data = {
            "user_id": user_id,
            "name": created_user["name"],
            "created_at": created_user["created_at"].isoformat()
        }
        
        try:
            workflow_id = await temporal_service.start_user_onboarding_workflow(onboarding_data)
            # You might want to store the workflow_id in the user document
        except Exception as e:
            # Log the error but don't fail user creation
            print(f"Warning: Could not start onboarding workflow for user {user_id}: {e}")
        
        return UserResponse(**created_user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")

@router.get("/users", response_model=List[UserResponse])
async def get_users(
    service: UserService = Depends(get_user_service)
):
    """Get all users."""
    try:
        users = await service.get_all_users()
        return [UserResponse(**user) for user in users]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching users: {str(e)}")

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    service: UserService = Depends(get_user_service)
):
    """Get a specific user by ID."""
    try:
        user = await service.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse(**user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user: {str(e)}")

@router.get("/users/name/{name}", response_model=UserResponse)
async def get_user_by_name(
    name: str,
    service: UserService = Depends(get_user_service)
):
    """Get a user by name."""
    try:
        user = await service.get_user_by_name(name)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse(**user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user: {str(e)}")

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    service: UserService = Depends(get_user_service)
):
    """Update a user."""
    try:
        # Remove None values
        update_data = {k: v for k, v in user_data.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No valid fields to update")
        
        updated_user = await service.update_user(user_id, update_data)
        
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse(**updated_user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating user: {str(e)}")

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    service: UserService = Depends(get_user_service)
):
    """Delete a user."""
    try:
        success = await service.delete_user(user_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {"message": "User deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting user: {str(e)}")

@router.put("/users/{user_id}/status", response_model=UserResponse)
async def update_user_status(
    user_id: str,
    status_data: UserStatusUpdate,
    service: UserService = Depends(get_user_service)
):
    """Update user status."""
    try:
        updated_user = await service.update_user_status(user_id, status_data.status)
        
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse(**updated_user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating user status: {str(e)}") 