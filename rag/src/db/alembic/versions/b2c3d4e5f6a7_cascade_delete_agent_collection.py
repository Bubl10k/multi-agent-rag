"""cascade delete on agent_collection.collection_id

Revision ID: b2c3d4e5f6a7
Revises: 1cc2c7a2f292
Create Date: 2026-06-10 20:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, Sequence[str], None] = "1cc2c7a2f292"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("agent_collection_collection_id_fkey", "agent_collection", type_="foreignkey")
    op.create_foreign_key(
        "agent_collection_collection_id_fkey",
        "agent_collection",
        "collection",
        ["collection_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint("agent_collection_collection_id_fkey", "agent_collection", type_="foreignkey")
    op.create_foreign_key(
        "agent_collection_collection_id_fkey",
        "agent_collection",
        "collection",
        ["collection_id"],
        ["id"],
    )