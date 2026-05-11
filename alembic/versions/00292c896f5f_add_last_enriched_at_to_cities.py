"""add_last_enriched_at_to_cities

Revision ID: 00292c896f5f
Revises: 74b6e9839d4e
Create Date: 2026-05-10 18:04:04.138329

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '00292c896f5f'
down_revision: Union[str, Sequence[str], None] = '74b6e9839d4e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('cities', sa.Column('last_enriched_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('cities', 'last_enriched_at')
