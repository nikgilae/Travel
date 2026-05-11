"""add_google_place_id

Revision ID: c56c8a58e7f8
Revises: dc03bca0975f
Create Date: 2026-04-24 15:39:53.048630

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c56c8a58e7f8'
down_revision: Union[str, Sequence[str], None] = 'dc03bca0975f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Оставляем только добавление колонки и индекса для google_place_id
    op.add_column('pois', sa.Column('google_place_id', sa.String(length=255), nullable=True))
    op.create_index(op.f('ix_pois_google_place_id'), 'pois', ['google_place_id'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    # Оставляем только удаление индекса и колонки
    op.drop_index(op.f('ix_pois_google_place_id'), table_name='pois')
    op.drop_column('pois', 'google_place_id')