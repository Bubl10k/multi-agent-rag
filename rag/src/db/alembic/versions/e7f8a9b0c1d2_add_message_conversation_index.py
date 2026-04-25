"""add message conversation index

Revision ID: e7f8a9b0c1d2
Revises: d63e9163349e
Create Date: 2026-04-26 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = 'e7f8a9b0c1d2'
down_revision: Union[str, Sequence[str], None] = 'd63e9163349e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index('idx_message_conversation_created_at', 'message', ['conversation_id', 'created_at'])


def downgrade() -> None:
    op.drop_index('idx_message_conversation_created_at', table_name='message')