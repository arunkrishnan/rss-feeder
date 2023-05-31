from datetime import datetime
from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey

from app.db.base_class import Base


class UserPost(Base):
    """
    ORM for the view user_post
    """

    __tablename__ = "user_post"

    post_id = Column(Integer, ForeignKey("post.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    feed_id = Column(Integer, ForeignKey("feed.id"), nullable=False)
    is_read = Column(Boolean, default=False, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    title = Column(String(255), nullable=False)
    content = Column(String, nullable=True)
    author = Column(String(255), nullable=True)
    link = Column(String(255), nullable=True)
    published_at = Column(DateTime, nullable=True)
