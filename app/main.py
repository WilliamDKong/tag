from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from app.routers import users, tags, links, redirect
from app.templates_engine import render

app = FastAPI(title="TapTag")

app.include_router(users.router)
app.include_router(tags.router)
app.include_router(links.router)
app.include_router(redirect.router)


@app.get("/")
async def root():
    return render("login.html")


@app.get("/activate")
async def activate_page(id: str):
    return render("activate.html", tag_id=id)


@app.get("/login")
async def login_page():
    return render("login.html")


@app.get("/my-tags")
async def my_tags_page():
    return render("my_tags.html")


@app.get("/{tag_id}")
async def short_link(tag_id: str):
    """短链接：taptag.cc/TAG001 → /r?id=TAG001"""
    return RedirectResponse(url=f"/r?id={tag_id}")
