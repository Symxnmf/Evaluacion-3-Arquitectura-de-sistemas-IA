from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer(auto_error=False)


def create_token(subject: str = "shopfast-user") -> str:
    secret = os.getenv("JWT_SECRET", "development-only-change-me")
    minutes = int(os.getenv("JWT_EXPIRATION_MINUTES", "60"))
    payload = {
        "sub": subject,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=minutes),
    }
    return jwt.encode(
        payload,
        secret,
        algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
    )


def require_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token required",
        )
    secret = os.getenv("JWT_SECRET", "development-only-change-me")
    try:
        return jwt.decode(
            credentials.credentials,
            secret,
            algorithms=[os.getenv("JWT_ALGORITHM", "HS256")],
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc

