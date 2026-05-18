"""add_description_to_countries

Revision ID: eacb4e35ee2e
Revises: 98bce5a355d5
Create Date: 2026-05-18 09:37:09.521141

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eacb4e35ee2e'
down_revision: Union[str, Sequence[str], None] = '98bce5a355d5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('countries', sa.Column('description', sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('countries', 'description')
