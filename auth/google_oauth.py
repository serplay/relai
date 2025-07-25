import os
from datetime import timedelta

import requests
from fastapi import HTTPException
from dotenv import load_dotenv

from .jwt_handler import create_access_token, get_jwt_config

# Load environment variables
load_dotenv()

# Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Google OAuth URLs
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


def get_google_auth_url():
    """Generate Google OAuth authorization URL"""
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=500, 
            detail="Google OAuth Client ID not configured"
        )
    
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/auth?"
        f"client_id={GOOGLE_CLIENT_ID}&"
        f"redirect_uri={FRONTEND_URL}/auth/callback&"
        f"scope=openid%20email%20profile&"
        f"response_type=code&"
        f"access_type=offline"
    )
    return {"auth_url": google_auth_url}


def exchange_code_for_token(code: str, redirect_uri: str):
    """Exchange authorization code for access token from Google"""
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=500, 
            detail="Google OAuth credentials not configured"
        )
    
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


def process_google_oauth(code: str, redirect_uri: str):
    """Complete Google OAuth flow and return JWT token with user info"""
    try:
        # Exchange code for Google access token
        token_data = exchange_code_for_token(code, redirect_uri)
        google_access_token = token_data.get("access_token")
        
        if not google_access_token:
            raise HTTPException(status_code=400, detail="Failed to get access token from Google")
        
        # Get user information from Google
        user_info = get_user_info(google_access_token)
        
        # Create JWT token for our app
        jwt_config = get_jwt_config()
        access_token_expires = timedelta(minutes=jwt_config["expiration_minutes"])
        access_token = create_access_token(
            data={"sub": user_info["id"], "email": user_info["email"]},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": jwt_config["expiration_minutes"] * 60,
            "user_info": user_info
        }
        
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"OAuth request failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
