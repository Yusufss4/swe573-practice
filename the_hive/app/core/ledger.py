"""
TimeBank ledger service for double-entry bookkeeping.

SRS Requirements:
- FR-7.1: TimeBank system tracks time exchanges
- FR-7.2: Provider gains hours, requester loses hours
- FR-7.3: Initial 5-hour credit
- FR-7.4: Reciprocity limit: can spend up to 10 hours over balance
- FR-7.5: All transactions logged for auditability
- FR-7.6: Separate transaction per participant
"""
from typing import Optional
from datetime import datetime

from sqlmodel import Session, select, func
from fastapi import HTTPException, status

from app.models.user import User
from app.models.participant import Participant, ParticipantStatus
from app.models.offer import Offer
from app.models.need import Need
from app.models.ledger import LedgerEntry, Transfer, TransactionType


RECIPROCITY_LIMIT = 10.0  # FR-7.4: Can go 10 hours into debt


def get_user_balance(session: Session, user_id: int) -> float:
    """
    Get the current balance for a user from the User table.
    
    Args:
        session: Database session
        user_id: User ID
        
    Returns:
        Current balance in hours
    """
    user = session.get(User, user_id)
    if not user:
        raise ValueError(f"User {user_id} not found")
    return user.balance


def create_ledger_entry(
    session: Session,
    user_id: int,
    debit: float = 0.0,
    credit: float = 0.0,
    transaction_type: TransactionType = TransactionType.EXCHANGE,
    description: str = "",
    participant_id: Optional[int] = None,
) -> LedgerEntry:
    """
    Create a ledger entry with double-entry bookkeeping.
    
    SRS Requirements:
    - FR-7.5: All transactions logged for auditability
    - FR-7.6: Separate transaction per participant
    
    Args:
        session: Database session
        user_id: User whose balance is affected
        debit: Hours deducted (provider spending)
        credit: Hours added (provider earning)
        transaction_type: Type of transaction
        description: Human-readable description
        participant_id: Reference to participant record if applicable
        
    Returns:
        Created LedgerEntry
    """
    # Get current balance
    user = session.get(User, user_id)
    if not user:
        raise ValueError(f"User {user_id} not found")
    
    # Calculate new balance
    new_balance = user.balance - debit + credit
    
    # Create ledger entry
    entry = LedgerEntry(
        user_id=user_id,
        debit=debit,
        credit=credit,
        balance=new_balance,
        transaction_type=transaction_type,
        description=description,
        participant_id=participant_id,
    )
    
    # Update user balance
    user.balance = new_balance
    
    session.add(entry)
    session.add(user)
    
    return entry


def check_reciprocity_limit(session: Session, user_id: int, hours_to_spend: float) -> tuple[bool, str]:
    """
    Check if user can spend hours without exceeding reciprocity limit.
    
    SRS Requirements:
    - FR-7.4: Users can spend up to 10 hours over their balance (reciprocity limit)
    - Warn or block if user tries to exceed limit without opening a Need
    
    Args:
        session: Database session
        user_id: User attempting to spend hours
        hours_to_spend: Hours they want to spend
        
    Returns:
        Tuple of (can_proceed: bool, message: str)
    """
    current_balance = get_user_balance(session, user_id)
    new_balance = current_balance - hours_to_spend
    
    # Calculate how much into debt they would be
    debt_amount = abs(min(0, new_balance))
    
    if debt_amount > RECIPROCITY_LIMIT:
        return False, (
            f"Cannot complete exchange: would exceed reciprocity limit. "
            f"Current balance: {current_balance:.1f}h, "
            f"Transaction: {hours_to_spend:.1f}h, "
            f"Would result in {debt_amount:.1f}h debt "
            f"(limit: {RECIPROCITY_LIMIT:.1f}h). "
            f"Please earn hours by fulfilling Needs before requesting more help."
        )
    
    # Warning if getting close to limit
    if debt_amount > RECIPROCITY_LIMIT * 0.8:  # 80% of limit
        warning = (
            f"Warning: Approaching reciprocity limit. "
            f"After this exchange, balance will be {new_balance:.1f}h "
            f"({debt_amount:.1f}h debt, limit: {RECIPROCITY_LIMIT:.1f}h). "
            f"Consider opening a Need to earn hours."
        )
        return True, warning
    
    return True, ""


