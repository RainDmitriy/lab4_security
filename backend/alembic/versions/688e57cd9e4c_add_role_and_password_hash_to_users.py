"""Add role and password_hash to users

Revision ID: 688e57cd9e4c
Revises: 7acd929489c9
Create Date: 2025-10-17 07:42:23.693242

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '688e57cd9e4c'
down_revision: Union[str, None] = '7acd929489c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Добавляем колонки
    op.add_column('users', sa.Column('role', sa.String(length=20), nullable=True, server_default='user'))
    op.add_column('users', sa.Column('password_hash', sa.String(length=255), nullable=True))

    op.alter_column('users', 'role', nullable=False, server_default='user')
    op.alter_column('users', 'password_hash', nullable=False)

def downgrade():
    # Удаляем колонки
    op.drop_column('users', 'password_hash')
    op.drop_column('users', 'role')
