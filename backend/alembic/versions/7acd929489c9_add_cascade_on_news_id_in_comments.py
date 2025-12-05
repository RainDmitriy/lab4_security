"""Add CASCADE on news_id in comments

Revision ID: 7acd929489c9
Revises: 6f973778addf
Create Date: 2025-10-06 23:38:05.743942

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '7acd929489c9'
down_revision: Union[str, None] = '6f973778addf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Удаляем старое ограничение
    op.drop_constraint("fk_comments_news_id", "comments", type_="foreignkey")
    # Создаём новое с каскадом
    op.create_foreign_key("fk_comments_news_id", "comments", "news", ["news_id"], ["id"], ondelete="CASCADE")

def downgrade():
    op.drop_constraint("fk_comments_news_id", "comments", type_="foreignkey")
    op.create_foreign_key("fk_comments_news_id", "comments", "news", ["news_id"], ["id"])
