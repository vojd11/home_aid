from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey, Integer, Text, func, Table
from sqlalchemy.orm import relationship
from .user import Base

# Association table for many-to-many relationship between medications and tags
medication_tags = Table(
    'medication_tags',
    Base.metadata,
    Column('medication_id', BigInteger, ForeignKey('medications.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', BigInteger, ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True)
)


class Medication(Base):
    __tablename__ = "medications"

    id = Column(BigInteger, primary_key=True, index=True)
    household_id = Column(BigInteger, ForeignKey("households.id", ondelete="CASCADE"), nullable=False)
    name_raw = Column(String, nullable=False)
    name_norm = Column(String, nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=0)
    description = Column(Text, nullable=True)  # For DRLZ description
    drlz_link = Column(Text, nullable=True)  # Link to DRLZ medication page
    drlz_instruction_link = Column(Text, nullable=True)  # Link to DRLZ instruction file
    tabletki_link = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_by = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    household = relationship("Household", back_populates="medications")
    creator = relationship("User")
    tags = relationship("Tag", secondary=medication_tags, back_populates="medications")
    inventory_events = relationship("InventoryEvent", back_populates="medication", cascade="all, delete-orphan")
    external_resolutions = relationship("ExternalResolution", back_populates="medication", cascade="all, delete-orphan")
