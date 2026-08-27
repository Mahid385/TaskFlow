"""add timestamps to users and tasks

Revision ID: 427afb5ed14d
Revises:
Create Date: 2026-08-22 15:38:38.760493
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "427afb5ed14d"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add timestamp columns to users and tasks.

    Existing rows are populated first, then the columns
    are changed to NOT NULL.
    """

    # =========================================================
    # USERS
    # =========================================================

    # Step 1:
    # Add created_at as nullable because existing rows
    # do not have a value yet.
    op.add_column(
        "users",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    # Step 2:
    # Populate created_at for existing users.
    op.execute(
        sa.text(
            """
            UPDATE users
            SET created_at = CURRENT_TIMESTAMP
            WHERE created_at IS NULL
            """
        )
    )

    # Step 3:
    # Now that every existing row has a value,
    # make the column NOT NULL.
    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column(
            "created_at",
            existing_type=sa.DateTime(timezone=True),
            nullable=False,
        )

    # =========================================================
    # TASKS
    # =========================================================

    # Step 1:
    # Add created_at temporarily as nullable.
    op.add_column(
        "tasks",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    # Step 2:
    # Add updated_at temporarily as nullable.
    op.add_column(
        "tasks",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    # Step 3:
    # Populate created_at for existing tasks.
    op.execute(
        sa.text(
            """
            UPDATE tasks
            SET created_at = CURRENT_TIMESTAMP
            WHERE created_at IS NULL
            """
        )
    )

    # Step 4:
    # Populate updated_at for existing tasks.
    op.execute(
        sa.text(
            """
            UPDATE tasks
            SET updated_at = CURRENT_TIMESTAMP
            WHERE updated_at IS NULL
            """
        )
    )

    # Step 5:
    # Make both timestamp columns NOT NULL.
    with op.batch_alter_table("tasks") as batch_op:
        batch_op.alter_column(
            "created_at",
            existing_type=sa.DateTime(timezone=True),
            nullable=False,
        )

        batch_op.alter_column(
            "updated_at",
            existing_type=sa.DateTime(timezone=True),
            nullable=False,
        )


def downgrade() -> None:
    """
    Remove timestamp columns from users and tasks.
    """

    # Remove users.created_at
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("created_at")

    # Remove task timestamps
    with op.batch_alter_table("tasks") as batch_op:
        batch_op.drop_column("updated_at")
        batch_op.drop_column("created_at")