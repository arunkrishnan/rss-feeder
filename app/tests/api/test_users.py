from datetime import datetime
from fastapi import FastAPI
from unittest.mock import patch

from app.api.v1.api import api_router
from app.core.config import settings
from app.repository.user import repo as user_repo
from app.schemas.user import User, Subscription, UserPost

app = FastAPI(title="Test app")

app.include_router(api_router, prefix=settings.API_V1_STR)


def test_signup_success(client):
    user_email = "user-1@test-signup.aa"
    signup_data = {
        "email": user_email,
        "password": "password123",
    }

    response = client.post(f"/users/signup", json=signup_data)
    assert response.status_code == 201, response.text
    respons_data = response.json()
    assert respons_data["email"] == user_email


def test_signup_existing_email(client):
    user_email = "user-2@test-signup.aa"
    signup_data = {
        "email": user_email,
        "password": "password123",
    }

    response = client.post("/users/signup", json=signup_data)
    assert response.status_code == 201

    response = client.post("/users/signup", json=signup_data)
    assert response.status_code == 400

    assert response.json() == {"detail": "Email already registered"}


def test_follow_feed(client, db, user_token):
    feed_id = 1
    with patch.object(user_repo, "get") as mock_get_user, patch.object(
        user_repo, "get_feed_subscription"
    ) as mock_get_subscription, patch.object(
        user_repo, "activate_feed_subscription"
    ) as mock_activate_subscription, patch.object(
        user_repo, "create_feed_subscription"
    ) as mock_create_subscription:
        mock_get_subscription.return_value = None
        mock_get_user.return_value = User(id=1, email="user-1@test-follow-feed.a")

        client.headers = {"Authorization": f"Bearer {user_token}"}
        response = client.post(f"/users/follow/{feed_id}")
        assert response.status_code == 200
        assert response.json() == {"message": "Followed feed successfully"}
        mock_get_subscription.assert_called_once_with(db=db, user_id=1, feed_id=feed_id)
        mock_activate_subscription.assert_not_called()
        mock_create_subscription.assert_called_once_with(
            db=db, user_id=1, feed_id=feed_id
        )


def test_unfollow_feed(client, db, user_token):
    feed_id = 1
    with patch.object(user_repo, "get") as mock_get_user, patch.object(
        user_repo, "get_feed_subscription"
    ) as mock_get_subscription, patch.object(
        user_repo, "deactivate_feed_subscription"
    ) as mock_deactivate_subscription:
        mock_get_user.return_value = User(id=1, email="user-1@test-unfollow-feed.a")
        mock_get_subscription.return_value = Subscription(
            id=1, user_id=1, feed_id=feed_id, is_active=True
        )

        client.headers = {"Authorization": f"Bearer {user_token}"}
        response = client.post(f"/users/unfollow/{feed_id}")
        assert response.status_code == 200
        assert response.json() == {"message": "Unfollowed feed successfully"}
        mock_get_subscription.assert_called_once_with(db=db, user_id=1, feed_id=feed_id)
        mock_deactivate_subscription.assert_called_once_with(db=db, id=1)


def test_get_posts(client, db, user_token):
    with patch.object(user_repo, "get") as mock_get_user, patch.object(
        user_repo, "get_posts"
    ) as mock_get_posts:
        mock_get_user.return_value = User(id=1, email="user-1@test-get-posts.a")
        mock_get_posts.return_value = [
            UserPost(
                post_id=1,
                title="Post 1",
                content="Content 1",
                user_id=1,
                is_read=False,
                created_at=datetime.now(),
                feed_id=1,
                published_at=datetime.now(),
                link="https://test.com",
            ),
            UserPost(
                post_id=2,
                title="Post 2",
                content="Content 2",
                user_id=2,
                is_read=True,
                created_at=datetime.now(),
                feed_id=1,
                published_at=datetime.now(),
                link="https://test.com",
            ),
        ]
        client.headers = {"Authorization": f"Bearer {user_token}"}
        response = client.get("/users/posts")
        assert response.status_code == 200
        assert len(response.json()) == 2
        assert response.json()[0]["post_id"] == 1
        assert response.json()[0]["title"] == "Post 1"
        assert response.json()[0]["content"] == "Content 1"
        assert response.json()[0]["user_id"] == 1
        assert not response.json()[0]["is_read"]
        mock_get_posts.assert_called_once_with(
            db=db, user_id=1, feed_id=None, is_read=None, offset=0, limit=100
        )


def test_mark_post_as_read(client, user_token) -> None:
    post_id = 100
    with patch.object(user_repo, "get") as mock_get_user, patch.object(
        user_repo, "mark_post_as_read"
    ) as mock_mark_post_as_read:
        mock_get_user.return_value = User(id=1, email="user1@test-read-status")
        mock_mark_post_as_read.return_value = UserPost(
            post_id=post_id,
            title="Post 100",
            content="Content 100",
            user_id=1,
            is_read=True,
            created_at=datetime.now(),
            feed_id=1,
            published_at=datetime.now(),
            link="https://www.google.com",
        )
        client.headers = {"Authorization": f"Bearer {user_token}"}
        response = client.post(f"/users/posts/{post_id}/read")
        assert response.status_code == 200
        assert response.json() == {"message": "Post marked as read"}


def test_mark_post_as_unread(client, user_token) -> None:
    post_id = 100
    with patch.object(user_repo, "get") as mock_get_user, patch.object(
        user_repo, "mark_post_as_unread"
    ) as mark_post_as_unread:
        mock_get_user.return_value = User(id=1, email="user1@test-read-status")
        mark_post_as_unread.return_value = UserPost(
            post_id=post_id,
            title="Post 100",
            content="Content 100",
            user_id=1,
            is_read=False,
            created_at=datetime.now(),
            feed_id=1,
            published_at=datetime.now(),
            link="https://www.google.com",
        )
        client.headers = {"Authorization": f"Bearer {user_token}"}
        response = client.post(f"/users/posts/{post_id}/unread")
        assert response.status_code == 200
        assert response.json() == {"message": "Post marked as unread"}
