# Import all models to ensure they are registered with SQLAlchemy
from .user import User
from .household import Household, HouseholdMember, Tag
from .medication import Medication, medication_tags
from .audit import InventoryEvent, ActivityLog, ExternalResolution, EventReason, ResolutionStatus, ResolutionSource

# Export the Base class for Alembic
from .user import Base

__all__ = [
    "Base",
    "User", 
    "Household", 
    "HouseholdMember",
    "Medication", 
    "Tag", 
    "medication_tags",
    "InventoryEvent", 
    "ActivityLog", 
    "ExternalResolution",
    "EventReason",
    "ResolutionStatus", 
    "ResolutionSource"
]
