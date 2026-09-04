"""add profile_name and bio to nfc_tags

Revision ID: c3d4e5f6a7b8
Revises: b1c3e2f4a5d6
Create Date: 2026-09-04
"""
from alembic import op
import sqlalchemy as sa

revision = 'c3d4e5f6a7b8'
down_revision = 'b1c3e2f4a5d6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('nfc_tags', sa.Column('profile_name', sa.String(80), nullable=True))
    op.add_column('nfc_tags', sa.Column('bio', sa.String(200), nullable=True))


def downgrade() -> None:
    op.drop_column('nfc_tags', 'bio')
    op.drop_column('nfc_tags', 'profile_name')
