# RSS Feeder

## Description

Service that provides an API to serve users with RSS feeds.

To run the application use [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/install/) 

   ```bash
   docker-compose up -d
   ```

This will spawn four containers
1. Web service to handle APIs
2. Celery worker to handle asyncronous jobs
3. Postgres
4. Rabitmq


The server will be accessible at the following address:

*Base URL: http://127.0.0.1:8000*

### Interactive API Documentation:

Interactive API documentation will be available at the following address:

*URL: http://127.0.0.1:8000/docs*

### Workflow:

To effectively use the application, follow the steps outlined below:

1. Adding Feeds:
    To track specific feeds, you need to add them to the application using the following API endpoint:

    ```API: POST /api/v1/feeds/```

2. User Account Creation:
    Create a user account by making a request to the following API endpoint:

    ```API: POST /api/v1/users/signup```

3. Fetching Latest Posts:
    
    After successfully adding the feeds, a background job will automatically start fetching the latest posts for each feed.

    This process occurs every 5 minutes.

    To manually refresh a feed, use the following API endpoint:

    ```API: POST /api/v1/feeds/refresh/{feed_id}```
        
        Note: Replace {feed_id} with the actual ID obtained from the response of the API endpoint: GET /api/v1/feeds/

4. Following and Unfollowing Feeds:

    To follow or unfollow a feed, use the respective API endpoints provided:

    ```API (Follow): POST /api/v1/users/follow/{feed_id}```

    ```API (Unfollow): POST /api/v1/users/unfollow/{feed_id}```

        The feed_id parameter can be obtained from the response of the API endpoint: GET /api/v1/feeds/

        Please note that these APIs can only be accessed by logged-in users.


5. Accessing Posts:
    
    To access the fetched posts, use the following API endpoint:

    ```API: GET /api/v1/feeds/```

        Note: Ensure that you have followed the feeds before accessing the posts and accessed by logged-in user.


6. Marking Posts as Read/Unread:
    To mark a post as read or unread, use the following API endpoints:

    ```API (Mark as Read): POST /api/v1/users/posts/{post_id}/read```

    ```API (Mark as Unread): POST /api/v1/users/posts/{post_id}/unread```

7. For testing the application use pytest