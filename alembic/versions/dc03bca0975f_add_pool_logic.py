"""add_pool_logic

Revision ID: dc03bca0975f
Revises: a28b7870f1b4
Create Date: 2026-04-24 14:35:37.385115

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'dc03bca0975f'
down_revision: Union[str, Sequence[str], None] = 'a28b7870f1b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Создаем ENUM тип в базе данных
    op.execute("CREATE TYPE poi_status_enum AS ENUM ('main', 'additional')")
    
    # 2. Добавляем колонку статуса места (по умолчанию 'main')
    op.add_column('trip_pois', sa.Column('poi_status', postgresql.ENUM('main', 'additional', name='poi_status_enum'), nullable=False, server_default='main'))
    
    # 3. Добавляем колонку выбора (по умолчанию false)
    op.add_column('trip_pois', sa.Column('is_selected', sa.Boolean(), nullable=False, server_default='false'))
    
    # 4. Изменяем sequence_order, делая его необязательным
    op.alter_column('trip_pois', 'sequence_order',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    # Возвращаем sequence_order к обязательному виду
    op.alter_column('trip_pois', 'sequence_order',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               nullable=False)
               
    # Удаляем новые колонки
    op.drop_column('trip_pois', 'is_selected')
    op.drop_column('trip_pois', 'poi_status')
    
    # Удаляем тип ENUM
    op.execute("DROP TYPE poi_status_enum")