from sqlalchemy import Column, String, Text, Integer, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class ModeEnum(str, enum.Enum):
    DIRECT = "DIRECT"      # 直接跳转第一条链接
    DISPLAY = "DISPLAY"    # 展示链接列表供访客选择


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    tags = relationship("NFCTag", back_populates="user")


class NFCTag(Base):
    __tablename__ = "nfc_tags"

    id = Column(String(10), primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    current_mode = Column(Enum(ModeEnum), default=ModeEnum.DIRECT, nullable=False, server_default="DIRECT")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="tags")
    links = relationship("TagLink", back_populates="tag", order_by="TagLink.sort_order")


class TagLink(Base):
    __tablename__ = "tag_links"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tag_id = Column(String(10), ForeignKey("nfc_tags.id"), nullable=False)
    label = Column(String(100), nullable=False)      # 按钮文字，如 "我的 GitHub"
    url = Column(Text, nullable=False)               # 目标网址
    sort_order = Column(Integer, default=0)          # 排序权重，拖拽时更新

    tag = relationship("NFCTag", back_populates="links")
