from fastapi import APIRouter, Depends

from .models import GoogleOAuthRequest, TokenResponse, UserInfo
from .google_oauth import get_google_auth_url, process_google_oauth
from .jwt_handler import verify_token

# Create router for auth endpoints
router = APIRouter(prefix="/auth", tags=["authentication"])


@router.get("/google/url")
async def google_auth_url():
    """Get Google OAuth authorization URL"""
    return get_google_auth_url()


@router.post("/google/token", response_model=TokenResponse)
async def google_oauth_token(oauth_request: GoogleOAuthRequest):
    """Exchange Google OAuth code for JWT token"""
    token_data = process_google_oauth(oauth_request.code, oauth_request.redirect_uri)
    return TokenResponse(**token_data)


@router.get("/me", response_model=UserInfo)
async def get_current_user(token_data: dict = Depends(verify_token)):
    """Get current user information from JWT token"""
    return UserInfo(
        id=token_data["sub"],
        email=token_data["email"],
        name=token_data.get("name", ""),
        picture=token_data.get("picture")
    )


@router.get("/protected")
async def protected_route(token_data: dict = Depends(verify_token)):
    """Example protected route that requires authentication"""
    return {
        "message": "This is a protected route",
        "user_id": token_data["sub"],
        "email": token_data["email"]
    }
