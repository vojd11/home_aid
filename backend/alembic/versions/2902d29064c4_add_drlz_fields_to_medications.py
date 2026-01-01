"""add drlz fields to medications

Revision ID: 2902d29064c4
Revises: 993b40c41202
Create Date: 2025-08-24 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '2902d29064c4'
down_revision = '993b40c41202'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add DRLZ-related columns to medications table
    op.add_column('medications', sa.Column('description', sa.Text(), nullable=True))
    op.add_column('medications', sa.Column('drlz_link', sa.Text(), nullable=True))
    op.add_column('medications', sa.Column('drlz_instruction_link', sa.Text(), nullable=True))


def downgrade() -> None:
    # Remove DRLZ-related columns
    op.drop_column('medications', 'drlz_instruction_link')
    op.drop_column('medications', 'drlz_link')
    op.drop_column('medications', 'description')