"""add barcode to medications

Revision ID: b7c3d9e14f20
Revises: 2902d29064c4
Create Date: 2026-07-23 00:00:00.000000

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = 'b7c3d9e14f20'
down_revision = '2902d29064c4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Idempotent: the app applies the same change on startup (app/db/init_db.py)
    op.execute("ALTER TABLE medications ADD COLUMN IF NOT EXISTS barcode VARCHAR")
    # A barcode identifies at most one medication per household
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_medications_household_barcode "
        "ON medications (household_id, barcode) WHERE barcode IS NOT NULL"
    )


def downgrade() -> None:
    op.drop_index('uq_medications_household_barcode', table_name='medications')
    op.drop_column('medications', 'barcode')
