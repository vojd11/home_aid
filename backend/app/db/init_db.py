from sqlalchemy import text

from app.models import Base
from app.db.database import engine

# create_all() only creates missing tables; it never alters existing ones.
# Columns and indexes added to an existing table are applied here so that
# databases created by an older version of the app pick them up on startup.
# Every statement must be idempotent (it runs on each start).
SCHEMA_UPGRADES = [
    # Scanned package barcode on medications
    "ALTER TABLE medications ADD COLUMN IF NOT EXISTS barcode VARCHAR",
    # Blank barcodes mean "no barcode"
    "UPDATE medications SET barcode = NULL WHERE barcode IS NOT NULL AND btrim(barcode) = ''",
    # Clear duplicate barcodes (keeping the oldest medication) so the unique
    # index below can be built; a no-op once that index exists
    """
    UPDATE medications m SET barcode = NULL
    FROM medications keep
    WHERE m.barcode IS NOT NULL
      AND keep.household_id = m.household_id
      AND keep.barcode = m.barcode
      AND keep.id < m.id
    """,
    "CREATE UNIQUE INDEX IF NOT EXISTS uq_medications_household_barcode "
    "ON medications (household_id, barcode) WHERE barcode IS NOT NULL",
]


async def init_db() -> None:
    """Initialize database tables"""
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

        # Bring existing tables up to date with the current models
        for statement in SCHEMA_UPGRADES:
            await conn.execute(text(statement))
