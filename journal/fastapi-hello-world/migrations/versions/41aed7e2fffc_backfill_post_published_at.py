"""backfill post published at

Revision ID: 41aed7e2fffc
Revises: 060fbf88ad71
Create Date: 2026-06-22 01:27:47.750085

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '41aed7e2fffc'
down_revision: Union[str, Sequence[str], None] = '060fbf88ad71'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                'published_at',
                sa.DateTime(timezone=True),
                server_default=sa.text('CURRENT_TIMESTAMP'),
                nullable=True,
            )
        )

    op.execute(
        """
        UPDATE posts
        SET published_at = created_at
        WHERE published_at IS NULL
        """
    )

    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.alter_column(
            'published_at',
            existing_type=sa.DateTime(timezone=True),
            nullable=False,
            existing_server_default=sa.text('CURRENT_TIMESTAMP'),
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.drop_column('published_at')
