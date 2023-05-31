from typing import Optional
from pydantic import BaseModel


class SubscriptionBase(BaseModel):
    is_active: Optional[bool] = True


class SubscriptionCreate(BaseModel):
    feed_id: int
    user_id: int


class SubscriptionUpdate(SubscriptionBase):
    id: int


class SubscriptionDBBase(SubscriptionBase):
    id: int

    class Config:
        orm_mode = True


class Subscription(SubscriptionDBBase):
    pass
