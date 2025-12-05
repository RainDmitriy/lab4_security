"""Create refresh_tokens table

Revision ID: e0a44546f3da
Revises: 688e57cd9e4c
Create Date: 2025-10-17 12:26:09.831060

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e0a44546f3da'
down_revision: Union[str, None] = '688e57cd9e4c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("token", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("user_agent", sa.String(500), nullable=True),
        sa.Column("expires_at", sa.DateTime, nullable=False),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.text("now()")),
    )

def downgrade():
    op.drop_table("refresh_tokens")
