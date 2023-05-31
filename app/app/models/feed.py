from datetime import datetime

from app.db.base_class import Base

from sqlalchemy.orm import relationship
from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, DateTime


class Feed(Base):
    __tablename__ = "feed"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    url = Column(String(255), nullable=False, unique=True)
    name = Column(String(255), nullable=False, unique=True)
    refreshed_at = Column(DateTime, default=datetime.utcnow)
    failed_attempts = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    posts = relationship("Post", back_populates="feed")
    subscriptions = relationship("Subscription", back_populates="feed")


class Post(Base):
    __tablename__ = "post"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    feed_id = Column(Integer, ForeignKey("feed.id"), nullable=False)
    feed = relationship("Feed", back_populates="posts")
    title = Column(String(255), nullable=False)
    content = Column(String, nullable=False)
    author = Column(String(255), nullable=True)
    link = Column(String(255), nullable=False, unique=True)
    uid = Column(String(255), nullable=False, unique=True)
    published_at = Column(DateTime, nullable=False)
