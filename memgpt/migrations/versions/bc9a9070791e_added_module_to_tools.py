"""added module to tools

Revision ID: bc9a9070791e
Revises: 8ab5757fa7a1
Create Date: 2024-08-07 02:18:39.649742

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "bc9a9070791e"
down_revision: Union[str, None] = "8ab5757fa7a1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("preset", sa.Column("system_name", sa.String(), nullable=False))
    op.add_column("preset", sa.Column("_human_memory_template_id", sa.UUID(), nullable=False))
    op.add_column("preset", sa.Column("_persona_memory_template_id", sa.UUID(), nullable=False))
    op.add_column("preset", sa.Column("_system_memory_template_id", sa.UUID(), nullable=False))
    op.create_foreign_key(None, "preset", "memory_template", ["_system_memory_template_id"], ["_id"])
    op.create_foreign_key(None, "preset", "memory_template", ["_persona_memory_template_id"], ["_id"])
    op.create_foreign_key(None, "preset", "memory_template", ["_human_memory_template_id"], ["_id"])
    op.drop_column("preset", "persona")
    op.drop_column("preset", "human")
    op.drop_column("preset", "system")
    op.add_column("tool", sa.Column("module", sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("tool", "module")
    op.add_column("preset", sa.Column("system", sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column("preset", sa.Column("human", sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column("preset", sa.Column("persona", sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_constraint(None, "preset", type_="foreignkey")
    op.drop_constraint(None, "preset", type_="foreignkey")
    op.drop_constraint(None, "preset", type_="foreignkey")
    op.drop_column("preset", "_system_memory_template_id")
    op.drop_column("preset", "_persona_memory_template_id")
    op.drop_column("preset", "_human_memory_template_id")
    op.drop_column("preset", "system_name")
    # ### end Alembic commands ###
