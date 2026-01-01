from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc, insert, delete
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from datetime import datetime
import re

from app.models.medication import Medication, medication_tags
from app.models.audit import InventoryEvent, EventReason
from app.models.household import Tag
from app.schemas.medication import (
    MedicationCreate,
    MedicationUpdate,
    MedicationResponse,
    MedicationList
)
from app.tasks.external_links import resolve_medication_links


class MedicationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    def normalize_name(self, name: str) -> str:
        """Normalize medication name for search and deduplication"""
        # Remove extra whitespace and convert to uppercase
        normalized = re.sub(r'\s+', ' ', name.strip().upper())
        # Remove common punctuation but keep Ukrainian characters
        normalized = re.sub(r'[^\w\s\u0400-\u04FF]', '', normalized)
        return normalized

    async def get_or_create_tags(self, household_id: int, tag_names: List[str]) -> List[Tag]:
        """Get existing tags or create new ones"""
        tags = []
        for tag_name in tag_names:
            tag_norm = self.normalize_name(tag_name)
            
            # Try to find existing tag
            result = await self.db.execute(
                select(Tag).where(
                    and_(Tag.household_id == household_id, Tag.name_norm == tag_norm)
                )
            )
            tag = result.scalar_one_or_none()
            
            if not tag:
                # Create new tag
                tag = Tag(
                    household_id=household_id,
                    name=tag_name,  # Store original name
                    name_norm=tag_norm
                )
                self.db.add(tag)
                await self.db.flush()  # Get the ID
            
            tags.append(tag)
        
        return tags

    async def create_medication(
        self,
        household_id: int,
        medication_data: MedicationCreate,
        created_by: int
    ) -> MedicationResponse:
        """Create a new medication"""
        name_norm = self.normalize_name(medication_data.name)
        
        # Check for existing medication with same normalized name
        existing = await self.db.execute(
            select(Medication).where(
                and_(
                    Medication.household_id == household_id,
                    Medication.name_norm == name_norm
                )
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Medication with this name already exists in household"
            )

        # Create medication
        medication = Medication(
            household_id=household_id,
            name_raw=medication_data.name,
            name_norm=name_norm,
            quantity=medication_data.quantity,
            description=medication_data.description,
            drlz_link=medication_data.drlz_link,
            drlz_instruction_link=medication_data.drlz_instruction_link,
            tabletki_link=medication_data.tabletki_link,
            notes=medication_data.notes,
            created_by=created_by
        )
        self.db.add(medication)
        await self.db.flush()

        # Handle tags
        if medication_data.tags:
            tags = await self.get_or_create_tags(household_id, medication_data.tags)
            for tag in tags:
                await self.db.execute(
                    insert(medication_tags).values(
                        medication_id=medication.id,
                        tag_id=tag.id
                    )
                )

        # Log inventory event
        if medication_data.quantity > 0:
            inventory_event = InventoryEvent(
                medication_id=medication.id,
                user_id=created_by,
                delta=medication_data.quantity,
                reason=EventReason.ADD
            )
            self.db.add(inventory_event)

        await self.db.commit()
        await self.db.refresh(medication)

        # Generate Tabletki link if not provided and we have a medication name
        if not medication_data.tabletki_link and medication_data.name:
            from urllib.parse import quote
            tabletki_url = f"https://tabletki.ua/uk/search/{quote(medication_data.name)}"
            medication.tabletki_link = tabletki_url
            await self.db.commit()
            await self.db.refresh(medication)

        # Trigger background link resolution for additional sources (if not already provided)
        if not (medication_data.drlz_link and medication_data.tabletki_link):
            resolve_medication_links.delay(medication.id, name_norm)

        return await self._medication_to_response(medication)

    async def get_household_medications(
        self,
        household_id: int,
        search: Optional[str] = None,
        tag_filter: Optional[str] = None,
        limit: int = 50,
        cursor: Optional[int] = None
    ) -> MedicationList:
        """Get medications for a household with search and filtering"""
        query = select(Medication).where(Medication.household_id == household_id)
        
        # Add search filter
        if search:
            search_norm = self.normalize_name(search)
            query = query.where(Medication.name_norm.ilike(f"%{search_norm}%"))
        
        # Add tag filter
        if tag_filter:
            tag_norm = self.normalize_name(tag_filter)
            query = query.join(medication_tags).join(Tag).where(Tag.name_norm == tag_norm)
        
        # Add cursor pagination
        if cursor:
            query = query.where(Medication.id > cursor)
        
        # Order and limit
        query = query.order_by(Medication.id).limit(limit + 1)
        
        result = await self.db.execute(query)
        medications = result.scalars().all()
        
        # Check if there are more results
        has_more = len(medications) > limit
        if has_more:
            medications = medications[:-1]
        
        next_cursor = medications[-1].id if medications and has_more else None
        
        # Convert to response format
        medication_responses = []
        for med in medications:
            medication_responses.append(await self._medication_to_response(med))
        
        # Get total count
        count_query = select(func.count(Medication.id)).where(Medication.household_id == household_id)
        if search:
            search_norm = self.normalize_name(search)
            count_query = count_query.where(Medication.name_norm.ilike(f"%{search_norm}%"))
        if tag_filter:
            tag_norm = self.normalize_name(tag_filter)
            count_query = count_query.join(medication_tags).join(Tag).where(Tag.name_norm == tag_norm)
        
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        return MedicationList(
            medications=medication_responses,
            total=total,
            next_cursor=next_cursor,
            has_more=has_more
        )

    async def get_medication(self, medication_id: int, household_id: int) -> Optional[MedicationResponse]:
        """Get a specific medication"""
        result = await self.db.execute(
            select(Medication).where(
                and_(
                    Medication.id == medication_id,
                    Medication.household_id == household_id
                )
            )
        )
        medication = result.scalar_one_or_none()
        if not medication:
            return None
        
        return await self._medication_to_response(medication)

    async def update_medication(
        self,
        medication_id: int,
        household_id: int,
        medication_update: MedicationUpdate,
        updated_by: int
    ) -> MedicationResponse:
        """Update medication details"""
        result = await self.db.execute(
            select(Medication).where(
                and_(
                    Medication.id == medication_id,
                    Medication.household_id == household_id
                )
            )
        )
        medication = result.scalar_one_or_none()
        if not medication:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Medication not found"
            )

        old_quantity = medication.quantity
        update_data = medication_update.dict(exclude_unset=True)
        
        # Handle name update
        if "name" in update_data:
            medication.name_raw = update_data["name"]
            medication.name_norm = self.normalize_name(update_data["name"])
        
        # Handle other fields
        for field, value in update_data.items():
            if field not in ["name", "tags"] and hasattr(medication, field):
                setattr(medication, field, value)
        
        medication.updated_at = datetime.utcnow()
        
        # Handle tags update
        if "tags" in update_data:
            # Remove existing tags
            await self.db.execute(
                delete(medication_tags).where(medication_tags.c.medication_id == medication_id)
            )
            
            # Add new tags
            if update_data["tags"]:
                tags = await self.get_or_create_tags(household_id, update_data["tags"])
                for tag in tags:
                    await self.db.execute(
                        insert(medication_tags).values(
                            medication_id=medication.id,
                            tag_id=tag.id
                        )
                    )

        # Log quantity change
        if "quantity" in update_data and update_data["quantity"] != old_quantity:
            delta = update_data["quantity"] - old_quantity
            inventory_event = InventoryEvent(
                medication_id=medication.id,
                user_id=updated_by,
                delta=delta,
                reason=EventReason.SET
            )
            self.db.add(inventory_event)

        await self.db.commit()
        await self.db.refresh(medication)

        return await self._medication_to_response(medication)

    async def decrement_medication(
        self,
        medication_id: int,
        household_id: int,
        amount: int,
        user_id: int
    ) -> MedicationResponse:
        """Decrement medication quantity"""
        result = await self.db.execute(
            select(Medication).where(
                and_(
                    Medication.id == medication_id,
                    Medication.household_id == household_id
                )
            )
        )
        medication = result.scalar_one_or_none()
        if not medication:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Medication not found"
            )

        # Check if we can decrement
        if medication.quantity < amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot decrement by {amount}. Current quantity: {medication.quantity}"
            )

        # Update quantity
        medication.quantity -= amount
        medication.updated_at = datetime.utcnow()

        # Log inventory event
        inventory_event = InventoryEvent(
            medication_id=medication.id,
            user_id=user_id,
            delta=-amount,
            reason=EventReason.DECREMENT
        )
        self.db.add(inventory_event)

        await self.db.commit()
        await self.db.refresh(medication)

        return await self._medication_to_response(medication)

    async def delete_medication(
        self,
        medication_id: int,
        household_id: int,
        deleted_by: int
    ) -> None:
        """Delete a medication"""
        result = await self.db.execute(
            select(Medication).where(
                and_(
                    Medication.id == medication_id,
                    Medication.household_id == household_id
                )
            )
        )
        medication = result.scalar_one_or_none()
        if not medication:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Medication not found"
            )

        await self.db.delete(medication)
        await self.db.commit()

    async def _medication_to_response(self, medication: Medication) -> MedicationResponse:
        """Convert medication model to response format with tags"""
        # Get tags
        tag_result = await self.db.execute(
            select(Tag.name_norm).join(medication_tags).where(
                medication_tags.c.medication_id == medication.id
            )
        )
        tags = [tag for tag in tag_result.scalars().all()]

        return MedicationResponse(
            id=medication.id,
            household_id=medication.household_id,
            name=medication.name_raw,
            name_norm=medication.name_norm,
            quantity=medication.quantity,
            description=medication.description,
            drlz_link=medication.drlz_link,
            drlz_instruction_link=medication.drlz_instruction_link,
            notes=medication.notes,
            tags=tags,
            tabletki_link=medication.tabletki_link,
            created_by=medication.created_by,
            created_at=medication.created_at,
            updated_at=medication.updated_at
        )