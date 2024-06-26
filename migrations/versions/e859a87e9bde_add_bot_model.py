"""add bot model

Revision ID: e859a87e9bde
Revises:
Create Date: 2024-05-21 08:17:15.032566

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e859a87e9bde"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "bots",
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("avatar", sa.String(length=36), nullable=False),
        sa.Column("welcome_message", sa.String(length=255), nullable=True),
        sa.Column("data_source", sa.String(length=100), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_bots_name"), "bots", ["name"], unique=True)
    op.create_table(
        "bot_contexts",
        sa.Column(
            "role",
            sa.Enum(
                "system",
                "user",
                "assistant",
                name="botcontextrole",
                native_enum=False,
                length=36,
            ),
            nullable=False,
        ),
        sa.Column("content", sa.String(length=1000), nullable=False),
        sa.Column("bot_id", sa.UUID(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["bot_id"],
            ["bots.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_bot_contexts_role"), "bot_contexts", ["role"], unique=False
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_bot_contexts_role"), table_name="bot_contexts")
    op.drop_table("bot_contexts")
    op.drop_index(op.f("ix_bots_name"), table_name="bots")
    op.drop_table("bots")
    # ### end Alembic commands ###
