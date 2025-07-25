from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from auth.routes import router as auth_router
from slackBot.routes import router as slack_bot_router

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


@app.get("/")
async def root():
    return {"message": "Google OAuth API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
