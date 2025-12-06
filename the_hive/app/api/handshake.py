"""
Handshake mechanism API endpoints.

This module provides alternative endpoints for the handshake workflow
using the underlying Participant model.

SRS Requirements:
- FR-5.1: User can propose help with optional short message
- FR-5.2: Proposal marked as PENDING until explicitly accepted/rejected
- FR-5.3: Once accepted, exchange marked as confirmed/active
- FR-5: Handshake mechanism (pending → accepted workflow)

Note: These endpoints are semantic aliases to the participants API,
following the handshake terminology in the requirements.
"""
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select, and_

from app.core.auth import CurrentUser
from app.core.db import get_session
from app.models.offer import Offer, OfferStatus
from app.models.need import Need, NeedStatus
from app.models.participant import Participant, ParticipantStatus, ParticipantRole
from app.models.user import User
from app.schemas.participant import (
    ParticipantCreate,
    ParticipantAccept,
    ParticipantResponse,
    ParticipantListResponse,
)
from app.schemas.auth import UserPublic

router = APIRouter(prefix="/handshake", tags=["handshake"])


def _build_participant_response(session: Session, participant: Participant) -> ParticipantResponse:
    """Helper to build ParticipantResponse with user data."""
    user = session.get(User, participant.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User not found"
        )
    
    return ParticipantResponse(
        id=participant.id,
        offer_id=participant.offer_id,
        need_id=participant.need_id,
        user_id=participant.user_id,
        user=UserPublic(
            id=user.id,
            username=user.username,
            display_name=user.full_name or user.username
        ),
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


@router.post("/propose", response_model=ParticipantResponse, status_code=status.HTTP_201_CREATED)
def propose_help(
    item_type: Literal["offer", "need"],
    item_id: int,
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
    message: str = Query(None, max_length=500, description="Optional short message"),
) -> ParticipantResponse:
    """
    Propose to help with an Offer or Need (Handshake proposal).
    
    SRS Requirements:
    - FR-5.1: User can propose help with optional short message
    - FR-5.2: Proposal marked as PENDING (status=proposed) until explicitly accepted
    
    The proposal remains in PENDING status until the item creator accepts it.
    
    Args:
        item_type: Type of item ("offer" or "need")
        item_id: ID of the offer or need
        message: Optional short message with the proposal
        current_user: Authenticated user making the proposal
        session: Database session
        
    Returns:
        ParticipantResponse with status="pending" (proposed state)
    """
    if item_type == "offer":
        # Get the offer
        offer = session.get(Offer, item_id)
        if not offer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Offer not found"
            )
        
        # Check offer is active (not FULL)
        if offer.status == OfferStatus.FULL:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot propose: offer is already full"
            )
        
        if offer.status != OfferStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Offer is {offer.status}, cannot propose help"
            )
        
        # Cannot propose to own offer
        if offer.creator_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot propose help to your own offer"
            )
        
        # Check if user already has pending/accepted proposal
        existing = session.exec(
            select(Participant).where(
                and_(
                    Participant.offer_id == item_id,
                    Participant.user_id == current_user.id,
                    Participant.status.in_([ParticipantStatus.PENDING, ParticipantStatus.ACCEPTED])
                )
            )
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"You already have a {existing.status} proposal for this offer"
            )
        
        # Create handshake proposal
        participant = Participant(
            offer_id=item_id,
            user_id=current_user.id,
            role=ParticipantRole.PROVIDER,
            status=ParticipantStatus.PENDING,  # proposed state
            message=message,
        )
        
    else:  # need
        # Get the need
        need = session.get(Need, item_id)
        if not need:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Need not found"
            )
        
        # Check need is active (not FULL)
        if need.status == NeedStatus.FULL:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot propose: need is already full"
            )
        
        if need.status != NeedStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Need is {need.status}, cannot propose help"
            )
        
        # Cannot propose to own need
        if need.creator_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot propose help to your own need"
            )
        
        # Check if user already has pending/accepted proposal
        existing = session.exec(
            select(Participant).where(
                and_(
                    Participant.need_id == item_id,
                    Participant.user_id == current_user.id,
                    Participant.status.in_([ParticipantStatus.PENDING, ParticipantStatus.ACCEPTED])
                )
            )
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"You already have a {existing.status} proposal for this need"
            )
        
        # Create handshake proposal
        participant = Participant(
            need_id=item_id,
            user_id=current_user.id,
            role=ParticipantRole.PROVIDER,
            status=ParticipantStatus.PENDING,  # proposed state
            message=message,
        )
    
    session.add(participant)
    session.commit()
    session.refresh(participant)
    
    # Build response with user data
    return _build_participant_response(session, participant)


