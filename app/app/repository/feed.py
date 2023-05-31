from datetime import datetime
from typing import Optional, List
from sqlalchemy import or_
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.models.feed import Feed, Post
from app.schemas.feed import FeedCreate, PostCreate


class FeedRepo:
    def get(self, db: Session, id: int) -> Optional[Feed]:
        return db.query(Feed).filter(Feed.id == id).first()

    def get_feeds(
        self,
        db: Session,
        *,
        offset: int,
        limit: int,
        is_active: bool = None,
        max_fail_count: int = None,
    ) -> Optional[List[Feed]]:
        query = db.query(Feed)
        if is_active is not None:
            query = query.filter(Feed.is_active == is_active)
        if max_fail_count is not None:
            query = query.filter(Feed.failed_attempts <= max_fail_count)
        return query.offset(offset).limit(limit).all()

    def get_feeds_count(
        self,
        db: Session,
        is_active: bool = None,
        max_fail_count: int = None,
    ) -> Optional[int]:
        query = db.query(Feed)
        if is_active is not None:
            query = query.filter(Feed.is_active == is_active)
        if max_fail_count is not None:
            query = query.filter(Feed.failed_attempts <= max_fail_count)
        return query.count()

    def get_feed_by_id(self, db: Session, *, id: int) -> Optional[Feed]:
        return db.query(Feed).filter(Feed.id == id).first()

    def get_feed_by_url_or_name(
        self, db: Session, *, url: str, name: str
    ) -> Optional[Feed]:
        return db.query(Feed).filter(or_(Feed.url == url, Feed.name == name)).first()

    def create_feed(self, db: Session, *, obj_in: FeedCreate) -> Optional[Feed]:
        db_obj = Feed(
            url=obj_in.url,
            name=obj_in.name,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_failure_count(self, db: Session, *, id: int, failed_attempts: int):
        db_obj = db.query(Feed).filter(Feed.id == id).first()
        db_obj.failed_attempts = failed_attempts
        db_obj.refreshed_at = datetime.utcnow()
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def batch_insert_posts(self, db: Session, *, feed_id: int, posts: List[PostCreate]):
        insert_stmt = (
            insert(Post)
            .values(
                [
                    {
                        "feed_id": feed_id,
                        "title": post.title,
                        "link": post.link,
                        "uid": post.uid,
                        "content": post.description,
                        "author": post.author,
                        "published_at": post.published_at,
                    }
                    for post in posts
                ]
            )
            .on_conflict_do_nothing()
        )

        db.execute(insert_stmt)
        db.commit()


repo = FeedRepo()
