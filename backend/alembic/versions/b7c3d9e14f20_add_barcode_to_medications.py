"""add barcode to medications

Revision ID: b7c3d9e14f20
Revises: 2902d29064c4
Create Date: 2026-07-23 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b7c3d9e14f20'
down_revision = '2902d29064c4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add scanned package barcode column to medications and index it for lookups
    op.add_column('medications', sa.Column('barcode', sa.String(), nullable=True))
    op.create_index('ix_medications_barcode', 'medications', ['barcode'])


def downgrade() -> None:
    op.drop_index('ix_medications_barcode', table_name='medications')
    op.drop_column('medications', 'barcode')
