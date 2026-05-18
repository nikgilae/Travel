"""merge_heads

Revision ID: 98bce5a355d5
Revises: 3f8a9cb929e7, 52d8b3e8ff63
Create Date: 2026-05-18 09:37:05.458612

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '98bce5a355d5'
down_revision: Union[str, Sequence[str], None] = ('3f8a9cb929e7', '52d8b3e8ff63')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