def complete_exchange(
    session: Session,
    participant_id: int,
    completing_user_id: int,
) -> tuple[LedgerEntry | None, LedgerEntry | None, Transfer | None]:
    """
    Complete an exchange and create ledger entries (double-entry bookkeeping).
    
    Requires mutual confirmation - both provider and requester must call this
    endpoint before the exchange is finalized. Returns (None, None, None) if
    only one party has confirmed and waiting for the other.
    
    SRS Requirements:
    - FR-7.1: TimeBank system tracks time exchanges
    - FR-7.2: Provider gains hours (credit), requester loses hours (debit)
    - FR-7.4: Enforce reciprocity limit
    - FR-7.5: All transactions logged for auditability
    - FR-7.6: Separate transaction per participant
    
    This creates:
    1. Credit entry for provider (earning hours)
    2. Debit entry for requester (spending hours)
    3. Transfer record linking the two
    4. Updates both user balances
    
    Args:
        session: Database session
        participant_id: ID of the participant record
        completing_user_id: User initiating the completion
        
    Returns:
        Tuple of (provider_entry, requester_entry, transfer)
        
    Raises:
        HTTPException: If validation fails or reciprocity limit exceeded
    """
    # Get participant record
    participant = session.get(Participant, participant_id)
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant not found"
        )
    
    # Must be accepted before completion
    if participant.status != ParticipantStatus.ACCEPTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot complete: participant status is {participant.status}, must be accepted"
        )
    
    # Get the offer or need to determine requester
    if participant.offer_id:
        offer = session.get(Offer, participant.offer_id)
        if not offer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Offer not found"
            )
        requester_id = offer.creator_id
        item_type = "offer"
        item_id = offer.id
        item_title = offer.title
    elif participant.need_id:
        need = session.get(Need, participant.need_id)
        if not need:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Need not found"
            )
        requester_id = need.creator_id
        item_type = "need"
        item_id = need.id
        item_title = need.title
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Participant has no associated offer or need"
        )
    
    provider_id = participant.user_id
    hours = participant.hours_contributed
    
    # Verify completing user is either provider or requester
    if completing_user_id not in [provider_id, requester_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the provider or requester can complete this exchange"
        )
    
    # Track which party is confirming completion
    if completing_user_id == provider_id:
        if participant.provider_confirmed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already confirmed completion. Waiting for the other party."
            )
        participant.provider_confirmed = True
    else:  # completing_user_id == requester_id
        if participant.requester_confirmed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already confirmed completion. Waiting for the other party."
            )
        participant.requester_confirmed = True
    
    participant.updated_at = datetime.utcnow()
    
    # If both parties haven't confirmed yet, save and return early
    if not (participant.provider_confirmed and participant.requester_confirmed):
        session.add(participant)
        session.commit()
        session.refresh(participant)
        
        # Return None to indicate partial confirmation (waiting for other party)
        return None, None, None
    
    # Both parties confirmed - proceed with exchange completion
    
    # Check reciprocity limit for requester (FR-7.4)
    can_proceed, message = check_reciprocity_limit(session, requester_id, hours)
    if not can_proceed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # Double-entry bookkeeping (FR-7.2, FR-7.6)
    
    # 1. Provider CREDIT (earning hours)
    provider_entry = create_ledger_entry(
        session=session,
        user_id=provider_id,
        credit=hours,
        debit=0.0,
        transaction_type=TransactionType.EXCHANGE,
        description=f"Provided service: {item_title} ({hours:.1f}h)",
        participant_id=participant_id,
    )
    
    # 2. Requester DEBIT (spending hours)
    requester_entry = create_ledger_entry(
        session=session,
        user_id=requester_id,
        debit=hours,
        credit=0.0,
        transaction_type=TransactionType.EXCHANGE,
        description=f"Received service: {item_title} ({hours:.1f}h)",
        participant_id=participant_id,
    )
    
    # 3. Create transfer record (FR-7.5)
    transfer = Transfer(
        sender_id=requester_id,
        receiver_id=provider_id,
        amount=hours,
        transaction_type=TransactionType.EXCHANGE,
        participant_id=participant_id,
        notes=f"Exchange completed: {item_type} #{item_id} - {item_title}",
    )
    
    # 4. Mark participant as completed
    participant.status = ParticipantStatus.COMPLETED
    participant.updated_at = datetime.utcnow()
    
    session.add(transfer)
    session.add(participant)
    session.commit()
    
    # Refresh to get updated values
    session.refresh(provider_entry)
    session.refresh(requester_entry)
    session.refresh(transfer)
    
    return provider_entry, requester_entry, transfer


def get_user_ledger(
    session: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[LedgerEntry], int]:
    """
    Get ledger history for a user.
    
    SRS Requirements:
    - FR-7.5: All transactions logged for auditability
    - Audit trail visible in /me/ledger
    
    Args:
        session: Database session
        user_id: User ID
        skip: Pagination offset
        limit: Pagination limit
        
    Returns:
        Tuple of (entries, total_count)
    """
    # Get total count
    count_statement = select(func.count(LedgerEntry.id)).where(LedgerEntry.user_id == user_id)
    total = session.exec(count_statement).one()
    
    # Get entries ordered by most recent first
    statement = (
        select(LedgerEntry)
        .where(LedgerEntry.user_id == user_id)
        .order_by(LedgerEntry.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    entries = session.exec(statement).all()
    
    return list(entries), total


def verify_balance_integrity(session: Session, user_id: int) -> tuple[bool, str]:
    """
    Verify that user balance matches ledger entries (audit check).
    
    Args:
        session: Database session
        user_id: User ID to verify
        
    Returns:
        Tuple of (is_valid: bool, message: str)
    """
    user = session.get(User, user_id)
    if not user:
        return False, f"User {user_id} not found"
    
    # Calculate balance from ledger entries
    entries = session.exec(
        select(LedgerEntry).where(LedgerEntry.user_id == user_id)
    ).all()
    
    if not entries:
        # No entries, balance should be initial (5.0)
        if user.balance == 5.0:
            return True, "Balance correct (initial state)"
        else:
            return False, f"Balance mismatch: user has {user.balance}h but should have 5.0h (initial)"
    
    # Sum all debits and credits
    total_credits = sum(e.credit for e in entries)
    total_debits = sum(e.debit for e in entries)
    calculated_balance = 5.0 + total_credits - total_debits  # Start with initial 5.0 balance
    
    # Check if matches user balance
    if abs(user.balance - calculated_balance) < 0.01:  # Allow for floating point errors
        return True, f"Balance correct: {user.balance:.2f}h"
    else:
        return False, (
            f"Balance mismatch: user has {user.balance:.2f}h but ledger shows {calculated_balance:.2f}h "
            f"(initial: 5.0h, credits: {total_credits:.2f}h, debits: {total_debits:.2f}h)"
        )
