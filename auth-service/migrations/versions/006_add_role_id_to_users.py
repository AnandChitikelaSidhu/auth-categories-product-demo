"""Add role_id to users table

Revision ID: 006
Revises: 005
Create Date: 2026-06-19

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=True),
    )

    op.execute(
        """
        UPDATE users u
        SET role_id = r.id
        FROM roles r
        WHERE r.name = u.role::text
        """
    )

    op.alter_column("users", "role_id", nullable=False)
    op.create_foreign_key("fk_users_role_id", "users", "roles", ["role_id"], ["id"])
    op.drop_column("users", "role")
    op.execute("DROP TYPE user_role")


def downgrade() -> None:
    user_role_enum = postgresql.ENUM(
        "customer",
        "admin",
        "super_admin",
        name="user_role",
        create_type=False,
    )
    user_role_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "users",
        sa.Column(
            "role",
            user_role_enum,
            server_default="customer",
            nullable=False,
        ),
    )

    op.execute(
        """
        UPDATE users u
        SET role = r.name::user_role
        FROM roles r
        WHERE u.role_id = r.id
        """
    )

    op.drop_constraint("fk_users_role_id", "users", type_="foreignkey")
    op.drop_column("users", "role_id")
