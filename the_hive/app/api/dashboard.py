"""Active Items Dashboard API endpoints.

SRS Requirements:
- FR-14: Active Items Dashboard for UI tabs
- FR-14.1: My Active Offers - offers created by user (exclude expired/completed)
- FR-14.2: My Active Needs - needs created by user (exclude expired/completed)
- FR-14.3: Applications I Submitted - where user applied (pending/accepted)
- FR-14.4: Accepted Participation - where user is accepted participant (exclude completed)
- FR-11.5: Platform statistics for moderator dashboard

This module provides filtered endpoints to feed UI tabs for active participation tracking
and platform-wide statistics for moderators.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session, select, func, or_

from app.core.auth import CurrentUser, ModeratorUser
from app.core.db import get_session
from app.models.offer import Offer, OfferStatus
from app.models.need import Need, NeedStatus
from app.models.participant import Participant, ParticipantStatus
from app.models.ledger import LedgerEntry
from app.models.user import User
from app.schemas.dashboard import (
    ActiveOfferResponse,
    ActiveNeedResponse,
    ApplicationResponse,
    ParticipationResponse,
    ActiveOffersListResponse,
    ActiveNeedsListResponse,
    ApplicationsListResponse,
    ParticipationsListResponse,
    DashboardStatsResponse,
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/my-active-offers", response_model=ActiveOffersListResponse)
def get_my_active_offers(
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> ActiveOffersListResponse:
    """Get user's active offers (FR-14.1).
    
    Returns offers created by the user, excluding:
    - EXPIRED offers
    - COMPLETED offers
    - CANCELLED offers
    
    Active statuses: ACTIVE, FULL
    """
    # Build query for active offers
    statement = select(Offer).where(
        Offer.creator_id == current_user.id,
        Offer.status.in_([OfferStatus.ACTIVE, OfferStatus.FULL])
    )
    
    # Count total
    count_statement = select(func.count()).select_from(Offer).where(
        Offer.creator_id == current_user.id,
        Offer.status.in_([OfferStatus.ACTIVE, OfferStatus.FULL])
    )
    total = session.exec(count_statement).one()
    
    # Apply pagination and ordering
    statement = statement.order_by(Offer.created_at.desc()).offset(skip).limit(limit)
    offers = session.exec(statement).all()
    
    return ActiveOffersListResponse(
        items=[ActiveOfferResponse.model_validate(offer) for offer in offers],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/my-active-needs", response_model=ActiveNeedsListResponse)
def get_my_active_needs(
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> ActiveNeedsListResponse:
    """Get user's active needs (FR-14.2).
    
    Returns needs created by the user, excluding:
    - EXPIRED needs
    - COMPLETED needs
    - CANCELLED needs
    
    Active statuses: ACTIVE, FULL
    """
    # Build query for active needs
    statement = select(Need).where(
        Need.creator_id == current_user.id,
        Need.status.in_([NeedStatus.ACTIVE, NeedStatus.FULL])
    )
    
    # Count total
    count_statement = select(func.count()).select_from(Need).where(
        Need.creator_id == current_user.id,
        Need.status.in_([NeedStatus.ACTIVE, NeedStatus.FULL])
    )
    total = session.exec(count_statement).one()
    
    # Apply pagination and ordering
    statement = statement.order_by(Need.created_at.desc()).offset(skip).limit(limit)
    needs = session.exec(statement).all()
    
    return ActiveNeedsListResponse(
        items=[ActiveNeedResponse.model_validate(need) for need in needs],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/my-applications", response_model=ApplicationsListResponse)
def get_my_applications(
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> ApplicationsListResponse:
    """Get applications submitted by user (FR-14.3).
    
    Returns participant records where user applied to help, including:
    - PENDING applications (awaiting acceptance)
    - ACCEPTED applications (confirmed participation)
    
    Excludes:
    - COMPLETED participations
    - DECLINED applications
    - CANCELLED applications
    
    Each application shows the offer/need title and creator info.
    """
    # Build query for applications
    statement = select(Participant).where(
        Participant.user_id == current_user.id,
        Participant.status.in_([ParticipantStatus.PENDING, ParticipantStatus.ACCEPTED])
    )
    
    # Count total
    count_statement = select(func.count()).select_from(Participant).where(
        Participant.user_id == current_user.id,
        Participant.status.in_([ParticipantStatus.PENDING, ParticipantStatus.ACCEPTED])
    )
    total = session.exec(count_statement).one()
    
    # Apply pagination and ordering
    statement = statement.order_by(Participant.created_at.desc()).offset(skip).limit(limit)
    participants = session.exec(statement).all()
    
    # Enrich with offer/need details
    applications = []
    for participant in participants:
        if participant.offer_id:
            offer = session.get(Offer, participant.offer_id)
            if offer:
                applications.append(ApplicationResponse(
                    id=participant.id,
                    offer_id=participant.offer_id,
                    need_id=None,
                    item_title=offer.title,
                    item_type="offer",
                    item_creator_id=offer.creator_id,
                    status=participant.status,
                    role=participant.role,
                    hours_contributed=participant.hours_contributed,
                    message=participant.message,
                    selected_slot=participant.selected_slot,
                    created_at=participant.created_at,
                ))
        elif participant.need_id:
            need = session.get(Need, participant.need_id)
            if need:
                applications.append(ApplicationResponse(
                    id=participant.id,
                    offer_id=None,
                    need_id=participant.need_id,
                    item_title=need.title,
                    item_type="need",
                    item_creator_id=need.creator_id,
                    status=participant.status,
                    role=participant.role,
                    hours_contributed=participant.hours_contributed,
                    message=participant.message,
                    selected_slot=participant.selected_slot,
                    created_at=participant.created_at,
                ))
    
    return ApplicationsListResponse(
        items=applications,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/my-participations", response_model=ParticipationsListResponse)
def get_my_participations(
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> ParticipationsListResponse:
    """Get accepted participations (FR-14.4).
    
    Returns participant records where user is accepted participant, excluding:
    - COMPLETED participations (finished exchanges)
    - PENDING applications (not yet accepted)
    - DECLINED applications
    - CANCELLED applications
    
    Only shows ACCEPTED participations (active exchanges).
    Each participation shows the offer/need title and creator info.
    """
    # Build query for accepted participations
    statement = select(Participant).where(
        Participant.user_id == current_user.id,
        Participant.status == ParticipantStatus.ACCEPTED
    )
    
    # Count total
    count_statement = select(func.count()).select_from(Participant).where(
        Participant.user_id == current_user.id,
        Participant.status == ParticipantStatus.ACCEPTED
    )
    total = session.exec(count_statement).one()
    
    # Apply pagination and ordering
    statement = statement.order_by(Participant.updated_at.desc()).offset(skip).limit(limit)
    participants = session.exec(statement).all()
    
    # Enrich with offer/need details
    participations = []
    for participant in participants:
        if participant.offer_id:
            offer = session.get(Offer, participant.offer_id)
            if offer:
                participations.append(ParticipationResponse(
                    id=participant.id,
                    offer_id=participant.offer_id,
                    need_id=None,
                    item_title=offer.title,
                    item_type="offer",
                    item_creator_id=offer.creator_id,
                    status=participant.status,
                    role=participant.role,
                    hours_contributed=participant.hours_contributed,
                    message=participant.message,
                    selected_slot=participant.selected_slot,
                    created_at=participant.created_at,
                    updated_at=participant.updated_at,
                ))
        elif participant.need_id:
            need = session.get(Need, participant.need_id)
            if need:
                participations.append(ParticipationResponse(
                    id=participant.id,
                    offer_id=None,
                    need_id=participant.need_id,
                    item_title=need.title,
                    item_type="need",
                    item_creator_id=need.creator_id,
                    status=participant.status,
                    role=participant.role,
                    hours_contributed=participant.hours_contributed,
                    message=participant.message,
                    selected_slot=participant.selected_slot,
                    created_at=participant.created_at,
                    updated_at=participant.updated_at,
                ))
    
    return ParticipationsListResponse(
        items=participations,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(
    moderator_user: ModeratorUser,
    session: Annotated[Session, Depends(get_session)],
) -> DashboardStatsResponse:
    """Get platform statistics for moderator dashboard (FR-11.5).
    
    Returns aggregate statistics:
    - Total and active offers/needs
    - Completed exchanges
    - Total hours exchanged
    - Active users
    """
    # Count total offers and needs
    total_offers_stmt = select(func.count()).select_from(Offer)
    total_offers = session.exec(total_offers_stmt).one()
    
    total_needs_stmt = select(func.count()).select_from(Need)
    total_needs = session.exec(total_needs_stmt).one()
    
    # Count active offers and needs
    active_offers_stmt = select(func.count()).select_from(Offer).where(
        Offer.status.in_([OfferStatus.ACTIVE, OfferStatus.FULL])
    )
    active_offers = session.exec(active_offers_stmt).one()
    
    active_needs_stmt = select(func.count()).select_from(Need).where(
        Need.status.in_([NeedStatus.ACTIVE, NeedStatus.FULL])
    )
    active_needs = session.exec(active_needs_stmt).one()
    
    # Count completed exchanges (participants with COMPLETED status)
    completed_stmt = select(func.count()).select_from(Participant).where(
        Participant.status == ParticipantStatus.COMPLETED
    )
    completed_exchanges = session.exec(completed_stmt).one()
    
    # Calculate total hours exchanged (sum of all ledger credits)
    # Credits represent hours earned, which equals hours spent by others
    hours_stmt = select(func.sum(LedgerEntry.credit)).select_from(LedgerEntry)
    total_hours = session.exec(hours_stmt).one()
    total_hours_exchanged = float(total_hours) if total_hours else 0.0
    
    # Count active users (users with at least one active offer or need)
    active_users_stmt = select(func.count(func.distinct(User.id))).select_from(User).where(
        or_(
            User.id.in_(
                select(Offer.creator_id).where(
                    Offer.status.in_([OfferStatus.ACTIVE, OfferStatus.FULL])
                )
            ),
            User.id.in_(
                select(Need.creator_id).where(
                    Need.status.in_([NeedStatus.ACTIVE, NeedStatus.FULL])
                )
            )
        )
    )
    active_users = session.exec(active_users_stmt).one()
    
    return DashboardStatsResponse(
        total_offers=total_offers,
        total_needs=total_needs,
        active_offers=active_offers,
        active_needs=active_needs,
        completed_exchanges=completed_exchanges,
        total_hours_exchanged=total_hours_exchanged,
        active_users=active_users,
    )
