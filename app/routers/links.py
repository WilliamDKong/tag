from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import NFCTag, TagLink, User
from app.schemas import LinkCreate, LinkUpdate, LinkReorder
from app.auth import get_current_user

router = APIRouter(prefix="/links", tags=["links"])


async def get_tag_for_user(tag_id: str, user: User, db: AsyncSession) -> NFCTag:
    """验证标签属于当前用户"""
    result = await db.execute(select(NFCTag).where(NFCTag.id == tag_id))
    tag = result.scalar_one_or_none()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")
    if tag.user_id != user.id:
        raise HTTPException(status_code=403, detail="无权操作此标签")
    return tag


@router.get("/{tag_id}")
async def get_links(
    tag_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取标签下所有链接"""
    await get_tag_for_user(tag_id, current_user, db)
    result = await db.execute(
        select(TagLink).where(TagLink.tag_id == tag_id).order_by(TagLink.sort_order)
    )
    links = result.scalars().all()
    return [{"id": l.id, "label": l.label, "url": l.url, "sort_order": l.sort_order} for l in links]


@router.post("/{tag_id}")
async def add_link(
    tag_id: str,
    data: LinkCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """添加一条链接"""
    await get_tag_for_user(tag_id, current_user, db)

    # 新链接排在最后
    result = await db.execute(select(TagLink).where(TagLink.tag_id == tag_id))
    count = len(result.scalars().all())

    link = TagLink(tag_id=tag_id, label=data.label, url=data.url, sort_order=count)
    db.add(link)
    await db.commit()
    return {"message": "链接添加成功", "id": link.id}


@router.patch("/{tag_id}/{link_id}")
async def update_link(
    tag_id: str,
    link_id: int,
    data: LinkUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """修改链接的文字或网址"""
    await get_tag_for_user(tag_id, current_user, db)

    result = await db.execute(select(TagLink).where(TagLink.id == link_id, TagLink.tag_id == tag_id))
    link = result.scalar_one_or_none()
    if not link:
        raise HTTPException(status_code=404, detail="链接不存在")

    if data.label is not None:
        link.label = data.label
    if data.url is not None:
        link.url = data.url
    await db.commit()
    return {"message": "链接更新成功"}


@router.delete("/{tag_id}/{link_id}")
async def delete_link(
    tag_id: str,
    link_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除一条链接"""
    await get_tag_for_user(tag_id, current_user, db)

    result = await db.execute(select(TagLink).where(TagLink.id == link_id, TagLink.tag_id == tag_id))
    link = result.scalar_one_or_none()
    if not link:
        raise HTTPException(status_code=404, detail="链接不存在")

    await db.delete(link)
    await db.commit()
    return {"message": "链接删除成功"}


@router.post("/{tag_id}/reorder")
async def reorder_links(
    tag_id: str,
    data: LinkReorder,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """拖拽排序：传入新的 id 顺序列表，更新 sort_order"""
    await get_tag_for_user(tag_id, current_user, db)

    for index, link_id in enumerate(data.link_ids):
        result = await db.execute(select(TagLink).where(TagLink.id == link_id, TagLink.tag_id == tag_id))
        link = result.scalar_one_or_none()
        if link:
            link.sort_order = index

    await db.commit()
    return {"message": "排序更新成功"}
