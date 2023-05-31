from datetime import datetime
import time

import feedparser
from typing import Optional
from sqlalchemy.orm import Session

from app.api import deps
from app.core.celery_app import celery_app
from app.repository.feed import repo as feed_repo
from app.schemas.feed import PostCreate

retry_count_map = [2 * 60, 5 * 60, 8 * 60]


@celery_app.task
def refresh_all_feed():
    db: Session = next(deps.get_db())
    total_feed_to_refresh = feed_repo.get_feeds_count(
        db=db, is_active=True, max_fail_count=3
    )

    for offset in range(0, total_feed_to_refresh, 100):
        feeds = feed_repo.get_feeds(
            db=db, is_active=True, max_fail_count=3, offset=offset, limit=100
        )
        for feed in feeds:
            celery_app.send_task("app.scheduler.tasks.refresh_feed", args=(feed.id,))
    return "refresh job started"


@celery_app.task
def refresh_feed(feed_id: int, forcce: Optional[bool] = False, retry_count: int = 0):
    db: Session = next(deps.get_db())
    feed = feed_repo.get_feed_by_id(db=db, id=feed_id)
    if not feed:
        return "no feed to refresh"
    if feed.failed_attempts > 3 and not forcce:
        return "feed failed more than 3 times"
    url = feed.url
    try:
        current_feed = feedparser.parse(url)
    except Exception as e:
        feed_repo.update_failure_count(
            db=db, id=feed_id, failed_attempts=feed.failed_attempts + 1
        )
        retry_if_required(feed_id=feed_id, retry_count=retry_count)
        return "Failed to parse feed"
    if current_feed.bozo:
        feed_repo.update_failure_count(
            db=db, id=feed_id, failed_attempts=feed.failed_attempts + 1
        )
        retry_if_required(feed_id=feed_id, retry_count=retry_count)
        return "Failed to parse feed"
    
    if not current_feed.entries:
        feed_repo.update_failure_count(db=db, id=feed_id, failed_attempts=0)
        return "no new posts"

    try:
        posts = [
            PostCreate(
                title=entry.title,
                uid=entry.id,
                link=entry.link,
                description=entry.summary,
                published_at=datetime.fromtimestamp(time.mktime(entry.published_parsed)),
            )
            for entry in current_feed.entries
        ]

        feed_repo.batch_insert_posts(db=db, feed_id=feed_id, posts=posts)
        feed_repo.update_failure_count(db=db, id=feed_id, failed_attempts=0)
        return f"succesfully refreshed feed {feed_id}"
    except Exception as e:
        feed_repo.update_failure_count(
            db=db, id=feed_id, failed_attempts=feed.failed_attempts + 1
        )
        retry_if_required(feed_id=feed_id, retry_count=retry_count)
        return "Failed to update posts"

def retry_if_required(feed_id: int, retry_count: int):
    if retry_count < len(retry_count_map):
        celery_app.send_task(
            "app.scheduler.tasks.refresh_feed",
            args=(feed_id, False, retry_count + 1),
            countdown=retry_count_map[retry_count],
        )