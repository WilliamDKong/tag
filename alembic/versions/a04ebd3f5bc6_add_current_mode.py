"""add current_mode

Revision ID: a04ebd3f5bc6
Revises: c8aa6312013a
Create Date: 2026-06-27 18:00:52.941028

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a04ebd3f5bc6'
down_revision: Union[str, Sequence[str], None] = 'c8aa6312013a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    modeenum = sa.Enum('DIRECT', 'DISPLAY', name='modeenum')
    modeenum.create(op.get_bind())
    op.add_column('nfc_tags', sa.Column('current_mode', modeenum, server_default='DIRECT', nullable=False))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('nfc_tags', 'current_mode')
    sa.Enum(name='modeenum').drop(op.get_bind())
