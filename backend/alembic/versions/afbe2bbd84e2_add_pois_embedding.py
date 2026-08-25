"""add_pois_embedding

Revision ID: afbe2bbd84e2
Revises: 575548e519ac
Create Date: 2026-08-25 10:50:38.382541

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = 'afbe2bbd84e2'
down_revision: Union[str, Sequence[str], None] = '575548e519ac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.add_column('pois', sa.Column('embedding', Vector(3072), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('pois', 'embedding')
