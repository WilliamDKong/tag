import os
import uuid
import time
from collections import defaultdict
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import User
from app.schemas import UserRegister, UserLogin
from app.auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/users", tags=["users"])

# ── Simple in-memory rate limiter ──────────────────────────────────────────
# { ip: [(timestamp, ...), ...] }
_rate_store: dict[str, list[float]] = defaultdict(list)
RATE_LIMIT   = 10       # max attempts
RATE_WINDOW  = 60       # per N seconds

def _check_rate(ip: str) -> None:
    now = time.monotonic()
    hits = [t for t in _rate_store[ip] if now - t < RATE_WINDOW]
    if len(hits) >= RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Too many attempts. Please wait a minute.")
    hits.append(now)
    _rate_store[ip] = hits

def _is_production() -> bool:
    return os.getenv("ENV", "development").lower() == "production"

def _set_auth_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=604800,          # 7 days
        samesite="lax",
        secure=_is_production(), # HTTPS-only in prod
    )

# ── Routes ──────────────────────────────────────────────────────────────────

@router.post("/register")
async def register(
    request: Request,
    data: UserRegister,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    ip = request.client.host
    _check_rate(ip)

    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="An account with this email already exists.")

    user = User(
        id=str(uuid.uuid4()),
        email=data.email,
        hashed_password=hash_password(data.password),
    )
    db.add(user)
    await db.commit()

    token = create_access_token(user.id)
    _set_auth_cookie(response, token)
    return {"message": "Account created.", "user_id": user.id}


@router.post("/login")
async def login(
    request: Request,
    data: UserLogin,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    ip = request.client.host
    _check_rate(ip)

    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")

    token = create_access_token(user.id)
    _set_auth_cookie(response, token)
    return {"message": "Logged in."}


@router.post("/logout")
async def logout(response: Response):
    """退出登录，清除 Cookie"""
    response.delete_cookie("access_token")
    from fastapi.responses import RedirectResponse
    res = RedirectResponse(url="/login", status_code=302)
    res.delete_cookie("access_token")
    return res
