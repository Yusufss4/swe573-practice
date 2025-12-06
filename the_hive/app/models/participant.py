from datetime import datetime
from typing import Optional
from enum import Enum

from sqlmodel import Field, SQLModel


class ParticipantRole(str, Enum):
    """Role in the exchange."""
    PROVIDER = "provider"  # Offering help
    REQUESTER = "requester"  # Requesting help


class ParticipantStatus(str, Enum):
    """Status of participation in an exchange.
    
    SRS Requirements:
    - FR-5.2: Offer marked as pending until explicitly accepted/rejected
    - FR-5.3: Once accepted, exchange marked as confirmed/active
    """
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Participant(SQLModel, table=True):
    """Tracks user participation in Offers/Needs (Handshake mechanism).
    
    SRS Requirements:
    - FR-5: Handshake mechanism
    - FR-5.1: Offer help with optional message
    - FR-5.5: Need/Offer may accept multiple participants up to capacity
    - FR-7.6: Separate transaction per participant
    - Database schema requirement (§3.5.1)
    """

    __tablename__ = "participants"

    id: Optional[int] = Field(default=None, primary_key=True)
    
    # References to either Offer or Need (one will be set)
    offer_id: Optional[int] = Field(default=None, foreign_key="offers.id", index=True)
    need_id: Optional[int] = Field(default=None, foreign_key="needs.id", index=True)
    
    # Participant user
    user_id: int = Field(foreign_key="users.id", index=True)
    
    # Role and status
    role: ParticipantRole = Field(index=True)
    status: ParticipantStatus = Field(default=ParticipantStatus.PENDING, index=True)
    
    # Hours contributed/received (FR-7.6)
    hours_contributed: float = Field(default=0.0)
    
    # Optional message when offering help (FR-5.1)
    message: Optional[str] = Field(default=None, max_length=500)
    
    # Selected time slot (if applicable)
    selected_slot: Optional[datetime] = Field(default=None)
    
    # Mutual completion confirmation flags
    # Both must be True for exchange to complete
    provider_confirmed: bool = Field(default=False)
    requester_confirmed: bool = Field(default=False)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
