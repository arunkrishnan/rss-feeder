from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class FeedInDBBase(BaseModel):
    id: Optional[int] = None
    url: str = None
    name: str = None

    class Config:
        orm_mode = True


class Feed(FeedInDBBase):
    pass


class FeedCreate(BaseModel):
    url: str = None
    name: str = None


class PostCreate(BaseModel):
    title: str = None
    link: str = None
    description: str = None
    published_at: datetime = None
    uid: str = None
    author: str = None
