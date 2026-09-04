"""add nickname to nfc_tags

Revision ID: b1c3e2f4a5d6
Revises: a04ebd3f5bc6
Create Date: 2026-06-28 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'b1c3e2f4a5d6'
down_revision: Union[str, Sequence[str], None] = 'a04ebd3f5bc6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('nfc_tags', sa.Column('nickname', sa.String(50), nullable=True))


def downgrade() -> None:
    op.drop_column('nfc_tags', 'nickname')
