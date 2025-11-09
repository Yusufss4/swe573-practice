"""
API endpoints for managing participants in offers and needs.

SRS Requirements:
- FR-5: Handshake mechanism
- FR-5.5: May accept multiple participants up to capacity
- FR-5.6: Offer/Need marked FULL when capacity reached
- FR-3.6: Creator can accept/decline offers of help
- FR-3.7: Prevent over-acceptance
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select, and_

from app.core.auth import CurrentUser
from app.core.db import get_session
from app.models.offer import Offer, OfferStatus
from app.models.need import Need, NeedStatus
from app.models.participant import Participant, ParticipantStatus, ParticipantRole
from app.schemas.participant import (
    ParticipantCreate,
    ParticipantAccept,
    ParticipantResponse,
    ParticipantListResponse,
)

router = APIRouter(prefix="/participants", tags=["participants"])


@router.post("/offers/{offer_id}", response_model=ParticipantResponse, status_code=status.HTTP_201_CREATED)
def offer_help_for_offer(
    offer_id: int,
    participant_data: ParticipantCreate,
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
) -> ParticipantResponse:
    """
    Offer help for an Offer (user wants to provide the service).
    
    SRS Requirements:
    - FR-5.1: User can offer help with optional message
    - FR-5.2: Offer marked as PENDING until explicitly accepted/rejected
    
    The participant status is PENDING until the offer creator accepts it.
    """
    # Get the offer
    offer = session.get(Offer, offer_id)
    if not offer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Offer not found"
        )
    
    # Check offer is active
    if offer.status != OfferStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Offer is {offer.status}, cannot offer help"
        )
    
    # Cannot offer help to own offer
    if offer.creator_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot offer help to your own offer"
        )
    
    # Check if user already offered help
    existing = session.exec(
        select(Participant).where(
            and_(
                Participant.offer_id == offer_id,
                Participant.user_id == current_user.id,
                Participant.status.in_([ParticipantStatus.PENDING, ParticipantStatus.ACCEPTED])
            )
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already offered help for this offer"
        )
    
    # Create participant record
    participant = Participant(
        offer_id=offer_id,
        user_id=current_user.id,
        role=ParticipantRole.PROVIDER,
        status=ParticipantStatus.PENDING,
        message=participant_data.message,
        selected_slot=participant_data.selected_slot,
    )
    
    session.add(participant)
    session.commit()
    session.refresh(participant)
    
    return participant


@router.post("/needs/{need_id}", response_model=ParticipantResponse, status_code=status.HTTP_201_CREATED)
def offer_help_for_need(
    need_id: int,
    participant_data: ParticipantCreate,
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
) -> ParticipantResponse:
    """
    Offer help for a Need (user wants to fulfill the service request).
    
    SRS Requirements:
    - FR-5.1: User can offer help with optional message
    - FR-5.2: Offer marked as PENDING until explicitly accepted/rejected
    
    The participant status is PENDING until the need creator accepts it.
    """
    # Get the need
    need = session.get(Need, need_id)
    if not need:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Need not found"
        )
    
    # Check need is active
    if need.status != NeedStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Need is {need.status}, cannot offer help"
        )
    
    # Cannot offer help to own need
    if need.creator_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot offer help to your own need"
        )
    
    # Check if user already offered help
    existing = session.exec(
        select(Participant).where(
            and_(
                Participant.need_id == need_id,
                Participant.user_id == current_user.id,
                Participant.status.in_([ParticipantStatus.PENDING, ParticipantStatus.ACCEPTED])
            )
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already offered help for this need"
        )
    
    # Create participant record
    participant = Participant(
        need_id=need_id,
        user_id=current_user.id,
        role=ParticipantRole.PROVIDER,
        status=ParticipantStatus.PENDING,
        message=participant_data.message,
        selected_slot=participant_data.selected_slot,
    )
    
    session.add(participant)
    session.commit()
    session.refresh(participant)
    
    return participant


@router.post("/offers/{offer_id}/accept", response_model=ParticipantResponse)
def accept_participant_for_offer(
    offer_id: int,
    accept_data: ParticipantAccept,
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
) -> ParticipantResponse:
    """
    Accept a participant for an Offer.
    
    SRS Requirements:
    - FR-3.6: Creator can accept offers of help
    - FR-3.7: Prevent over-acceptance (atomic check)
    - FR-5.3: Once accepted, exchange marked as confirmed/active
    - FR-5.5: May accept multiple participants up to capacity
    - FR-5.6: Offer marked FULL when capacity reached
    
    Uses atomic database transaction to prevent race conditions.
    Constraint: accepted_count < capacity
    """
    # Get the offer WITH row-level locking
    offer = session.exec(
        select(Offer)
        .where(Offer.id == offer_id)
        .with_for_update()
    ).first()
    
    if not offer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Offer not found"
        )
    
    # Only creator can accept participants
    if offer.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the offer creator can accept participants"
        )
    
    # Get the participant
    participant = session.get(Participant, accept_data.participant_id)
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant not found"
        )
    
    # Verify participant is for this offer
    if participant.offer_id != offer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Participant is not associated with this offer"
        )
    
    # Check participant is pending
    if participant.status != ParticipantStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Participant is already {participant.status}"
        )
    
    # CRITICAL: Check capacity constraint (FR-3.7)
    if offer.accepted_count >= offer.capacity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Offer capacity already reached"
        )
    
    # Atomic update: accept participant and increment count
    participant.status = ParticipantStatus.ACCEPTED
    participant.hours_contributed = accept_data.hours
    
    offer.accepted_count += 1
    
    # Mark as FULL if capacity reached (FR-5.6)
    if offer.accepted_count >= offer.capacity:
        offer.status = OfferStatus.FULL
    
    session.add(participant)
    session.add(offer)
    session.commit()
    session.refresh(participant)
    
    return participant


@router.post("/needs/{need_id}/accept", response_model=ParticipantResponse)
def accept_participant_for_need(
    need_id: int,
    accept_data: ParticipantAccept,
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
) -> ParticipantResponse:
    """
    Accept a participant for a Need.
    
    SRS Requirements:
    - FR-3.6: Creator can accept offers of help
    - FR-3.7: Prevent over-acceptance (atomic check)
    - FR-5.3: Once accepted, exchange marked as confirmed/active
    - FR-5.5: May accept multiple participants up to capacity
    - FR-5.6: Need marked FULL when capacity reached
    
    Uses atomic database transaction to prevent race conditions.
    Constraint: accepted_count < capacity
    """
    # Get the need WITH row-level locking
    need = session.exec(
        select(Need)
        .where(Need.id == need_id)
        .with_for_update()
    ).first()
    
    if not need:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Need not found"
        )
    
    # Only creator can accept participants
    if need.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the need creator can accept participants"
        )
    
    # Get the participant
    participant = session.get(Participant, accept_data.participant_id)
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant not found"
        )
    
    # Verify participant is for this need
    if participant.need_id != need_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Participant is not associated with this need"
        )
    
    # Check participant is pending
    if participant.status != ParticipantStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Participant is already {participant.status}"
        )
    
    # CRITICAL: Check capacity constraint (FR-3.7)
    if need.accepted_count >= need.capacity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Need capacity already reached"
        )
    
    # Atomic update: accept participant and increment count
    participant.status = ParticipantStatus.ACCEPTED
    participant.hours_contributed = accept_data.hours
    
    need.accepted_count += 1
    
    # Mark as FULL if capacity reached (FR-5.6)
    if need.accepted_count >= need.capacity:
        need.status = NeedStatus.FULL
    
    session.add(participant)
    session.add(need)
    session.commit()
    session.refresh(participant)
    
    return participant


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
    
    return ParticipantListResponse(
        items=participants,
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
    
    return ParticipantListResponse(
        items=participants,
        total=total,
        skip=skip,
        limit=limit
    )
