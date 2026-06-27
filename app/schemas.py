from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class LinkCreate(BaseModel):
    label: str
    url: str


class LinkUpdate(BaseModel):
    label: str | None = None
    url: str | None = None


class LinkReorder(BaseModel):
    link_ids: list[int]  # 拖拽后的新顺序，传入 id 列表
