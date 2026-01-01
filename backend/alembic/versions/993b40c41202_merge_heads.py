"""merge heads

Revision ID: 993b40c41202
Revises: 8dfdd837bb90, remove_drlz_simplify_tabletki
Create Date: 2025-08-24 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '993b40c41202'
down_revision = ('8dfdd837bb90', 'remove_drlz_simplify_tabletki')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass