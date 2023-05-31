"""create user post view

Revision ID: f1d5dbbe6f56
Revises: 9bd17093c9ae
Create Date: 2023-05-31 16:07:19.389244

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f1d5dbbe6f56'
down_revision = '9bd17093c9ae'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE VIEW user_post AS 
        SELECT
            p.id as post_id,
            p.feed_id,
            p.title,
            p.content,
            p.author,
            p.created_at,
            p.published_at,
            p.link,
            us.user_id,
            CASE WHEN prs.is_read THEN true ELSE false END AS is_read
        FROM post p
        JOIN user_subscription us ON us.feed_id = p.feed_id and us.is_active = true 
        LEFT JOIN post_read_status prs ON prs.post_id = p.id and prs.user_id = us.user_id
        ORDER BY published_at;
        """
    )


def downgrade() -> None:
    op.execute("drop view user_post;")
