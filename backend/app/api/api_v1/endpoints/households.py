from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_active_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.household import (
    HouseholdCreate,
    HouseholdResponse,
    HouseholdMemberInvite,
    HouseholdMemberResponse,
    HouseholdMemberRoleUpdate
)
from app.services.household import HouseholdService

router = APIRouter()


@router.get("/", response_model=List[HouseholdResponse])
async def get_households(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> List[HouseholdResponse]:
    """Get user's households"""
    household_service = HouseholdService(db)
    return await household_service.get_user_households(current_user.id)


@router.post("/", response_model=HouseholdResponse)
async def create_household(
    household_data: HouseholdCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> HouseholdResponse:
    """Create a new household"""
    household_service = HouseholdService(db)
    return await household_service.create_household(household_data, current_user.id)


@router.get("/{household_id}", response_model=HouseholdResponse)
async def get_household(
    household_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> HouseholdResponse:
    """Get household details"""
    household_service = HouseholdService(db)
    household = await household_service.get_household(household_id, current_user.id)
    if not household:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Household not found or access denied"
        )
    return household


@router.get("/{household_id}/members", response_model=List[HouseholdMemberResponse])
async def get_household_members(
    household_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> List[HouseholdMemberResponse]:
    """Get household members"""
    household_service = HouseholdService(db)
    return await household_service.get_household_members(household_id, current_user.id)


@router.post("/{household_id}/members", response_model=HouseholdMemberResponse)
async def invite_member(
    household_id: int,
    member_data: HouseholdMemberInvite,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> HouseholdMemberResponse:
    """Invite a user to household"""
    household_service = HouseholdService(db)
    return await household_service.invite_member(
        household_id=household_id,
        inviter_id=current_user.id,
        email=member_data.email,
        role=member_data.role
    )


@router.patch("/{household_id}/members/{user_id}", response_model=HouseholdMemberResponse)
async def update_member_role(
    household_id: int,
    user_id: int,
    role_update: HouseholdMemberRoleUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> HouseholdMemberResponse:
    """Update member role"""
    household_service = HouseholdService(db)
    return await household_service.update_member_role(
        household_id=household_id,
        member_user_id=user_id,
        new_role=role_update.role,
        updater_id=current_user.id
    )
