from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_active_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.medication import (
    MedicationCreate,
    MedicationUpdate,
    MedicationResponse,
    MedicationList,
    MedicationLookupResponse
)
from app.schemas.store_prices import StorePricesResponse
from app.services.medication import MedicationService
from app.services.household import HouseholdService
from app.services.store_prices import StorePriceService

router = APIRouter()


async def verify_household_access(
    household_id: int,
    current_user: User,
    db: AsyncSession,
    required_role: str = "viewer"
) -> None:
    """Verify user has access to household with required role"""
    household_service = HouseholdService(db)
    has_access = await household_service.check_user_access(
        household_id, current_user.id, required_role
    )
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions for this household"
        )


@router.get("/{household_id}/medications", response_model=MedicationList)
async def get_medications(
    household_id: int,
    search: Optional[str] = Query(None, description="Search in medication names"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    limit: int = Query(50, ge=1, le=100),
    cursor: Optional[int] = Query(None, description="Pagination cursor"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> MedicationList:
    """Get medications for a household with optional search and filtering"""
    await verify_household_access(household_id, current_user, db, "viewer")
    
    medication_service = MedicationService(db)
    return await medication_service.get_household_medications(
        household_id=household_id,
        search=search,
        tag_filter=tag,
        limit=limit,
        cursor=cursor
    )


@router.post("/{household_id}/medications", response_model=MedicationResponse)
async def create_medication(
    household_id: int,
    medication_data: MedicationCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> MedicationResponse:
    """Add a new medication to household"""
    await verify_household_access(household_id, current_user, db, "editor")
    
    medication_service = MedicationService(db)
    return await medication_service.create_medication(
        household_id=household_id,
        medication_data=medication_data,
        created_by=current_user.id
    )


@router.get("/{household_id}/medications/lookup", response_model=MedicationLookupResponse)
async def lookup_medication_by_barcode(
    household_id: int,
    barcode: str = Query(..., description="Scanned package barcode (e.g. EAN-13)"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> MedicationLookupResponse:
    """Look up a medication in the household by scanned barcode.

    Returns whether a matching medication already exists. The mobile scan flow
    uses this to decide between adjusting an existing item's quantity or
    suggesting the creation of a new medication.
    """
    await verify_household_access(household_id, current_user, db, "viewer")

    medication_service = MedicationService(db)
    medication = await medication_service.get_medication_by_barcode(household_id, barcode)
    return MedicationLookupResponse(
        found=medication is not None,
        barcode=barcode.strip(),
        medication=medication
    )


@router.get("/{household_id}/medications/{medication_id}", response_model=MedicationResponse)
async def get_medication(
    household_id: int,
    medication_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> MedicationResponse:
    """Get specific medication details"""
    await verify_household_access(household_id, current_user, db, "viewer")
    
    medication_service = MedicationService(db)
    medication = await medication_service.get_medication(medication_id, household_id)
    if not medication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medication not found"
        )
    return medication


@router.patch("/{household_id}/medications/{medication_id}", response_model=MedicationResponse)
async def update_medication(
    household_id: int,
    medication_id: int,
    medication_update: MedicationUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> MedicationResponse:
    """Update medication details"""
    await verify_household_access(household_id, current_user, db, "editor")
    
    medication_service = MedicationService(db)
    return await medication_service.update_medication(
        medication_id=medication_id,
        household_id=household_id,
        medication_update=medication_update,
        updated_by=current_user.id
    )


@router.post("/{household_id}/medications/{medication_id}/increment", response_model=MedicationResponse)
async def increment_medication(
    household_id: int,
    medication_id: int,
    amount: int = 1,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> MedicationResponse:
    """Increment medication quantity by specified amount (default: 1)"""
    await verify_household_access(household_id, current_user, db, "editor")

    if amount < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Increment amount must be at least 1"
        )

    medication_service = MedicationService(db)
    return await medication_service.increment_medication(
        medication_id=medication_id,
        household_id=household_id,
        amount=amount,
        user_id=current_user.id
    )


@router.post("/{household_id}/medications/{medication_id}/decrement", response_model=MedicationResponse)
async def decrement_medication(
    household_id: int,
    medication_id: int,
    amount: int = 1,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> MedicationResponse:
    """Decrement medication quantity by specified amount (default: 1)"""
    await verify_household_access(household_id, current_user, db, "editor")
    
    medication_service = MedicationService(db)
    return await medication_service.decrement_medication(
        medication_id=medication_id,
        household_id=household_id,
        amount=amount,
        user_id=current_user.id
    )


@router.post("/{household_id}/medications/{medication_id}/resolve-links")
async def resolve_medication_links(
    household_id: int,
    medication_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Manually trigger external link resolution for a medication"""
    await verify_household_access(household_id, current_user, db, "editor")
    
    medication_service = MedicationService(db)
    medication = await medication_service.get_medication(medication_id, household_id)
    if not medication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medication not found"
        )
    
    # Trigger background link resolution
    from app.tasks.external_links import resolve_medication_links
    task = resolve_medication_links.delay(medication_id, medication.name_norm)
    
    return {
        "message": "Link resolution triggered",
        "task_id": task.id,
        "medication_id": medication_id
    }


@router.get("/{household_id}/medications/{medication_id}/store-prices", response_model=StorePricesResponse)
async def get_medication_store_prices(
    household_id: int,
    medication_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> StorePricesResponse:
    """Get current store prices for a medication from various pharmacy websites"""
    await verify_household_access(household_id, current_user, db, "viewer")
    
    medication_service = MedicationService(db)
    medication = await medication_service.get_medication(medication_id, household_id)
    if not medication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medication not found"
        )
    
    store_price_service = StorePriceService()
    return await store_price_service.get_all_store_prices(
        medication_id=medication_id,
        medication_name=medication.name  # Use .name instead of .name_raw
    )


@router.delete("/{household_id}/medications/{medication_id}")
async def delete_medication(
    household_id: int,
    medication_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a medication"""
    await verify_household_access(household_id, current_user, db, "editor")
    
    medication_service = MedicationService(db)
    await medication_service.delete_medication(
        medication_id=medication_id,
        household_id=household_id,
        deleted_by=current_user.id
    )
    return {"message": "Medication deleted successfully"}
