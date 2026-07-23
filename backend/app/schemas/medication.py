from pydantic import BaseModel, constr, conint, HttpUrl
from typing import Optional, List
from datetime import datetime


class MedicationBase(BaseModel):
    name: constr(min_length=1)
    quantity: conint(ge=0) = 0
    description: Optional[str] = None
    notes: Optional[str] = None
    barcode: Optional[str] = None


class MedicationCreate(MedicationBase):
    tags: Optional[List[str]] = []
    drlz_link: Optional[str] = None
    drlz_instruction_link: Optional[str] = None
    tabletki_link: Optional[str] = None


class MedicationUpdate(BaseModel):
    name: Optional[constr(min_length=1)] = None
    quantity: Optional[conint(ge=0)] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    barcode: Optional[str] = None
    tags: Optional[List[str]] = None


class MedicationResponse(MedicationBase):
    id: int
    household_id: int
    name_norm: str
    description: Optional[str] = None
    drlz_link: Optional[HttpUrl] = None
    drlz_instruction_link: Optional[HttpUrl] = None
    tabletki_link: Optional[HttpUrl] = None
    tags: List[str] = []
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MedicationList(BaseModel):
    medications: List[MedicationResponse]
    total: int
    next_cursor: Optional[int] = None
    has_more: bool = False


class MedicationDecrement(BaseModel):
    amount: conint(ge=1) = 1


class MedicationLookupResponse(BaseModel):
    """Result of looking up a medication by scanned barcode within a household."""
    found: bool
    barcode: str
    medication: Optional[MedicationResponse] = None


class TagBase(BaseModel):
    name: constr(min_length=1)


class TagCreate(TagBase):
    pass


class TagResponse(TagBase):
    id: int
    household_id: int
    name_norm: str

    class Config:
        from_attributes = True
