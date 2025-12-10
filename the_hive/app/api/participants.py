"""
API endpoints for viewing participants in offers and needs.

Note: Participant creation and acceptance has been moved to /api/v1/handshake/* endpoints
for better semantic clarity. This module now focuses on listing and completion functionality.

SRS Requirements:
- FR-5: Handshake mechanism
- FR-7: TimeBank ledger management
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from app.core.auth import CurrentUser
from app.core.db import get_session
from app.models.offer import Offer
from app.models.need import Need
from app.models.participant import Participant, ParticipantStatus
from app.models.user import User
from app.schemas.participant import (
    ParticipantResponse,
    ParticipantListResponse,
)
from app.schemas.auth import UserPublic

router = APIRouter(prefix="/participants", tags=["participants"])


def _build_participant_response(session: Session, participant: Participant) -> ParticipantResponse:
    """Build a ParticipantResponse with user info."""
    # Fetch user information
    user = session.get(User, participant.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found"
        )
    
    user_public = UserPublic(
        id=user.id,
        username=user.username,
        display_name=user.full_name,
        profile_image=user.profile_image,
        profile_image_type=user.profile_image_type,
    )
    
    return ParticipantResponse(
        id=participant.id,
        offer_id=participant.offer_id,
        need_id=participant.need_id,
        user_id=participant.user_id,
        user=user_public,
        role=participant.role.value,
        status=participant.status.value,
        hours_contributed=participant.hours_contributed,
        message=participant.message,
        selected_slot=participant.selected_slot,
        provider_confirmed=participant.provider_confirmed,
        requester_confirmed=participant.requester_confirmed,
        created_at=participant.created_at,
        updated_at=participant.updated_at,
    )


@router.get("/offers/{offer_id}", response_model=ParticipantListResponse)
def list_offer_participants(
    offer_id: int,
    session: Annotated[Session, Depends(get_session)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status_filter: str = Query(None, description="Filter by status: pending, accepted, all"),
) -> ParticipantListResponse:
    """List all participants for an offer."""
    # Verify offer exists
    offer = session.get(Offer, offer_id)
    if not offer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Offer not found"
        )
    
    # Build query
    statement = select(Participant).where(Participant.offer_id == offer_id)
    
    # Apply status filter
    if status_filter == "pending":
        statement = statement.where(Participant.status == ParticipantStatus.PENDING)
    elif status_filter == "accepted":
        statement = statement.where(Participant.status == ParticipantStatus.ACCEPTED)
    
    statement = statement.order_by(Participant.created_at.desc())
    
    # Get total count
    total = len(session.exec(statement).all())
    
    # Apply pagination
    statement = statement.offset(skip).limit(limit)
    participants = session.exec(statement).all()
    
    items = [_build_participant_response(session, p) for p in participants]
    
    return ParticipantListResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/needs/{need_id}", response_model=ParticipantListResponse)
def list_need_participants(
    need_id: int,
    session: Annotated[Session, Depends(get_session)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status_filter: str = Query(None, description="Filter by status: pending, accepted, all"),
) -> ParticipantListResponse:
    """List all participants for a need."""
    # Verify need exists
    need = session.get(Need, need_id)
    if not need:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Need not found"
        )
    
    # Build query
    statement = select(Participant).where(Participant.need_id == need_id)
    
    # Apply status filter
    if status_filter == "pending":
        statement = statement.where(Participant.status == ParticipantStatus.PENDING)
    elif status_filter == "accepted":
        statement = statement.where(Participant.status == ParticipantStatus.ACCEPTED)
    
    statement = statement.order_by(Participant.created_at.desc())
    
    # Get total count
    total = len(session.exec(statement).all())
    
    # Apply pagination
    statement = statement.offset(skip).limit(limit)
    participants = session.exec(statement).all()
    
    items = [_build_participant_response(session, p) for p in participants]
    
    return ParticipantListResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit
    )


@router.post("/exchange/{participant_id}/complete", status_code=status.HTTP_200_OK)
def complete_exchange_endpoint(
    participant_id: int,
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
):
    """
    Confirm completion of an exchange. Requires mutual confirmation.
    
    Both the provider and requester must call this endpoint before the 
    exchange is finalized and TimeBank balances are updated.
    
    SRS Requirements:
    - FR-7.1: TimeBank system tracks time exchanges
    - FR-7.2: Provider gains hours (credit), requester loses hours (debit)
    - FR-7.4: Enforce reciprocity limit (10 hours)
    - FR-7.5: All transactions logged for auditability
    - FR-7.6: Separate transaction per participant
    
    Creates double-entry ledger entries (only after both confirm):
    - Provider: CREDIT (earning hours)
    - Requester: DEBIT (spending hours)
    
    Updates both user balances and creates audit trail.
    
    Args:
        participant_id: ID of the participant/exchange to complete
        current_user: User completing the exchange (must be provider or requester)
        session: Database session
        
    Returns:
        ExchangeCompleteResponse with details and balances, or
        ConfirmationPendingResponse if waiting for other party
    """
    from app.core.ledger import complete_exchange, check_reciprocity_limit
    from app.schemas.ledger import ExchangeCompleteResponse
    from app.models.user import User
    
    # Complete the exchange (creates ledger entries or returns None if waiting)
    result = complete_exchange(
        session=session,
        participant_id=participant_id,
        completing_user_id=current_user.id,
    )
    
    # SRS FR-N.16: Need and Offer imports for notification context
    from app.core.notifications import notify_exchange_awaiting_confirmation, notify_exchange_completed
    from app.models.offer import Offer
    from app.models.need import Need
    
    # If returns all None, one party confirmed but waiting for the other
    if result[0] is None:
        participant = session.get(Participant, participant_id)
        
        # Determine who to notify (the party who hasn't confirmed yet)
        if participant.offer_id:
            offer = session.get(Offer, participant.offer_id)
            provider_id = participant.user_id
            requester_id = offer.creator_id
            item_title = offer.title
            item_id = offer.id
        else:
            need = session.get(Need, participant.need_id)
            provider_id = participant.user_id
            requester_id = need.creator_id
            item_title = need.title
            item_id = need.id
        
        # Notify the party who hasn't confirmed yet
        if participant.provider_confirmed and not participant.requester_confirmed:
            # Provider confirmed, notify requester
            provider = session.get(User, provider_id)
            notify_exchange_awaiting_confirmation(
                session=session,
                user_id=requester_id,
                other_party_username=provider.username,
                offer_title=item_title,
                offer_id=item_id,
                participant_id=participant_id,
            )
        elif participant.requester_confirmed and not participant.provider_confirmed:
            # Requester confirmed, notify provider
            requester = session.get(User, requester_id)
            notify_exchange_awaiting_confirmation(
                session=session,
                user_id=provider_id,
                other_party_username=requester.username,
                offer_title=item_title,
                offer_id=item_id,
                participant_id=participant_id,
            )
        
        return {
            "status": "pending_confirmation",
            "message": "Your confirmation has been recorded. Waiting for the other party to confirm.",
            "participant_id": participant_id,
            "provider_confirmed": participant.provider_confirmed,
            "requester_confirmed": participant.requester_confirmed,
        }
    
    # Both confirmed - exchange completed
    provider_entry, requester_entry, transfer = result
    
    # Both confirmed - exchange completed
    # Get updated balances
    provider = session.get(User, provider_entry.user_id)
    requester = session.get(User, requester_entry.user_id)
    
    # Check if there was a warning about reciprocity limit
    _, warning_message = check_reciprocity_limit(
        session, requester.id, 0  # Check current state
    )
    
    # SRS FR-N.14: Notify both parties that exchange is completed
    participant = session.get(Participant, participant_id)
    if participant.offer_id:
        offer = session.get(Offer, participant.offer_id)
        item_title = offer.title
        item_id = offer.id
    else:
        need = session.get(Need, participant.need_id)
        item_title = need.title
        item_id = need.id
    
    notify_exchange_completed(
        session=session,
        user_id=provider.id,
        other_party_username=requester.username,
        offer_title=item_title,
        offer_id=item_id,
        participant_id=participant_id,
    )
    notify_exchange_completed(
        session=session,
        user_id=requester.id,
        other_party_username=provider.username,
        offer_title=item_title,
        offer_id=item_id,
        participant_id=participant_id,
    )
    
    return ExchangeCompleteResponse(
        participant_id=participant_id,
        provider_id=provider.id,
        requester_id=requester.id,
        hours=transfer.amount,
        provider_new_balance=provider.balance,
        requester_new_balance=requester.balance,
        transfer_id=transfer.id,
        warning=warning_message if warning_message else None,
        completed_at=transfer.timestamp,
    )


@router.delete("/{participant_id}", status_code=status.HTTP_204_NO_CONTENT)
def decline_or_withdraw_participant(
    participant_id: int,
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
) -> None:
    """Decline or withdraw a participant application.
    
    - If the current user is the participant (applicant): withdraw their own application
    - If the current user is the offer/need creator: decline the application
    
    Only works for PENDING or ACCEPTED participants.
    """
    # Get the participant
    participant = session.get(Participant, participant_id)
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant not found"
        )
    
    # Check if user has permission (either the applicant or the creator)
    is_applicant = participant.user_id == current_user.id
    
    if participant.offer_id:
        offer = session.get(Offer, participant.offer_id)
        if not offer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Offer not found")
        is_creator = offer.creator_id == current_user.id
    elif participant.need_id:
        need = session.get(Need, participant.need_id)
        if not need:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Need not found")
        is_creator = need.creator_id == current_user.id
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid participant")
    
    if not is_applicant and not is_creator:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to modify this participant"
        )
    
    # Can only decline/withdraw PENDING or ACCEPTED participants
    if participant.status not in [ParticipantStatus.PENDING, ParticipantStatus.ACCEPTED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot decline/withdraw participant with status: {participant.status}"
        )
    
    # Store original status before updating
    original_status = participant.status
    
    # Update status based on who is declining
    if is_applicant:
        # Applicant is withdrawing
        participant.status = ParticipantStatus.CANCELLED
    else:
        # Creator is declining
        participant.status = ParticipantStatus.DECLINED
    
    # If the participant was ACCEPTED, update the accepted_count
    if original_status == ParticipantStatus.ACCEPTED:
        if participant.offer_id and offer:
            offer.accepted_count = max(0, offer.accepted_count - 1)
        elif participant.need_id and need:
            need.accepted_count = max(0, need.accepted_count - 1)
    
    session.add(participant)
    session.commit()
    
    return None
