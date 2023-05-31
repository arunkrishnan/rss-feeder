import json
from unittest.mock import patch

from app.core.celery_app import celery_app
from app.repository.feed import repo as feed_repo
from app.schemas.feed import Feed


def test_create_feed(client):
    test_feed_url = "https://test-create-feed-1/"
    feed_data = {
        "url": test_feed_url,
        "name": "test-create-feed-1",
    }
    response = client.post(
        "/feeds/",
        data=json.dumps(feed_data),
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["url"] == test_feed_url

    # Try creating a feed with the same URL, should return a 400 error
    response = client.post(
        "/feeds/",
        data=json.dumps(feed_data),
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 400
    response_data = response.json()
    assert response_data["detail"] == "Feed with this url already exists"

    # Try creating a feed with the same name, should return a 400 error
    feed_data["url"] = "https://test-create-feed-2/"
    response = client.post(
        "/feeds/",
        data=json.dumps(feed_data),
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 400
    response_data = response.json()
    assert response_data["detail"] == "Feed with this name already exists"


def test_refresh_feed(client):
    feed_id = 1
    with patch.object(feed_repo, "get") as mock_get_feed, patch.object(
        celery_app, "send_task"
    ) as mock_send_task:
        mock_get_feed.return_value = Feed(
            id=feed_id, name="test-create-feed-1", url="https://test-create-feed-1"
        )
        response = client.post(f"/feeds/refresh/{feed_id}")
        assert response.status_code == 200
        assert response.json() == {"message": "Feed refreshed successfully"}
        mock_send_task.assert_called_once_with(
            "app.scheduler.tasks.refresh_feed", args=(feed_id, True)
        )
