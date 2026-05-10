"""initial schema

Revision ID: 20260510_0001
Revises:
Create Date: 2026-05-10
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


revision: str = "20260510_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "hero",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("power", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_hero_age", "hero", ["age"], unique=False)
    op.create_index("ix_hero_name", "hero", ["name"], unique=False)
    op.create_index("ix_hero_power", "hero", ["power"], unique=False)

    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("hashed_password", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("is_admin", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_user_hashed_password", "user", ["hashed_password"], unique=False)
    op.create_index("ix_user_is_admin", "user", ["is_admin"], unique=False)
    op.create_index("ix_user_username", "user", ["username"], unique=True)

    op.create_table(
        "mission",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("difficulty", sa.Integer(), nullable=False),
        sa.Column("completed", sa.Boolean(), nullable=False),
        sa.Column("hero_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["hero_id"], ["hero.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_mission_completed", "mission", ["completed"], unique=False)
    op.create_index("ix_mission_difficulty", "mission", ["difficulty"], unique=False)
    op.create_index("ix_mission_name", "mission", ["name"], unique=False)

    op.create_table(
        "role",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_role_name", "role", ["name"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_role_name", table_name="role")
    op.drop_table("role")

    op.drop_index("ix_mission_name", table_name="mission")
    op.drop_index("ix_mission_difficulty", table_name="mission")
    op.drop_index("ix_mission_completed", table_name="mission")
    op.drop_table("mission")

    op.drop_index("ix_user_username", table_name="user")
    op.drop_index("ix_user_is_admin", table_name="user")
    op.drop_index("ix_user_hashed_password", table_name="user")
    op.drop_table("user")

    op.drop_index("ix_hero_power", table_name="hero")
    op.drop_index("ix_hero_name", table_name="hero")
    op.drop_index("ix_hero_age", table_name="hero")
    op.drop_table("hero")
