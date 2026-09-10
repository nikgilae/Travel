"""add source to pois

Признак происхождения места. NULL — как было (Google Places или сид).
'ai_fallback' — место названо AI-моделью, потому что Places API был недоступен
(выключенный биллинг с 09.09.2026, см. AI_POI_FALLBACK_ENABLED). Индекс нужен
ровно для одной операции: вычистить такие места, когда Google оживёт, и дать
городу собраться заново.

Revision ID: e7b2f4c81d09
Revises: d4a1c7e90b52
Create Date: 2026-09-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7b2f4c81d09'
down_revision: Union[str, Sequence[str], None] = 'd4a1c7e90b52'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('pois', sa.Column('source', sa.String(length=20), nullable=True))
    op.create_index('ix_pois_source', 'pois', ['source'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_pois_source', table_name='pois')
    op.drop_column('pois', 'source')
