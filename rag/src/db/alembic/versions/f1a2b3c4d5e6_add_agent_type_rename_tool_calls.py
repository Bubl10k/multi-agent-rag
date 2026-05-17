"""add agent_type, rename tool_calls to agent_config

Revision ID: f1a2b3c4d5e6
Revises: e7f8a9b0c1d2
Create Date: 2026-05-10 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "f1a2b3c4d5e6"
down_revision: Union[str, Sequence[str], None] = "5b429f57fab6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("agent", "tool_calls", new_column_name="agent_config")
    op.add_column(
        "agent",
        sa.Column("agent_type", sa.String(length=50), nullable=False, server_default="general"),
    )


def downgrade() -> None:
    op.drop_column("agent", "agent_type")
    op.alter_column("agent", "agent_config", new_column_name="tool_calls")
