from typing import Optional
from app.models.user import User, Subscription, PostReadStatus
from app.models.user_post import UserPost
from app.schemas.user import SignupRequest
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password


class UserRepo:
    def get(self, db: Session, id: int) -> Optional[User]:
        return db.query(User).filter(User.id == id).first()

    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, *, obj_in: SignupRequest) -> User:
        db_obj = User(
            email=obj_in.email,
            password=get_password_hash(obj_in.password),
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user

    def get_feed_subscription(
        self, db: Session, *, user_id: int, feed_id: int
    ) -> Optional[Subscription]:
        return (
            db.query(Subscription)
            .filter(Subscription.user_id == user_id, Subscription.feed_id == feed_id)
            .first()
        )

    def create_feed_subscription(
        self, db: Session, *, user_id: int, feed_id: int
    ) -> Optional[Subscription]:
        db_obj = Subscription(
            user_id=user_id,
            feed_id=feed_id,
            is_active=True,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def activate_feed_subscription(
        self, db: Session, *, id: int
    ) -> Optional[Subscription]:
        db_obj = db.query(Subscription).filter(Subscription.id == id).first()
        db_obj.is_active = True
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def deactivate_feed_subscription(
        self, db: Session, *, id: int
    ) -> Optional[Subscription]:
        db_obj = db.query(Subscription).filter(Subscription.id == id).first()
        db_obj.is_active = False
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_posts(
        self,
        db: Session,
        *,
        user_id: int,
        feed_id: Optional[int],
        is_read: Optional[bool],
        offset: int = 0,
        limit: int = 100
    ) -> Optional[UserPost]:
        query = db.query(UserPost).filter(UserPost.user_id == user_id)

        if feed_id is not None:
            query = query.filter(UserPost.feed_id == feed_id)

        if is_read is not None:
            query = query.filter(UserPost.is_read == is_read)

        return query.offset(offset).limit(limit).all()

    def mark_post_as_read(
        self, db: Session, *, user_id: int, post_id: int
    ) -> Optional[UserPost]:
        db_obj = (
            db.query(PostReadStatus)
            .filter(
                PostReadStatus.user_id == user_id, PostReadStatus.post_id == post_id
            )
            .first()
        )
        if db_obj:
            db_obj.is_read = True
        else:
            db_obj = PostReadStatus(
                user_id=user_id,
                post_id=post_id,
                is_read=True,
            )
            db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def mark_post_as_unread(
        self, db: Session, *, user_id: int, post_id: int
    ) -> Optional[UserPost]:
        db_obj = (
            db.query(PostReadStatus)
            .filter(
                PostReadStatus.user_id == user_id, PostReadStatus.post_id == post_id
            )
            .first()
        )
        if db_obj:
            db_obj.is_read = False
            return db_obj


repo = UserRepo()
