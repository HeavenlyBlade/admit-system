"""
Google OAuth router for ADMIT system.
Handles Google sign-in, callback, and current-user endpoint.
"""
import os
import httpx
import logging
from urllib.parse import urlencode
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from itsdangerous import TimestampSigner, SignatureExpired, BadSignature

from db.database import get_db
from models.schemas import User
from auth.jwt_handler import create_access_token, decode_token

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Auth"])

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
GOOGLE_STATE_SECRET = os.getenv("GOOGLE_STATE_SECRET", "changeme-state-secret")

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

# Optional OAuth2 bearer — auto_error=False so unauthenticated requests return None
oauth2_scheme_optional = OAuth2PasswordBearer(
    tokenUrl="/api/auth/token",
    auto_error=False
)


async def get_optional_user(
    token: Optional[str] = Depends(oauth2_scheme_optional),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """
    Dependency that returns the User ORM object if a valid Bearer token is
    provided, or None if there is no token or the token is invalid.
    """
    if not token:
        return None
    try:
        payload = decode_token(token)
        user_id = int(payload.get("sub", 0))
        if not user_id:
            return None
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()
    except Exception:
        return None


@router.get("/google")
async def google_login():
    """Redirect user to Google OAuth consent screen."""
    signer = TimestampSigner(GOOGLE_STATE_SECRET)
    state = signer.sign("oauth").decode()

    params = urlencode({
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": f"{BACKEND_URL}/api/auth/google/callback",
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
    })

    return RedirectResponse(url=f"{GOOGLE_AUTH_URL}?{params}")


@router.get("/google/callback")
async def google_callback(
    code: str,
    state: str,
    db: AsyncSession = Depends(get_db),
):
    """Handle Google OAuth callback, upsert user, issue JWT, redirect to frontend."""
    # 1. Verify state
    signer = TimestampSigner(GOOGLE_STATE_SECRET)
    try:
        signer.unsign(state, max_age=600)
    except (SignatureExpired, BadSignature):
        raise HTTPException(status_code=400, detail="Invalid or expired OAuth state")

    # 2. Exchange code for access token
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": f"{BACKEND_URL}/api/auth/google/callback",
                "grant_type": "authorization_code",
            },
        )
        token_data = token_resp.json()
        access_token = token_data.get("access_token")
        if not access_token:
            logger.error("Google token exchange failed: %s", token_data)
            raise HTTPException(status_code=400, detail="Failed to obtain access token from Google")

        # 3. Fetch user info
        userinfo_resp = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        userinfo = userinfo_resp.json()

    google_id = userinfo.get("sub")
    email = userinfo.get("email")
    name = userinfo.get("name", email)
    avatar_url = userinfo.get("picture")

    if not google_id or not email:
        raise HTTPException(status_code=400, detail="Incomplete user info from Google")

    # 4. Upsert user
    result = await db.execute(select(User).where(User.google_id == google_id))
    user = result.scalars().first()

    if user:
        user.name = name
        user.avatar_url = avatar_url
        user.last_login = datetime.utcnow()
    else:
        user = User(
            google_id=google_id,
            email=email,
            name=name,
            avatar_url=avatar_url,
        )
        db.add(user)

    await db.flush()
    await db.commit()
    await db.refresh(user)

    # 5. Create JWT
    jwt_token = create_access_token({
        "sub": str(user.id),
        "email": user.email,
        "name": user.name,
        "avatar_url": user.avatar_url,
    })

    # 6. Redirect to frontend with token
    return RedirectResponse(url=f"{FRONTEND_URL}/chat?token={jwt_token}")


@router.get("/me")
async def get_me(
    token: Optional[str] = Depends(oauth2_scheme_optional),
    db: AsyncSession = Depends(get_db),
):
    """Return current authenticated user info."""
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = decode_token(token)
        user_id = int(payload.get("sub", 0))
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "avatar_url": user.avatar_url,
    }
