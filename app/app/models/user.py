from datetime import datetime

from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    subscriptions = relationship("Subscription", back_populates="user")


class Subscription(Base):
    __tablename__ = "user_subscription"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    feed_id = Column(Integer, ForeignKey("feed.id"), nullable=False)
    feed = relationship("Feed", back_populates="subscriptions")
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    user = relationship("User", back_populates="subscriptions")
    is_active = Column(Boolean, default=True, nullable=False)


class PostReadStatus(Base):
    __tablename__ = "post_read_status"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("post.id"), nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
