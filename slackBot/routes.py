import os
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from dotenv import load_dotenv

# Import the LLM parser and slack interface from the same folder
from .llm_parser import parse_task
from .slack_interface import send_to_slack, test_slack_connection

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
        slack_error = None
        
        try:
            # Check if Slack is properly configured first
            bot_token = os.getenv('SLACK_BOT_TOKEN')
            app_token = os.getenv('SLACK_APP_TOKEN')
            
            if not bot_token or not app_token:
                slack_error = "Slack tokens not configured"
            elif bot_token == "xoxb-your-bot-token-here" or app_token == "xapp-your-app-token-here":
                slack_error = "Slack tokens are placeholder values - please update your .env file"
            else:
                # Attempt to send to Slack
                result = send_to_slack(parsed_task)
                if result:
                    slack_sent = True
                else:
                    slack_error = "Slack sending failed - check your configuration"
                    
        except Exception as e:
            slack_error = f"Slack sending error: {str(e)}"
            print(f"Slack sending failed: {e}")
        
        # Determine the appropriate message
        if slack_sent:
            message = f"Task parsed and sent to Slack successfully"
        elif slack_error:
            message = f"Task parsed successfully, but Slack sending failed: {slack_error}"
        else:
            message = "Task parsed successfully"
        
        return TaskResponse(
            success=True,
            parsed_task=parsed_task,
            message=message,
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