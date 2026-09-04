"""add indexes on nfc_tags.user_id and tag_links(tag_id, sort_order)

Revision ID: d1e2f3a4b5c6
Revises: c3d4e5f6a7b8
Create Date: 2026-09-04
"""
from alembic import op

revision = 'd1e2f3a4b5c6'
down_revision = 'c3d4e5f6a7b8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index('ix_nfc_tags_user_id', 'nfc_tags', ['user_id'])
    op.create_index('ix_tag_links_tag_id_sort', 'tag_links', ['tag_id', 'sort_order'])


def downgrade() -> None:
    op.drop_index('ix_tag_links_tag_id_sort', table_name='tag_links')
    op.drop_index('ix_nfc_tags_user_id', table_name='nfc_tags')
