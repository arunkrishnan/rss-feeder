from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class SignupRequest(BaseModel):
    email: str = None
    password: str = None

    class Config:
        schema_extra = {"example": {"email": "user1@app.com", "password": "password"}}


class User(BaseModel):
    id: int
    email: str

    class Config:
        orm_mode = True


class UserPost(BaseModel):
    user_id: int
    post_id: int
    is_read: bool
    created_at: datetime
    feed_id: int
    title: str
    link: str
    content: str
    author: Optional[str]
    published_at: datetime

    class Config:
        orm_mode = True


class Subscription(BaseModel):
    id: int
    user_id: int
    feed_id: int
    is_active: bool

    class Config:
        orm_mode = True
