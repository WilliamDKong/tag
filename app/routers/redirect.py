from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import NFCTag, TagLink, ModeEnum
from app.templates_engine import render

router = APIRouter(tags=["redirect"])


@router.get("/r")
async def scan_redirect(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(NFCTag).where(NFCTag.id == id))
    tag = result.scalar_one_or_none()

    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")

    if tag.user_id is None:
        return RedirectResponse(url=f"/activate?id={id}")

    links_result = await db.execute(
        select(TagLink).where(TagLink.tag_id == id).order_by(TagLink.sort_order)
    )
    links = links_result.scalars().all()

    if tag.current_mode == ModeEnum.DIRECT:
        # 直接跳转第一条链接
        if not links:
            return render("links.html", links=[], tag_id=id)
        return RedirectResponse(url=links[0].url, status_code=302)

    else:
        # DISPLAY 模式：展示链接列表
        links_data = [{"label": l.label, "url": l.url} for l in links]
        return render("links.html", links=links_data, tag_id=id)
