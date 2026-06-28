"""add password hash for auth

Revision ID: ffb29e3dd7c8
Revises: 41aed7e2fffc
Create Date: 2026-06-24 23:57:55.121422

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ffb29e3dd7c8'
down_revision: Union[str, Sequence[str], None] = '41aed7e2fffc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('password_hash', sa.String(length=255), nullable=True))

    op.execute(
        """
        UPDATE users
        SET password_hash = '$2b$12$dbUHJxSTdW7U9ODAk2KXr.ffGRiDBBy4YIVR6cYgmIKLBtIktqp22'
        WHERE password_hash IS NULL
        """
    )

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column(
            'password_hash',
            existing_type=sa.String(length=255),
            nullable=False,
        )
        batch_op.drop_column('password')


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('password', sa.VARCHAR(length=255), nullable=True))

    op.execute(
        """
        UPDATE users
        SET password = 'change-me-password'
        WHERE password IS NULL
        """
    )

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column(
            'password',
            existing_type=sa.VARCHAR(length=255),
            nullable=False,
        )
        batch_op.drop_column('password_hash')
