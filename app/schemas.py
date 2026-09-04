from pydantic import BaseModel, EmailStr, field_validator
import re


class UserRegister(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[0-9!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", v):
            raise ValueError("Password must contain a number or special character")
        return v


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


class ModeSwitch(BaseModel):
    mode: str  # "DIRECT" 或 "DISPLAY"


class NicknameUpdate(BaseModel):
    nickname: str | None = None


class ProfileUpdate(BaseModel):
    profile_name: str | None = None
    bio: str | None = None