@router.post("/{handshake_id}/accept", response_model=ParticipantResponse)
def accept_handshake(
    handshake_id: int,
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
    hours: float = Query(..., gt=0, description="Hours for this exchange"),
) -> ParticipantResponse:
    """
    Accept a handshake proposal (only by the requester/owner).
    
    SRS Requirements:
    - FR-5.3: Once accepted, exchange marked as confirmed/active
    - FR-5: Handshake mechanism (pending → accepted workflow)
    - Ownership checks: Only the item creator (requester) can accept
    
    This atomically:
    1. Changes proposal status from PENDING to ACCEPTED
    2. Increments accepted_count on the offer/need
    3. Marks item as FULL if capacity reached
    
    Args:
        handshake_id: ID of the handshake proposal to accept
        hours: Hours allocated for this exchange
        current_user: Authenticated user (must be item creator)
        session: Database session
        
    Returns:
        ParticipantResponse with status="accepted"
        
    Raises:
        403: If current user is not the item creator
        400: If proposal is not pending or capacity already reached
        404: If handshake proposal not found
    """
    # Get the handshake proposal
    participant = session.get(Participant, handshake_id)
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Handshake proposal not found"
        )
    
    # Check proposal is pending
    if participant.status != ParticipantStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Handshake is already {participant.status}"
        )
    
    # Determine if this is for an offer or need
    if participant.offer_id is not None:
        # Get offer with row-level lock
        offer = session.exec(
            select(Offer)
            .where(Offer.id == participant.offer_id)
            .with_for_update()
        ).first()
        
        if not offer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Offer not found"
            )
        
        # OWNERSHIP CHECK: Only requester (offer creator) can accept
        if offer.creator_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the offer creator can accept this handshake proposal"
            )
        
        # Check capacity (cannot accept if FULL)
        if offer.accepted_count >= offer.capacity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot accept: offer capacity already reached"
            )
        
        # Atomic update: accept and increment
        participant.status = ParticipantStatus.ACCEPTED
        participant.hours_contributed = hours
        offer.accepted_count += 1
        
        # Mark as FULL if capacity reached
        if offer.accepted_count >= offer.capacity:
            offer.status = OfferStatus.FULL
        
        session.add(participant)
        session.add(offer)
        
    else:  # need
        # Get need with row-level lock
        need = session.exec(
            select(Need)
            .where(Need.id == participant.need_id)
            .with_for_update()
        ).first()
        
        if not need:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Need not found"
            )
        
        # OWNERSHIP CHECK: Only requester (need creator) can accept
        if need.creator_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the need creator can accept this handshake proposal"
            )
        
        # Check capacity (cannot accept if FULL)
        if need.accepted_count >= need.capacity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot accept: need capacity already reached"
            )
        
        # Atomic update: accept and increment
        participant.status = ParticipantStatus.ACCEPTED
        participant.hours_contributed = hours
        need.accepted_count += 1
        
        # Mark as FULL if capacity reached
        if need.accepted_count >= need.capacity:
            need.status = NeedStatus.FULL
        
        session.add(participant)
        session.add(need)
    
    session.commit()
    session.refresh(participant)
    
    # Build response with user data
    return _build_participant_response(session, participant)


@router.get("/my-proposals", response_model=ParticipantListResponse)
def list_my_proposals(
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
    status_filter: str = Query(None, description="Filter by status: pending, accepted, all"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> ParticipantListResponse:
    """
    List handshake proposals made by the current user.
    
    Allows proposer to see their pending proposals until accepted.
    
    Args:
        current_user: Authenticated user
        session: Database session
        status_filter: Optional filter ("pending", "accepted", or "all")
        skip: Pagination offset
        limit: Pagination limit
        
    Returns:
        ParticipantListResponse with proposals
    """
    # Build query
    statement = select(Participant).where(Participant.user_id == current_user.id)
    
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
    proposals = session.exec(statement).all()
    
    # Build response items with user data
    response_items = [_build_participant_response(session, p) for p in proposals]
    
    return ParticipantListResponse(
        items=response_items,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/pending-for-me", response_model=ParticipantListResponse)
def list_pending_proposals_for_my_items(
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> ParticipantListResponse:
    """
    List pending handshake proposals for items owned by the current user.
    
    Shows proposals that the current user (as requester) can accept.
    
    Args:
        current_user: Authenticated user (item creator/requester)
        session: Database session
        skip: Pagination offset
        limit: Pagination limit
        
    Returns:
        ParticipantListResponse with pending proposals awaiting acceptance
    """
    # Get all offers and needs created by current user
    my_offers = session.exec(
        select(Offer.id).where(Offer.creator_id == current_user.id)
    ).all()
    
    my_needs = session.exec(
        select(Need.id).where(Need.creator_id == current_user.id)
    ).all()
    
    # Build query for pending proposals
    statement = select(Participant).where(
        and_(
            Participant.status == ParticipantStatus.PENDING,
            (
                Participant.offer_id.in_(my_offers) if my_offers else False
            ) | (
                Participant.need_id.in_(my_needs) if my_needs else False
            )
        )
    ).order_by(Participant.created_at.desc())
    
    # Get total count
    total = len(session.exec(statement).all())
    
    # Apply pagination
    statement = statement.offset(skip).limit(limit)
    proposals = session.exec(statement).all()
    
    # Build response items with user data
    response_items = [_build_participant_response(session, p) for p in proposals]
    
    return ParticipantListResponse(
        items=response_items,
        total=total,
        skip=skip,
        limit=limit
    )
