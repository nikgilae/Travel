"""add messages

Revision ID: 575548e519ac
Revises: f1e533719e0b
Create Date: 2026-07-14 05:29:54.812691

Ручная миграция: autogenerate дополнительно предлагал удалить служебные таблицы
PostGIS/Tiger (edges, place, tract, faces и т.д.) — они живут в БД из образа
postgis, но не описаны нашими моделями. Эти drop'ы вычищены; миграция создаёт
ТОЛЬКО таблицу messages.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '575548e519ac'
down_revision: Union[str, Sequence[str], None] = 'f1e533719e0b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'messages',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('trip_id', sa.UUID(), nullable=True),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('tool_name', sa.String(length=100), nullable=True),
        sa.Column('tool_calls', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['trip_id'], ['trips.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_messages_trip_created', 'messages', ['trip_id', 'created_at'], unique=False)
    op.create_index('idx_messages_user_created', 'messages', ['user_id', 'created_at'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('idx_messages_user_created', table_name='messages')
    op.drop_index('idx_messages_trip_created', table_name='messages')
    op.drop_table('messages')
