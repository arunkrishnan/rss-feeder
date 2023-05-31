from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.feed import Feed, FeedCreate
from app.repository.feed import repo as feed_repo
from app.core.celery_app import celery_app

router = APIRouter()


@router.get("/", response_model=List[Feed])
def get_feeds(
    db: Session = Depends(deps.get_db),
    offset: int = 0,
    limit: int = 100,
) -> Any:
    feeds = feed_repo.get_feeds(db, offset=offset, limit=limit)
    return feeds


@router.post("/", status_code=201, response_model=Feed, description="Add a new feed")
def create_feed(*, db: Session = Depends(deps.get_db), request: FeedCreate) -> Any:
    existing_feed = feed_repo.get_feed_by_url_or_name(
        db, url=request.url, name=request.name
    )
    if existing_feed:
        if existing_feed.url == request.url:
            raise HTTPException(
                status_code=400,
                detail="Feed with this url already exists",
            )
        elif existing_feed.name == request.name:
            raise HTTPException(
                status_code=400,
                detail="Feed with this name already exists",
            )

    feed = feed_repo.create_feed(db, obj_in=request)
    return feed


@router.post("/refresh/{feed_id}", description="Update feed posts")
def refresh_feed(
    feed_id: int,
    db: Session = Depends(deps.get_db),
):
    feed = feed_repo.get(db, id=feed_id)
    if feed:
        celery_app.send_task("app.scheduler.tasks.refresh_feed", args=(feed_id, True))
    else:
        raise HTTPException(
            status_code=404,
            detail="Feed not found",
        )

    return {"message": "Feed refreshed successfully"}
