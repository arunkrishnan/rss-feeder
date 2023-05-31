from unittest.mock import patch
from datetime import datetime
from app.repository.user import UserRepo
from app.schemas.user import SignupRequest
from app.models.user import User, Subscription
from app.models.user_post import UserPost
from app.models.feed import Post


def test_get_user(client, db):
    repo = UserRepo()
    user = User(id=1, email="user1@test-get-user.com", password="password")
    db.add(user)
    db.commit()

    result = repo.get(db, id=1)
    assert result == user


def test_get_user_by_email(client, db):
    repo = UserRepo()
    user_email = "user1@test-get-user-email.com"
    user = User(id=1, email=user_email, password="password")
    db.add(user)
    db.commit()

    result = repo.get_by_email(db, email=user_email)
    assert result == user


def test_create_user(client, db):
    repo = UserRepo()
    signup_request = SignupRequest(
        email="user1@test-create-user.com", password="password123"
    )

    result = repo.create(db, obj_in=signup_request)
    assert result.email == signup_request.email
    assert result.password != signup_request.password


def test_get_feed_subscription(client, db):
    repo = UserRepo()
    user_id = 1
    feed_id = 1
    subscription = Subscription(user_id=user_id, feed_id=feed_id)
    db.add(subscription)
    db.commit()

    result = repo.get_feed_subscription(db, user_id=user_id, feed_id=feed_id)
    assert result == subscription


def test_create_feed_subscription(client, db):
    repo = UserRepo()
    user_id = 1
    feed_id = 1

    result = repo.create_feed_subscription(db, user_id=user_id, feed_id=feed_id)
    assert result.user_id == user_id
    assert result.feed_id == feed_id
    assert result.is_active is True


def test_activate_feed_subscription(client, db):
    repo = UserRepo()
    subscription = Subscription(id=1, is_active=False, feed_id=1, user_id=1)
    db.add(subscription)
    db.commit()

    result = repo.activate_feed_subscription(db, id=1)
    assert result.is_active is True


def test_deactivate_feed_subscription(client, db):
    repo = UserRepo()
    subscription = Subscription(id=1, is_active=True, feed_id=1, user_id=1)
    db.add(subscription)
    db.commit()

    result = repo.deactivate_feed_subscription(db, id=1)
    assert result.is_active is False


def test_get_posts(client, db):
    repo = UserRepo()
    user_id = 1
    user_post = UserPost(
        user_id=user_id,
        post_id=1,
        is_read=False,
        created_at=datetime.now(),
        feed_id=1,
        title="Post 1",
        content="Post 1 content",
        link="http://test-post/1",
        published_at=datetime.now(),
    )
    db.add(user_post)
    db.commit()
    result = repo.get_posts(db, user_id=user_id, feed_id=None, is_read=None)
    assert len(result) == 1
    assert result[0] == user_post


def test_mark_post_as_read(client, db):
    repo = UserRepo()
    user_id = 1
    post_id = 1

    result = repo.mark_post_as_read(db, user_id=user_id, post_id=post_id)
    assert result.user_id == user_id
    assert result.post_id == post_id
    assert result.is_read is True


def test_mark_post_as_unread(client, db):
    repo = UserRepo()
    user_id = 1
    post_id = 1

    result = repo.mark_post_as_unread(db, user_id=user_id, post_id=post_id)
    assert result is None

    repo.mark_post_as_read(db, user_id=user_id, post_id=post_id)

    result = repo.mark_post_as_unread(db, user_id=user_id, post_id=post_id)
    assert result.is_read is False
