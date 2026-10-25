"""
Tests for medication barcode scanning: startup schema upgrade, barcode
normalization/uniqueness, lookup and quantity adjustments.

These run against a real PostgreSQL database given by TEST_DATABASE_URL
(e.g. postgresql://postgres@localhost:5432/home_aid_test). The schema in that
database is dropped and recreated, so never point it at a database with data.
"""

import asyncio
import os

import pytest
import pytest_asyncio
from fastapi import HTTPException
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.deps import get_current_active_user
from app.db import init_db as init_db_module
from app.db.database import get_db
from app.main import app
from app.models import Base, Household, HouseholdMember, InventoryEvent, User
from app.schemas.medication import MedicationCreate, MedicationUpdate
from app.services import medication as medication_module
from app.services.medication import MedicationService

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.skipif(not TEST_DATABASE_URL, reason="TEST_DATABASE_URL is not set"),
]


class _NoopTask:
    def delay(self, *args, **kwargs):
        return None


@pytest_asyncio.fixture
async def engine(monkeypatch):
    test_engine = create_async_engine(
        TEST_DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    )
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    # Run startup schema creation/upgrade against the test database
    monkeypatch.setattr(init_db_module, "engine", test_engine)
    # Don't queue Celery link resolution when creating medications
    monkeypatch.setattr(medication_module, "resolve_medication_links", _NoopTask())

    yield test_engine
    await test_engine.dispose()


@pytest_asyncio.fixture
async def session(engine):
    await init_db_module.init_db()
    async with async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)() as db:
        yield db


async def _create_household(db: AsyncSession, email: str) -> tuple[User, Household]:
    user = User(email=email, password_hash="x")
    household = Household(name=f"Home of {email}")
    db.add_all([user, household])
    await db.flush()
    db.add(HouseholdMember(household_id=household.id, user_id=user.id, role="owner"))
    await db.commit()
    return user, household


async def _create(service: MedicationService, household: Household, user: User, name: str, barcode=None, quantity=0):
    return await service.create_medication(
        household_id=household.id,
        medication_data=MedicationCreate(name=name, barcode=barcode, quantity=quantity),
        created_by=user.id,
    )


async def _barcode_index_exists(conn) -> bool:
    result = await conn.execute(text(
        "SELECT 1 FROM pg_indexes WHERE indexname = 'uq_medications_household_barcode'"
    ))
    return result.first() is not None


async def test_startup_adds_barcode_to_existing_database(engine):
    # Simulate a database created before barcodes existed
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(text("DROP INDEX uq_medications_household_barcode"))
        await conn.execute(text("ALTER TABLE medications DROP COLUMN barcode"))

    await init_db_module.init_db()
    # Running again must be a no-op
    await init_db_module.init_db()

    async with engine.connect() as conn:
        column = await conn.execute(text(
            "SELECT 1 FROM information_schema.columns "
            "WHERE table_name = 'medications' AND column_name = 'barcode'"
        ))
        assert column.first() is not None
        assert await _barcode_index_exists(conn)


