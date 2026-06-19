"""Create permissions table

Revision ID: 004
Revises: 003
Create Date: 2026-06-19

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "permissions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )

    op.execute(
        """
        INSERT INTO permissions (code, description) VALUES
            ('show_new_product', 'Show the new product button on manage products'),
            ('create_product', 'Create new products'),
            ('manage_users', 'List and view users'),
            ('manage_roles', 'Assign roles and permissions')
        """
    )


def downgrade() -> None:
    op.drop_table("permissions")
