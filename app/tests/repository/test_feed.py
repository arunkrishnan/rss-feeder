from datetime import datetime
from typing import List

# from sqlalchemy.orm import Session

from app.models.feed import Feed, Post
from app.schemas.feed import FeedCreate, PostCreate
from app.repository.feed import FeedRepo


def test_get_feed_by_id(client, db):
    feed = Feed(url="https://testfeed/1", name="Example Feed 1")
    db.add(feed)
    db.commit()

    # Test getting the feed by ID
    retrieved_feed = FeedRepo().get_feed_by_id(db=db, id=feed.id)
    assert retrieved_feed is not None
    assert retrieved_feed.id == feed.id
    assert retrieved_feed.url == feed.url
    assert retrieved_feed.name == feed.name


def test_get_feed_by_url_or_name(client, db):
    # Create a feed in the database
    feed = Feed(url="https://testfeed/2", name="Example Feed 2")
    db.add(feed)
    db.commit()

    # Test getting the feed by URL or name
    retrieved_feed = FeedRepo().get_feed_by_url_or_name(
        db=db, url=feed.url, name=feed.name
    )
    assert retrieved_feed is not None
    assert retrieved_feed.id == feed.id
    assert retrieved_feed.url == feed.url
    assert retrieved_feed.name == feed.name


def test_create_feed(client, db):
    # Test creating a new feed
    feed_data = FeedCreate(url="https://testfeed/3", name="Example Feed 3")
    created_feed = FeedRepo().create_feed(db=db, obj_in=feed_data)
    assert created_feed is not None
    assert created_feed.url == feed_data.url
    assert created_feed.name == feed_data.name


def test_update_failure_count(client, db):
    feed = Feed(url="https://testfeed/4", name="Example Feed 4")
    db.add(feed)
    db.commit()

    new_failed_attempts = 3
    updated_feed = FeedRepo().update_failure_count(
        db=db, id=feed.id, failed_attempts=new_failed_attempts
    )
    assert updated_feed is not None
    assert updated_feed.id == feed.id
    assert updated_feed.failed_attempts == new_failed_attempts
    assert updated_feed.refreshed_at is not None


def test_batch_insert_posts(client, db):
    feed = Feed(url="https://testfeed/5", name="Example Feed 5")
    db.add(feed)
    db.commit()

    posts_data = [
        PostCreate(
            title="Post 1",
            link="https://testfeed-5/post1",
            description="Post 1 content",
            uid="post1",
            published_at=datetime.utcnow(),
        ),
        PostCreate(
            title="Post 2",
            link="https://testfeed-5/post2",
            description="Post 2 content",
            uid="post2",
            published_at=datetime.utcnow(),
        ),
    ]
    FeedRepo().batch_insert_posts(db=db, feed_id=feed.id, posts=posts_data)

    inserted_posts = db.query(Post).filter(Post.feed_id == feed.id).all()
    assert len(inserted_posts) == len(posts_data)
    for inserted_post, post_data in zip(inserted_posts, posts_data):
        assert inserted_post.title == post_data.title
        assert inserted_post.link == post_data.link
        assert inserted_post.content == post_data.description
        assert inserted_post.published_at == post_data.published_at
