import random
import string
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import NFCTag, User
from app.auth import get_current_user
from app.templates_engine import render

router = APIRouter(prefix="/tags", tags=["tags"])


def generate_tag_id(length=5) -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


@router.post("/create")
async def create_tag(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    while True:
        tag_id = generate_tag_id()
        result = await db.execute(select(NFCTag).where(NFCTag.id == tag_id))
        if not result.scalar_one_or_none():
            break

    tag = NFCTag(id=tag_id, user_id=current_user.id)
    db.add(tag)
    await db.commit()
    return {"tag_id": tag_id, "message": "标签创建成功"}


@router.post("/bind/{tag_id}")
async def bind_tag(
    tag_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(NFCTag).where(NFCTag.id == tag_id))
    tag = result.scalar_one_or_none()

    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")
    if tag.user_id is not None:
        raise HTTPException(status_code=400, detail="标签已被绑定")

    tag.user_id = current_user.id
    await db.commit()
    return {"message": "绑定成功"}


@router.get("/my")
async def get_my_tags(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(NFCTag).where(NFCTag.user_id == current_user.id))
    tags = result.scalars().all()
    return [{"id": t.id, "created_at": t.created_at} for t in tags]


@router.get("/dashboard/{tag_id}")
async def dashboard(
    tag_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(NFCTag).where(NFCTag.id == tag_id))
    tag = result.scalar_one_or_none()

    if not tag or tag.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问")

    return render("dashboard.html", tag_id=tag_id)
