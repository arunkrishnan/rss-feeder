from fastapi import APIRouter

from app.api.v1 import users, feeds, login

api_router = APIRouter()
api_router.include_router(login.router, prefix="/login", tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(feeds.router, prefix="/feeds", tags=["feeds"])
