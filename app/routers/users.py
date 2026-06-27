import uuid
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import User
from app.schemas import UserRegister, UserLogin
from app.auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register")
async def register(data: UserRegister, response: Response, db: AsyncSession = Depends(get_db)):
    """注册新用户"""
    # 检查邮箱是否已被注册
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="邮箱已被注册")

    user = User(
        id=str(uuid.uuid4()),
        email=data.email,
        hashed_password=hash_password(data.password),
    )
    db.add(user)
    await db.commit()

    # 注册完自动登录，把 JWT 写入 Cookie
    token = create_access_token(user.id)
    response.set_cookie("access_token", token, httponly=True, max_age=604800)
    return {"message": "注册成功", "user_id": user.id}


@router.post("/login")
async def login(data: UserLogin, response: Response, db: AsyncSession = Depends(get_db)):
    """用户登录"""
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="邮箱或密码错误")

    token = create_access_token(user.id)
    response.set_cookie("access_token", token, httponly=True, max_age=604800)
    return {"message": "登录成功"}


@router.post("/logout")
async def logout(response: Response):
    """退出登录，清除 Cookie"""
    response.delete_cookie("access_token")
    return {"message": "已退出"}
