from sqlalchemy import text

from app.models import Base
from app.db.database import engine

# create_all() only creates missing tables; it never alters existing ones.
# Columns added to an existing table are applied here so that databases
# created by an older version of the app pick them up on startup.
# Every statement must be idempotent (it runs on each start).
SCHEMA_UPGRADES = [
    # Scanned package barcode on medications
    "ALTER TABLE medications ADD COLUMN IF NOT EXISTS barcode VARCHAR",
]

BARCODE_INDEX = "uq_medications_household_barcode"

# Run once, while the unique barcode index is missing (databases created
# before it existed): tidy existing barcodes so the index can be built
BARCODE_INDEX_SETUP = [
    # Blank barcodes mean "no barcode"
    "UPDATE medications SET barcode = NULL WHERE btrim(barcode) = ''",
    # Keep a duplicated barcode only on the oldest medication of the household
    """
    UPDATE medications m SET barcode = NULL
    FROM medications keep
    WHERE m.barcode IS NOT NULL
      AND keep.household_id = m.household_id
      AND keep.barcode = m.barcode
      AND keep.id < m.id
    """,
    f"CREATE UNIQUE INDEX {BARCODE_INDEX} "
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

        barcode_index_exists = await conn.scalar(
            text(
                "SELECT 1 FROM pg_indexes "
                "WHERE tablename = 'medications' AND indexname = :name"
            ),
            {"name": BARCODE_INDEX},
        )
        if not barcode_index_exists:
            for statement in BARCODE_INDEX_SETUP:
                await conn.execute(text(statement))
