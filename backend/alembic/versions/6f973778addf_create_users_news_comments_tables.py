"""Create users, news, comments tables

Revision ID: 6f973778addf
Revises: 
Create Date: 2025-10-06 13:38:00.193730

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision: str = '6f973778addf'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("login", sa.String(100), unique=True, nullable=False, index=True),
        sa.Column("registered_at", sa.DateTime, server_default=sa.text("now()")),
        sa.Column("is_author_verified", sa.Boolean, default=False),
        sa.Column("avatar_url", sa.String(255), nullable=True),
    )

    op.create_table(
        "news",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("content", JSONB, nullable=False),
        sa.Column("published_at", sa.DateTime, server_default=sa.text("now()")),
        sa.Column("author_id", sa.Integer, nullable=False),
        sa.Column("cover_url", sa.String(255), nullable=True),
    )
    op.create_foreign_key("fk_news_author_id", "news", "users", ["author_id"], ["id"])

    op.create_table(
        "comments",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("text", sa.String(500), nullable=False),
        sa.Column("news_id", sa.Integer, nullable=False),
        sa.Column("author_id", sa.Integer, nullable=False),
        sa.Column("published_at", sa.DateTime, server_default=sa.text("now()")),
    )
    op.create_foreign_key("fk_comments_news_id", "comments", "news", ["news_id"], ["id"])
    op.create_foreign_key("fk_comments_author_id", "comments", "users", ["author_id"], ["id"])

def downgrade():
    op.drop_constraint("fk_comments_author_id", "comments", type_="foreignkey")
    op.drop_constraint("fk_comments_news_id", "comments", type_="foreignkey")
    op.drop_table("comments")
    op.drop_constraint("fk_news_author_id", "news", type_="foreignkey")
    op.drop_table("news")
    op.drop_table("users")
