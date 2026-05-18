"""Merge conflict

Revision ID: 251c9801b3a4
Revises: c2ea5feeb147, eacb4e35ee2e
Create Date: 2026-05-18 11:02:04.359074

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '251c9801b3a4'
down_revision: Union[str, Sequence[str], None] = ('c2ea5feeb147', 'eacb4e35ee2e')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
