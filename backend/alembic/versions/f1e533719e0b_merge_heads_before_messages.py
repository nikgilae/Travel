"""merge heads before messages

Revision ID: f1e533719e0b
Revises: 251c9801b3a4, 64c71498e706
Create Date: 2026-07-14 05:29:50.185619

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f1e533719e0b'
down_revision: Union[str, Sequence[str], None] = ('251c9801b3a4', '64c71498e706')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
