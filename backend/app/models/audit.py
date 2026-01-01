from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey, Integer, Text, func, Enum
from sqlalchemy.orm import relationship
from .user import Base
import enum


class EventReason(enum.Enum):
    ADD = "ADD"
    DECREMENT = "DECREMENT"
    SET = "SET"
    IMPORT = "IMPORT"


class ResolutionStatus(enum.Enum):
    SUCCESS = "SUCCESS"
    NO_MATCH = "NO_MATCH"
    ERROR = "ERROR"


class ResolutionSource(enum.Enum):
    DRLZ = "DRLZ"
    TABLETKI = "TABLETKI"


class InventoryEvent(Base):
    __tablename__ = "inventory_events"

    id = Column(BigInteger, primary_key=True, index=True)
    medication_id = Column(BigInteger, ForeignKey("medications.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    delta = Column(Integer, nullable=False)
    reason = Column(Enum(EventReason), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    medication = relationship("Medication", back_populates="inventory_events")
    user = relationship("User")


class ActivityLog(Base):
    __tablename__ = "activity_log"

    id = Column(BigInteger, primary_key=True, index=True)
    household_id = Column(BigInteger, ForeignKey("households.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)
    entity_id = Column(BigInteger, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    meta = Column(Text, nullable=True)  # JSON string

    # Relationships
    household = relationship("Household")
    user = relationship("User")


class ExternalResolution(Base):
    __tablename__ = "external_resolutions"

    id = Column(BigInteger, primary_key=True, index=True)
    medication_id = Column(BigInteger, ForeignKey("medications.id", ondelete="CASCADE"), nullable=False)
    source = Column(Enum(ResolutionSource), nullable=False)
    query = Column(Text, nullable=False)
    result_title = Column(Text, nullable=True)
    page_url = Column(Text, nullable=True)
    instruction_url = Column(Text, nullable=True)
    status = Column(Enum(ResolutionStatus), nullable=False)
    http_status = Column(Integer, nullable=True)
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())
    hash = Column(String, nullable=True)

    # Relationships
    medication = relationship("Medication", back_populates="external_resolutions")
