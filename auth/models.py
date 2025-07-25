from typing import Optional
from pydantic import BaseModel


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
