from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session
from app.repository.user import repo as user_repo
from app.api import deps
from app.schemas.user import SignupRequest, User, UserPost

router = APIRouter()


@router.post(
    "/signup", response_model=User, status_code=201, description="Signup a new user"
)
def signup(*, db: Session = Depends(deps.get_db), request: SignupRequest) -> Any:
    user = user_repo.get_by_email(db, email=request.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )

    user = user_repo.create(db, obj_in=request)

    return user


@router.post("/follow/{feed_id}")
def follow_feed(
    feed_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    user_id = current_user.id

    subscription = user_repo.get_feed_subscription(
        db=db, user_id=user_id, feed_id=feed_id
    )
    if subscription:
        if subscription.is_active:
            raise HTTPException(
                status_code=400,
                detail="You are already following this feed",
            )
        else:
            user_repo.activate_feed_subscription(db=db, id=subscription.id)
    else:
        user_repo.create_feed_subscription(db=db, user_id=user_id, feed_id=feed_id)

    return {"message": "Followed feed successfully"}


@router.post("/unfollow/{feed_id}")
def unfollow_feed(
    feed_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    user_id = current_user.id

    subscription = user_repo.get_feed_subscription(
        db=db, user_id=user_id, feed_id=feed_id
    )
    if subscription and subscription.is_active:
        user_repo.deactivate_feed_subscription(db=db, id=subscription.id)
    else:
        raise HTTPException(
            status_code=400,
            detail="You are not following this feed",
        )

    return {"message": "Unfollowed feed successfully"}


@router.get("/posts", response_model=List[UserPost])
def get_posts(
    db: Session = Depends(deps.get_db),
    feed_id: Optional[int] = None,
    is_read: Optional[bool] = None,
    offset: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
):
    user_id = current_user.id
    return user_repo.get_posts(
        db=db, user_id=user_id, feed_id=feed_id, is_read=is_read, offset=offset, limit=limit
    )


@router.post("/posts/{post_id}/read")
def mark_post_as_read(
    post_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    user_id = current_user.id
    user_repo.mark_post_as_read(db, user_id=user_id, post_id=post_id)

    return {"message": "Post marked as read"}


@router.post("/posts/{post_id}/unread")
def mark_post_as_unread(
    post_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    user_id = current_user.id
    user_repo.mark_post_as_unread(db, user_id=user_id, post_id=post_id)

    return {"message": "Post marked as unread"}
