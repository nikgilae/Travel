"""Merge conflicting heads

Revision ID: c2ea5feeb147
Revises: 3f8a9cb929e7, 52d8b3e8ff63
Create Date: 2026-05-13 12:42:08.485943

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c2ea5feeb147'
down_revision: Union[str, Sequence[str], None] = ('3f8a9cb929e7', '52d8b3e8ff63')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
