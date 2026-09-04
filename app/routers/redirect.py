from fastapi import APIRouter, Depends
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

    if not tag or tag.user_id is None:
        return RedirectResponse(url=f"/activate?id={id}")

    links_result = await db.execute(
        select(TagLink).where(TagLink.tag_id == id).order_by(TagLink.sort_order)
    )
    links = links_result.scalars().all()

    if tag.current_mode == ModeEnum.DIRECT:
        if not links:
            return render("profile.html", links=[], tag=_tag_ctx(tag))
        return RedirectResponse(url=links[0].url, status_code=302)

    links_data = [{"label": l.label, "url": l.url} for l in links]
    return render("profile.html", links=links_data, tag=_tag_ctx(tag))


def _tag_ctx(tag: NFCTag) -> dict:
    return {
        "id": tag.id,
        "profile_name": tag.profile_name or "",
        "bio": tag.bio or "",
    }
