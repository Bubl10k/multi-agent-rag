"""add refresh tokens

Revision ID: a1b2c3d4e5f6
Revises: d63e9163349e
Create Date: 2026-04-25 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'd63e9163349e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'refresh_token',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('jti', sa.String(), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_revoked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_refresh_token_jti', 'refresh_token', ['jti'], unique=True)
    op.create_index('ix_refresh_token_user_id', 'refresh_token', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_refresh_token_user_id', table_name='refresh_token')
    op.drop_index('ix_refresh_token_jti', table_name='refresh_token')
    op.drop_table('refresh_token')