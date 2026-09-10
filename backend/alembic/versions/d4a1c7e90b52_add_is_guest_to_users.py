"""add is_guest to users

Гостевой аккаунт: онбординг заводит его сам, чтобы человек дошёл до маршрута
без формы регистрации. Флаг снимается, когда человек вписывает свою почту
(AuthService.claim). server_default='false' — все существующие пользователи
настоящие, регистрировались руками.

Revision ID: d4a1c7e90b52
Revises: c752eabffe3a
Create Date: 2026-09-09

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4a1c7e90b52'
down_revision: Union[str, Sequence[str], None] = 'c752eabffe3a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'users',
        sa.Column(
            'is_guest',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('false'),
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'is_guest')
