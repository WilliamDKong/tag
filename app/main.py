from fastapi import FastAPI, Request
from app.routers import users, tags, links, redirect
from app.templates_engine import render

app = FastAPI(title="Tagging")

app.include_router(users.router)
app.include_router(tags.router)
app.include_router(links.router)
app.include_router(redirect.router)


@app.get("/")
async def root():
    return {"message": "Tagging API is running"}


@app.get("/activate")
async def activate_page(id: str):
    """首次扫码激活页"""
    return render("activate.html", tag_id=id)
