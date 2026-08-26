"""add ai_description to pois

Revision ID: c752eabffe3a
Revises: afbe2bbd84e2
Create Date: 2026-08-26 13:51:40.879858

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c752eabffe3a'
down_revision: Union[str, Sequence[str], None] = 'afbe2bbd84e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('pois', sa.Column('ai_description', sa.Text(), nullable=True))
    op.add_column(
        'pois', sa.Column('ai_description_source', sa.String(length=50), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('pois', 'ai_description_source')
    op.drop_column('pois', 'ai_description')
