from datetime import datetime
from typing import Optional
from enum import Enum

from sqlmodel import Field, SQLModel


class TransactionType(str, Enum):
    """Type of TimeBank transaction.
    
    SRS Requirements:
    - FR-7: TimeBank system tracks exchanges
    - FR-7.5: All transactions logged for auditability
    """
    EXCHANGE = "exchange"  # Normal service exchange
    INITIAL = "initial"  # Starting balance (5 hours)
    ADJUSTMENT = "adjustment"  # Admin correction
    PENALTY = "penalty"  # Moderation action


class LedgerEntry(SQLModel, table=True):
    """Double-entry ledger for TimeBank accounting.
    
    SRS Requirements:
    - FR-7.2: Update balance when exchange completed
    - FR-7.5: All transactions logged for auditability
    - FR-7.6: Separate transaction per participant
    - Database schema requirement (§3.5.1): debit/credit fields
    """

    __tablename__ = "ledger_entries"

    id: Optional[int] = Field(default=None, primary_key=True)
    
    # User account affected
    user_id: int = Field(foreign_key="users.id", index=True)
    
    # Double-entry accounting: debit (hours spent) or credit (hours earned)
    debit: float = Field(default=0.0)  # Hours deducted
    credit: float = Field(default=0.0)  # Hours added
    
    # Running balance after this entry
    balance: float = Field(default=0.0)
    
    # Transaction metadata
    transaction_type: TransactionType = Field(index=True)
    description: str = Field(max_length=500)
    
    # Reference to related exchange (if applicable)
    participant_id: Optional[int] = Field(default=None, foreign_key="participants.id")
    
    # Audit trail (NFR-8)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)


class Transfer(SQLModel, table=True):
    """Represents a TimeBank transfer between two users.
    
    SRS Requirements:
    - FR-7.2: Provider gains hours, requester loses hours
    - FR-7.7: Anti-hoarding rule for multi-participant exchanges
    - Database schema requirement (§3.5.1)
    """

    __tablename__ = "transfers"

    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Sender (requester losing hours) and receiver (provider gaining hours)
    sender_id: int = Field(foreign_key="users.id", index=True)
    receiver_id: int = Field(foreign_key="users.id", index=True)
    
    # Amount transferred
    amount: float = Field(gt=0)  # Must be positive
    
    # Transaction type and context
    transaction_type: TransactionType = Field(default=TransactionType.EXCHANGE)
    
    # Reference to participant record
    participant_id: Optional[int] = Field(default=None, foreign_key="participants.id")
    
    # Timestamp (FR-7.5)
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    # Audit notes
    notes: Optional[str] = Field(default=None, max_length=500)
