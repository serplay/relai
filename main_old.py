import os
import secrets
from datetime import datetime, timedelta
from typing import Optional

import requests
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", "30"))
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Google OAuth URLs
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

# FastAPI app
app = FastAPI(title="Google OAuth API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Pydantic models
class GoogleOAuthRequest(BaseModel):
    code: str
    redirect_uri: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user_info: dict

class UserInfo(BaseModel):
    id: str
    email: str
    name: str
    picture: Optional[str] = None

# JWT utility functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(datetime.timezone.utc) + expires_delta
    else:
        expire = datetime.now(datetime.timezone.utc) + timedelta(minutes=JWT_EXPIRATION_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

# Google OAuth functions
def exchange_code_for_token(code: str, redirect_uri: str):
    """Exchange authorization code for access token from Google"""
    data = {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
    }
    
    response = requests.post(GOOGLE_TOKEN_URL, data=data)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to exchange code for token")
    
    return response.json()

def get_user_info(access_token: str):
    """Get user information from Google using access token"""
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(GOOGLE_USER_INFO_URL, headers=headers)
    
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to get user information")
    
    return response.json()

# API Routes
@app.get("/")
async def root():
    return {"message": "Google OAuth API is running"}

@app.get("/auth/google/url")
async def get_google_auth_url():
    """Get Google OAuth authorization URL"""
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/auth?"
        f"client_id={GOOGLE_CLIENT_ID}&"
        f"redirect_uri={FRONTEND_URL}/auth/callback&"
        f"scope=openid%20email%20profile&"
        f"response_type=code&"
        f"access_type=offline"
    )
    return {"auth_url": google_auth_url}

@app.post("/auth/google/token", response_model=TokenResponse)
async def google_oauth_token(oauth_request: GoogleOAuthRequest):
    """Exchange Google OAuth code for JWT token"""
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=500, 
            detail="Google OAuth credentials not configured"
        )
    
    try:
        # Exchange code for Google access token
        token_data = exchange_code_for_token(oauth_request.code, oauth_request.redirect_uri)
        google_access_token = token_data.get("access_token")
        
        if not google_access_token:
            raise HTTPException(status_code=400, detail="Failed to get access token from Google")
        
        # Get user information from Google
        user_info = get_user_info(google_access_token)
        
        # Create JWT token for our app
        access_token_expires = timedelta(minutes=JWT_EXPIRATION_MINUTES)
        access_token = create_access_token(
            data={"sub": user_info["id"], "email": user_info["email"]},
            expires_delta=access_token_expires
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=JWT_EXPIRATION_MINUTES * 60,
            user_info=user_info
        )
        
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"OAuth request failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/auth/me", response_model=UserInfo)
async def get_current_user(token_data: dict = Depends(verify_token)):
    """Get current user information from JWT token"""
    return UserInfo(
        id=token_data["sub"],
        email=token_data["email"],
        name=token_data.get("name", ""),
        picture=token_data.get("picture")
    )

@app.get("/protected")
async def protected_route(token_data: dict = Depends(verify_token)):
    """Example protected route that requires authentication"""
    return {
        "message": "This is a protected route",
        "user_id": token_data["sub"],
        "email": token_data["email"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)