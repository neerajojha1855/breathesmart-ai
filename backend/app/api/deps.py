"""Dependencies for session authentication, database sessions, and CSRF protection."""

from datetime import datetime, timedelta, timezone
from typing import Annotated
import uuid
from fastapi import Cookie, Depends, Header, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.exceptions import CSRFError, InvalidSessionError
from app.core.security import (
    generate_csrf_token,
    generate_session_token,
    get_cookie_settings,
    hash_token,
    verify_csrf_token,
)
from app.db.session import get_db
from app.models.profile import UserProfile
from app.models.session import UserSession


async def get_or_create_session(
    request: Request,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
    breathe_smart_session: Annotated[str | None, Cookie()] = None,
    authorization: Annotated[str | None, Header()] = None,
) -> UserSession:
    """Retrieve existing session from cookie/header or securely provision a new one."""
    raw_token = breathe_smart_session
    if not raw_token and authorization and authorization.startswith("Bearer "):
        raw_token = authorization.split(" ")[1]

    now = datetime.now(timezone.utc)

    if raw_token:
        token_h = hash_token(raw_token)
        stmt = (
            select(UserSession)
            .options(selectinload(UserSession.profile))
            .where(
                UserSession.token_hash == token_h,
                UserSession.expires_at > now,
            )
        )
        result = await db.execute(stmt)
        session_obj = result.scalar_one_or_none()
        if session_obj:
            session_obj.last_activity_at = now
            await db.commit()
            return session_obj

    # Provision fresh anonymous session
    new_token = generate_session_token()
    new_hash = hash_token(new_token)
    expires = now + timedelta(seconds=settings.SESSION_LIFETIME_SECONDS)

    new_session = UserSession(
        id=uuid.uuid4(),
        token_hash=new_hash,
        created_at=now,
        expires_at=expires,
        last_activity_at=now,
    )
    db.add(new_session)

    # Initialize associated profile
    new_profile = UserProfile(
        id=uuid.uuid4(),
        session_id=new_session.id,
        preferred_language="en",
        household_preferences={},
        commuting_preferences={},
        indoor_environment_preferences={},
        sensitive_group_consent=False,
    )
    db.add(new_profile)
    await db.commit()
    await db.refresh(new_session)

    # Set secure HttpOnly session cookie
    cookie_opts = get_cookie_settings()
    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=new_token,
        **cookie_opts,
    )

    # Provide CSRF token for state-changing operations
    csrf_token = generate_csrf_token()
    response.set_cookie(
        key="breathe_smart_csrf",
        value=csrf_token,
        httponly=False,  # Accessible to client JS for double-submit header
        samesite="lax",
        secure=settings.ENVIRONMENT.lower() == "production",
        path="/",
    )

    return new_session


def verify_csrf(
    request: Request,
    x_csrf_token: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
    breathe_smart_csrf: Annotated[str | None, Cookie()] = None,
) -> None:
    """Guard mutating HTTP requests using double-submit CSRF verification."""
    if request.method in ("POST", "PUT", "DELETE", "PATCH"):
        # Allow requests with Authorization Bearer header to bypass cookie CSRF
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return
        if not verify_csrf_token(x_csrf_token, breathe_smart_csrf):
            raise CSRFError("Invalid or missing CSRF token in X-CSRF-Token header")
