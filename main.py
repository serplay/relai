from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import asyncio
import logging

from auth.routes import router as auth_router
from slackBot.routes import router as slack_bot_router
from task_routes import router as task_router
from user_routes import router as user_router
from workflow_routes import router as workflow_router
from temporal_workflows.service import temporal_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# FastAPI app
app = FastAPI(title="RelAI", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include auth routes
app.include_router(auth_router)

# Include slack bot routes
app.include_router(slack_bot_router)

# Include task routes
app.include_router(task_router)

# Include user routes
app.include_router(user_router)

# Include workflow routes
app.include_router(workflow_router)

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("Starting RelAI application...")
    
    # Start periodic cleanup workflow
    try:
        cleanup_workflow_id = await temporal_service.start_periodic_cleanup_workflow()
        logger.info(f"Periodic cleanup workflow started: {cleanup_workflow_id}")
    except Exception as e:
        logger.warning(f"Could not start periodic cleanup workflow: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down RelAI application...")


@app.get("/")
async def root():
    return {"message": "RelAI API is running with Temporal integration"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "RelAI",
        "timestamp": "2025-01-25T00:00:00Z",
        "temporal_integration": "enabled"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
