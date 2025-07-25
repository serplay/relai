import os
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from dotenv import load_dotenv

# Import the LLM parser from the slackBot module
import sys
sys.path.append('slackBot')
from llm_parser import parse_task
from slack_interface import send_to_slack, test_slack_connection

load_dotenv()

router = APIRouter(prefix="/slack-bot", tags=["slack-bot"])

class TaskRequest(BaseModel):
    raw_text: str
    user_id: Optional[str] = None

class TaskResponse(BaseModel):
    success: bool
    parsed_task: Optional[Dict[str, Any]] = None
    message: str
    slack_sent: bool = False

class SlackStatusResponse(BaseModel):
    connected: bool
    message: str

@router.post("/parse-task", response_model=TaskResponse)
async def parse_and_send_task(task_request: TaskRequest):
    """
    Parse a natural language task and optionally send it to Slack
    """
    try:
        # Parse the task using the LLM parser
        parsed_task = parse_task(task_request.raw_text)
        
        # Try to send to Slack if configured
        slack_sent = False
        try:
            send_to_slack(parsed_task)
            slack_sent = True
        except Exception as e:
            # Slack sending failed, but parsing succeeded
            print(f"Slack sending failed: {e}")
        
        return TaskResponse(
            success=True,
            parsed_task=parsed_task,
            message="Task parsed successfully",
            slack_sent=slack_sent
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse task: {str(e)}"
        )

@router.post("/parse-only", response_model=TaskResponse)
async def parse_task_only(task_request: TaskRequest):
    """
    Parse a natural language task without sending to Slack
    """
    try:
        parsed_task = parse_task(task_request.raw_text)
        
        return TaskResponse(
            success=True,
            parsed_task=parsed_task,
            message="Task parsed successfully",
            slack_sent=False
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse task: {str(e)}"
        )

@router.get("/status", response_model=SlackStatusResponse)
async def get_slack_status():
    """
    Check if Slack integration is properly configured and connected
    """
    try:
        connected = test_slack_connection()
        return SlackStatusResponse(
            connected=connected,
            message="Slack connection tested successfully" if connected else "Slack connection failed"
        )
    except Exception as e:
        return SlackStatusResponse(
            connected=False,
            message=f"Slack connection error: {str(e)}"
        )

@router.get("/config")
async def get_slack_config():
    """
    Get Slack configuration status (without exposing sensitive tokens)
    """
    config = {
        "openai_configured": bool(os.getenv('OPENAI_API_KEY')),
        "slack_bot_configured": bool(os.getenv('SLACK_BOT_TOKEN')),
        "slack_app_configured": bool(os.getenv('SLACK_APP_TOKEN')),
        "default_channel": os.getenv('SLACK_DEFAULT_CHANNEL', 'general')
    }
    
    return {
        "config": config,
        "all_configured": all([
            config["openai_configured"],
            config["slack_bot_configured"],
            config["slack_app_configured"]
        ])
    } 