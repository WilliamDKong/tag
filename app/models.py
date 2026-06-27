from sqlalchemy import Column, String, Text, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)           # 随机生成的唯一ID
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    tags = relationship("NFCTag", back_populates="user")


class NFCTag(Base):
    __tablename__ = "nfc_tags"

    id = Column(String(10), primary_key=True)        # 5位短码，如 W67B9
    user_id = Column(String, ForeignKey("users.id"), nullable=True)  # NULL = 未绑定
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
