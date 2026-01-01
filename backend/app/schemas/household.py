from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class HouseholdBase(BaseModel):
    name: str


class HouseholdCreate(HouseholdBase):
    pass


class HouseholdUpdate(BaseModel):
    name: Optional[str] = None


class HouseholdResponse(HouseholdBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class HouseholdMemberInvite(BaseModel):
    email: EmailStr
    role: str = "viewer"


class HouseholdMemberRoleUpdate(BaseModel):
    role: str


class HouseholdMemberResponse(BaseModel):
    id: int
    household_id: int
    user_id: int
    user_email: str
    role: str
    joined_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class HouseholdDetailResponse(HouseholdResponse):
    members: List[HouseholdMemberResponse] = []