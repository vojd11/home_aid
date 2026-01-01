from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey, Text, func, UniqueConstraint
from sqlalchemy.orm import relationship
from .user import Base


class Household(Base):
    __tablename__ = "households"

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    members = relationship("HouseholdMember", back_populates="household", cascade="all, delete-orphan")
    medications = relationship("Medication", back_populates="household", cascade="all, delete-orphan")
    tags = relationship("Tag", back_populates="household", cascade="all, delete-orphan")


class HouseholdMember(Base):
    __tablename__ = "household_members"

    id = Column(BigInteger, primary_key=True, index=True)
    household_id = Column(BigInteger, ForeignKey("households.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, nullable=False)  # 'owner', 'editor', 'viewer'
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    household = relationship("Household", back_populates="members")
    user = relationship("User")


class Tag(Base):
    __tablename__ = "tags"

    id = Column(BigInteger, primary_key=True, index=True)
    household_id = Column(BigInteger, ForeignKey("households.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    name_norm = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    household = relationship("Household", back_populates="tags")
    medications = relationship("Medication", secondary="medication_tags", back_populates="tags")

    __table_args__ = (
        UniqueConstraint('household_id', 'name_norm', name='uq_household_tag_name_norm'),
    )
