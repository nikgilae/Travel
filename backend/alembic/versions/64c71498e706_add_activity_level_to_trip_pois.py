"""add_activity_level_to_trip_pois

Revision ID: 64c71498e706
Revises: eacb4e35ee2e
Create Date: 2026-05-19 01:57:34.808716

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '64c71498e706'
down_revision: Union[str, Sequence[str], None] = 'eacb4e35ee2e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('trip_pois', sa.Column('activity_level', sa.Integer(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('trip_pois', 'activity_level')
