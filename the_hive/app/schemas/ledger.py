"""
Schemas for ledger and exchange operations.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class LedgerEntryResponse(BaseModel):
    """Schema for ledger entry response."""
    id: int
    user_id: int
    debit: float
    credit: float
    balance: float
    transaction_type: str
    description: str
    participant_id: Optional[int]
    created_at: datetime
    
    model_config = {"from_attributes": True}


class LedgerHistoryResponse(BaseModel):
    """Schema for paginated ledger history."""
    items: list[LedgerEntryResponse]
    total: int
    skip: int
    limit: int
    current_balance: float


class ExchangeCompleteResponse(BaseModel):
    """Schema for exchange completion response."""
    participant_id: int
    provider_id: int
    requester_id: int
    hours: float
    provider_new_balance: float
    requester_new_balance: float
    transfer_id: int
    warning: Optional[str] = None
    completed_at: datetime
