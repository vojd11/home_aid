from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from fastapi import HTTPException, status
from datetime import datetime

from app.models.household import Household, HouseholdMember
from app.models.user import User
from app.schemas.household import HouseholdCreate, HouseholdResponse, HouseholdMemberResponse


class HouseholdService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_household(self, household_data: HouseholdCreate, owner_id: int) -> HouseholdResponse:
        """Create a new household with the user as owner"""
        # Create household
        household = Household(name=household_data.name)
        self.db.add(household)
        await self.db.flush()

        # Add owner as member
        member = HouseholdMember(
            household_id=household.id,
            user_id=owner_id,
            role="owner"
        )
        self.db.add(member)
        
        await self.db.commit()
        await self.db.refresh(household)
        
        return HouseholdResponse.from_orm(household)

    async def get_user_households(self, user_id: int) -> List[HouseholdResponse]:
        """Get all households where user is a member"""
        result = await self.db.execute(
            select(Household)
            .join(HouseholdMember)
            .where(HouseholdMember.user_id == user_id)
            .order_by(Household.created_at)
        )
        households = result.scalars().all()
        return [HouseholdResponse.from_orm(h) for h in households]

    async def get_household(self, household_id: int, user_id: int) -> Optional[HouseholdResponse]:
        """Get household if user has access"""
        if not await self.check_user_access(household_id, user_id, "viewer"):
            return None
        
        household = await self.db.get(Household, household_id)
        if not household:
            return None
        
        return HouseholdResponse.from_orm(household)

    async def check_user_access(self, household_id: int, user_id: int, required_role: str = "viewer") -> bool:
        """Check if user has required access level to household"""
        result = await self.db.execute(
            select(HouseholdMember.role).where(
                and_(
                    HouseholdMember.household_id == household_id,
                    HouseholdMember.user_id == user_id
                )
            )
        )
        user_role = result.scalar_one_or_none()
        
        if not user_role:
            return False
        
        # Role hierarchy: owner > editor > viewer
        role_hierarchy = {"viewer": 1, "editor": 2, "owner": 3}
        user_level = role_hierarchy.get(user_role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        return user_level >= required_level

    async def invite_member(
        self, 
        household_id: int, 
        inviter_id: int,
        email: str, 
        role: str = "viewer"
    ) -> HouseholdMemberResponse:
        """Invite a user to household"""
        # Check if inviter has owner permissions
        if not await self.check_user_access(household_id, inviter_id, "owner"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only household owners can invite members"
            )

        # Find user by email
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User with this email not found"
            )

        # Check if user is already a member
        existing = await self.db.execute(
            select(HouseholdMember).where(
                and_(
                    HouseholdMember.household_id == household_id,
                    HouseholdMember.user_id == user.id
                )
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member of this household"
            )

        # Add member
        member = HouseholdMember(
            household_id=household_id,
            user_id=user.id,
            role=role,
            invited_at=datetime.utcnow()
        )
        self.db.add(member)
        await self.db.commit()
        await self.db.refresh(member)

        return HouseholdMemberResponse(
            id=member.id,
            household_id=member.household_id,
            user_id=member.user_id,
            user_email=user.email,
            role=member.role,
            invited_at=member.invited_at
        )

    async def get_household_members(self, household_id: int, user_id: int) -> List[HouseholdMemberResponse]:
        """Get all members of a household"""
        if not await self.check_user_access(household_id, user_id, "viewer"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this household"
            )

        result = await self.db.execute(
            select(HouseholdMember, User.email)
            .join(User)
            .where(HouseholdMember.household_id == household_id)
            .order_by(HouseholdMember.invited_at)
        )
        
        members = []
        for member, email in result.all():
            members.append(HouseholdMemberResponse(
                id=member.id,
                household_id=member.household_id,
                user_id=member.user_id,
                user_email=email,
                role=member.role,
                invited_at=member.invited_at
            ))
        
        return members

    async def update_member_role(
        self,
        household_id: int,
        member_user_id: int,
        new_role: str,
        updater_id: int
    ) -> HouseholdMemberResponse:
        """Update a member's role"""
        # Check if updater has owner permissions
        if not await self.check_user_access(household_id, updater_id, "owner"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only household owners can change member roles"
            )

        # Get member
        result = await self.db.execute(
            select(HouseholdMember, User.email)
            .join(User)
            .where(
                and_(
                    HouseholdMember.household_id == household_id,
                    HouseholdMember.user_id == member_user_id
                )
            )
        )
        member_data = result.first()
        if not member_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found"
            )

        member, email = member_data
        
        # Prevent demoting yourself if you're the only owner
        if member.user_id == updater_id and member.role == "owner" and new_role != "owner":
            owner_count = await self.db.execute(
                select(HouseholdMember).where(
                    and_(
                        HouseholdMember.household_id == household_id,
                        HouseholdMember.role == "owner"
                    )
                )
            )
            if len(owner_count.scalars().all()) == 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot demote the only owner"
                )

        # Update role
        member.role = new_role
        await self.db.commit()
        await self.db.refresh(member)

        return HouseholdMemberResponse(
            id=member.id,
            household_id=member.household_id,
            user_id=member.user_id,
            user_email=email,
            role=member.role,
            invited_at=member.invited_at
        )