async def test_startup_clears_blank_and_duplicate_barcodes(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(text("DROP INDEX uq_medications_household_barcode"))
        await conn.execute(text(
            "INSERT INTO users (id, email, password_hash) VALUES (1, 'a@example.com', 'x')"
        ))
        await conn.execute(text("INSERT INTO households (id, name) VALUES (1, 'Home'), (2, 'Other')"))
        await conn.execute(text(
            "INSERT INTO medications (id, household_id, name_raw, name_norm, quantity, barcode) VALUES "
            "(1, 1, 'A', 'A', 0, '111'), "
            "(2, 1, 'B', 'B', 0, '111'), "
            "(3, 2, 'C', 'C', 0, '111'), "
            "(4, 1, 'D', 'D', 0, '   ')"
        ))

    await init_db_module.init_db()

    async with engine.connect() as conn:
        rows = await conn.execute(text("SELECT id, barcode FROM medications ORDER BY id"))
        # Oldest keeps the barcode, other households are unaffected, blanks become NULL
        assert rows.all() == [(1, "111"), (2, None), (3, "111"), (4, None)]
        assert await _barcode_index_exists(conn)


async def test_create_normalizes_and_rejects_duplicate_barcode(session):
    user, household = await _create_household(session, "a@example.com")
    _, other_household = await _create_household(session, "b@example.com")
    service = MedicationService(session)

    created = await _create(service, household, user, "Ibuprofen", barcode=" 4820000000017 ")
    assert created.barcode == "4820000000017"

    with pytest.raises(HTTPException) as exc:
        await _create(service, household, user, "Ibuprofen Forte", barcode="4820000000017")
    assert exc.value.status_code == 400
    assert "barcode" in exc.value.detail

    # The same barcode is fine in another household
    other = await _create(service, other_household, user, "Ibuprofen", barcode="4820000000017")
    assert other.barcode == "4820000000017"

    # Blank barcodes are stored as "no barcode" and never conflict
    first_blank = await _create(service, household, user, "Aspirin", barcode="  ")
    second_blank = await _create(service, household, user, "Vitamin D3", barcode="")
    assert first_blank.barcode is None
    assert second_blank.barcode is None


async def test_update_barcode_rejects_conflicts(session):
    user, household = await _create_household(session, "a@example.com")
    service = MedicationService(session)
    first = await _create(service, household, user, "Ibuprofen", barcode="111")
    second = await _create(service, household, user, "Aspirin")

    with pytest.raises(HTTPException) as exc:
        await service.update_medication(second.id, household.id, MedicationUpdate(barcode="111"), user.id)
    assert exc.value.status_code == 400

    # Re-saving a medication with its own barcode is allowed
    unchanged = await service.update_medication(first.id, household.id, MedicationUpdate(barcode="111"), user.id)
    assert unchanged.barcode == "111"

    linked = await service.update_medication(second.id, household.id, MedicationUpdate(barcode=" 222 "), user.id)
    assert linked.barcode == "222"

    cleared = await service.update_medication(second.id, household.id, MedicationUpdate(barcode=""), user.id)
    assert cleared.barcode is None


async def test_lookup_and_quantity_adjustments(session):
    user, household = await _create_household(session, "a@example.com")
    service = MedicationService(session)
    medication = await _create(service, household, user, "Ibuprofen", barcode="111", quantity=2)

    found = await service.get_medication_by_barcode(household.id, " 111 ")
    assert found.id == medication.id
    assert await service.get_medication_by_barcode(household.id, "999") is None
    assert await service.get_medication_by_barcode(household.id, "  ") is None

    increased = await service.increment_medication(medication.id, household.id, 3, user.id)
    assert increased.quantity == 5
    decreased = await service.decrement_medication(medication.id, household.id, 4, user.id)
    assert decreased.quantity == 1

    with pytest.raises(HTTPException) as exc:
        await service.decrement_medication(medication.id, household.id, 2, user.id)
    assert exc.value.status_code == 400

    events = await session.execute(
        text("SELECT delta, reason FROM inventory_events WHERE medication_id = :id ORDER BY id"),
        {"id": medication.id},
    )
    assert events.all() == [(2, "ADD"), (3, "ADD"), (-4, "DECREMENT")]


async def test_lookup_route_is_not_shadowed_by_medication_id_route(session):
    user, household = await _create_household(session, "a@example.com")
    medication = await _create(MedicationService(session), household, user, "Ibuprofen", barcode="111")

    async def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_active_user] = lambda: user
    try:
        async with AsyncClient(app=app, base_url="http://test") as client:
            base = f"/api/v1/households/{household.id}/medications"

            hit = await client.get(f"{base}/lookup", params={"barcode": "111"})
            assert hit.status_code == 200
            assert hit.json()["found"] is True
            assert hit.json()["medication"]["id"] == medication.id

            miss = await client.get(f"{base}/lookup", params={"barcode": "999"})
            assert miss.status_code == 200
            assert miss.json() == {"found": False, "barcode": "999", "medication": None}

            increment = await client.post(f"{base}/{medication.id}/increment", params={"amount": 2})
            assert increment.status_code == 200
            assert increment.json()["quantity"] == 2

            # Numeric ids still reach the single-medication route
            single = await client.get(f"{base}/{medication.id}")
            assert single.status_code == 200
            assert single.json()["barcode"] == "111"
    finally:
        app.dependency_overrides.clear()


async def test_concurrent_quantity_changes_are_not_lost(engine, session):
    user, household = await _create_household(session, "a@example.com")
    medication = await _create(MedicationService(session), household, user, "Ibuprofen", quantity=5)
    make_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Several household members tap "Add 1" on the same package at once
    async def add_one():
        async with make_session() as db:
            await MedicationService(db).increment_medication(medication.id, household.id, 1, user.id)

    await asyncio.gather(*(add_one() for _ in range(5)))

    quantity = await session.scalar(
        text("SELECT quantity FROM medications WHERE id = :id"), {"id": medication.id}
    )
    assert quantity == 10


async def test_quantity_change_amount_is_validated(session):
    user, household = await _create_household(session, "a@example.com")
    medication = await _create(MedicationService(session), household, user, "Ibuprofen", quantity=5)

    async def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_active_user] = lambda: user
    try:
        async with AsyncClient(app=app, base_url="http://test") as client:
            base = f"/api/v1/households/{household.id}/medications/{medication.id}"
            for action in ("increment", "decrement"):
                for amount in (0, -5, 10001):
                    response = await client.post(f"{base}/{action}", params={"amount": amount})
                    assert response.status_code == 422, (action, amount)
    finally:
        app.dependency_overrides.clear()

    quantity = await session.scalar(
        text("SELECT quantity FROM medications WHERE id = :id"), {"id": medication.id}
    )
    assert quantity == 5


async def test_startup_barcode_cleanup_runs_only_while_index_is_missing(session):
    user, household = await _create_household(session, "a@example.com")
    await _create(MedicationService(session), household, user, "Ibuprofen", barcode="111")
    # A blank barcode the API would never store; the one-time cleanup would clear it
    await session.execute(text("UPDATE medications SET barcode = ' '"))
    await session.commit()

    # Later restarts must not re-run the full-table cleanup
    await init_db_module.init_db()

    assert await session.scalar(text("SELECT barcode FROM medications")) == " "
