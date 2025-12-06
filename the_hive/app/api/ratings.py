"""
API endpoints for the rating system.

SRS Requirements:
- FR-10.4: Multi-category rating system
- FR-10.5: Blind ratings with visibility control

Endpoints:
- POST /ratings/ - Submit a rating for a completed exchange
- GET /ratings/user/{user_id} - Get visible ratings for a user
- GET /ratings/status/{participant_id} - Check rating status for an exchange
- GET /ratings/summary/{user_id} - Get aggregated rating summary
- GET /ratings/labels - Get rating labels and category info
- POST /ratings/check-visibility - Manually trigger visibility check (admin)
"""
from datetime import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select, func

from app.core.auth import CurrentUser
from app.core.db import get_session
from app.core.moderation import moderate_content
from app.models.rating import Rating, RatingVisibility, RATING_VISIBILITY_DEADLINE_DAYS
from app.models.participant import Participant, ParticipantStatus
from app.models.offer import Offer
from app.models.need import Need
from app.models.user import User
from app.schemas.rating import (
    RatingCreate,
    RatingResponse,
    RatingListResponse,
    RatingStatusResponse,
    RatingCategoryLabelsResponse,
    UserRatingSummary,
    BlindRatingExplanation,
    RATING_LABELS,
    CATEGORY_INFO,
)

router = APIRouter(prefix="/ratings", tags=["ratings"])


def _get_other_party_id(session: Session, participant: Participant, user_id: int) -> int:
    """Get the other party's user ID from a participant record."""
    if participant.offer_id:
        offer = session.get(Offer, participant.offer_id)
        if not offer:
            raise HTTPException(status_code=404, detail="Offer not found")
        # If user is participant, other party is offer creator; vice versa
        return offer.creator_id if participant.user_id == user_id else participant.user_id
    elif participant.need_id:
        need = session.get(Need, participant.need_id)
        if not need:
            raise HTTPException(status_code=404, detail="Need not found")
        return need.creator_id if participant.user_id == user_id else participant.user_id
    else:
        raise HTTPException(status_code=400, detail="Invalid participant record")


def _check_rating_visibility(session: Session, rating: Rating) -> bool:
    """
    Check and update rating visibility based on blind rating rules.
    
    Returns True if rating should be visible.
    """
    if rating.visibility == RatingVisibility.VISIBLE:
        return True
    
    # Check if deadline has passed
    if rating.is_past_deadline():
        rating.visibility = RatingVisibility.VISIBLE
        rating.made_visible_at = datetime.utcnow()
        session.add(rating)
        session.commit()
        return True
    
    # Check if other party has rated
    other_rating = session.exec(
        select(Rating).where(
            Rating.participant_id == rating.participant_id,
            Rating.from_user_id == rating.to_user_id,  # Other party's rating
            Rating.to_user_id == rating.from_user_id
        )
    ).first()
    
    if other_rating:
        # Both parties have rated - make both visible
        rating.visibility = RatingVisibility.VISIBLE
        rating.made_visible_at = datetime.utcnow()
        other_rating.visibility = RatingVisibility.VISIBLE
        other_rating.made_visible_at = datetime.utcnow()
        session.add(rating)
        session.add(other_rating)
        session.commit()
        return True
    
    return False


def _build_rating_response(
    session: Session,
    rating: Rating,
    check_visibility: bool = True
) -> RatingResponse:
    """Build a RatingResponse with user info and visibility check."""
    from_user = session.get(User, rating.from_user_id)
    to_user = session.get(User, rating.to_user_id)
    
    is_visible = rating.visibility == RatingVisibility.VISIBLE
    if check_visibility and not is_visible:
        is_visible = _check_rating_visibility(session, rating)
    
    return RatingResponse.from_rating(
        rating,
        from_username=from_user.username if from_user else None,
        to_username=to_user.username if to_user else None,
        is_visible=is_visible
    )


@router.get("/labels", response_model=RatingCategoryLabelsResponse)
def get_rating_labels() -> RatingCategoryLabelsResponse:
    """
    Get rating labels and category information.
    
    Returns human-friendly labels for rating values and category descriptions
    for building the rating UI.
    """
    return RatingCategoryLabelsResponse(
        rating_labels=RATING_LABELS,
        categories=CATEGORY_INFO
    )


@router.get("/explanation", response_model=BlindRatingExplanation)
def get_rating_explanation() -> BlindRatingExplanation:
    """
    Get explanation of the blind rating system.
    
    Returns user-friendly explanation for display in UI.
    """
    return BlindRatingExplanation()


@router.post("/", response_model=RatingResponse, status_code=status.HTTP_201_CREATED)
def submit_rating(
    rating_data: RatingCreate,
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
) -> RatingResponse:
    """
    Submit a rating for a completed exchange.
    
    Requirements:
    - Exchange must be completed (participant status = COMPLETED)
    - User must be either the provider or requester of the exchange
    - User can only submit one rating per exchange
    - Rating is hidden until both parties submit or deadline passes
    
    Args:
        rating_data: Rating details including scores and optional comment
        
    Returns:
        Created rating (with visibility status)
        
    Raises:
        400: Exchange not completed or already rated
        403: User not involved in exchange
        404: Participant not found
    """
    # Get participant record
    participant = session.get(Participant, rating_data.participant_id)
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exchange not found"
        )
    
    # Determine if current user is provider or requester
    if participant.offer_id:
        offer = session.get(Offer, participant.offer_id)
        if not offer:
            raise HTTPException(status_code=404, detail="Offer not found")
        requester_id = offer.creator_id
        provider_id = participant.user_id
    else:
        need = session.get(Need, participant.need_id)
        if not need:
            raise HTTPException(status_code=404, detail="Need not found")
        requester_id = need.creator_id
        provider_id = participant.user_id
    
    # Check if user is involved
    if current_user.id not in {provider_id, requester_id}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only rate exchanges you participated in"
        )
    
    # Check if user has confirmed their part of the exchange
    # SRS: User can rate as soon as they confirm completion (no need to wait for other party)
    user_has_confirmed = False
    if current_user.id == provider_id:
        user_has_confirmed = participant.provider_confirmed
    else:
        user_has_confirmed = participant.requester_confirmed
    
    if participant.status != ParticipantStatus.ACCEPTED and participant.status != ParticipantStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Exchange must be accepted before rating."
        )
    
    if not user_has_confirmed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must confirm completion before rating. Click 'Complete' first."
        )
    
    # Determine the other party
    other_party_id = provider_id if current_user.id == requester_id else requester_id
    
    # Verify recipient is the other party
    if rating_data.recipient_id != other_party_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid recipient. You can only rate the other party in your exchange."
        )
    
    # Check for existing rating
    existing_rating = session.exec(
        select(Rating).where(
            Rating.from_user_id == current_user.id,
            Rating.participant_id == rating_data.participant_id
        )
    ).first()
    
    if existing_rating:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already submitted a rating for this exchange. Each exchange can only be rated once."
        )
    
    # Moderate public comment if provided
    comment_approved = True
    moderation_reason = None
    if rating_data.public_comment:
        is_appropriate, reason = moderate_content(rating_data.public_comment)
        if not is_appropriate:
            comment_approved = False
            moderation_reason = reason
    
    # Calculate general rating as average of the three category ratings
    general_rating = Rating.compute_general_rating(
        rating_data.reliability_rating,
        rating_data.kindness_rating,
        rating_data.helpfulness_rating
    )
    
    # Create rating
    rating = Rating(
        from_user_id=current_user.id,
        to_user_id=rating_data.recipient_id,
        participant_id=rating_data.participant_id,
        general_rating=general_rating,
        reliability_rating=rating_data.reliability_rating,
        kindness_rating=rating_data.kindness_rating,
        helpfulness_rating=rating_data.helpfulness_rating,
        public_comment=rating_data.public_comment,
        comment_is_moderated=rating_data.public_comment is not None,
        comment_is_approved=comment_approved,
        moderation_reason=moderation_reason,
    )
    
    session.add(rating)
    session.commit()
    session.refresh(rating)
    
    # Check if this makes ratings visible (other party already rated)
    _check_rating_visibility(session, rating)
    
    return _build_rating_response(session, rating, check_visibility=False)


@router.get("/status/{participant_id}", response_model=RatingStatusResponse)
def get_rating_status(
    participant_id: int,
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
) -> RatingStatusResponse:
    """
    Get rating status for an exchange.
    
    Returns information about whether the user can rate, has rated,
    and the current visibility state.
    """
    participant = session.get(Participant, participant_id)
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exchange not found"
        )
    
    # Determine if current user is provider or requester
    if participant.offer_id:
        offer = session.get(Offer, participant.offer_id)
        if not offer:
            raise HTTPException(status_code=404, detail="Offer not found")
        requester_id = offer.creator_id
        provider_id = participant.user_id
    else:
        need = session.get(Need, participant.need_id)
        if not need:
            raise HTTPException(status_code=404, detail="Need not found")
        requester_id = need.creator_id
        provider_id = participant.user_id
    
    # Check if user is involved
    if current_user.id not in {provider_id, requester_id}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not involved in this exchange"
        )
    
    other_party_id = provider_id if current_user.id == requester_id else requester_id
    
    # Check if user has confirmed their part
    user_has_confirmed = False
    if current_user.id == provider_id:
        user_has_confirmed = participant.provider_confirmed
    else:
        user_has_confirmed = participant.requester_confirmed
    
    # User can submit rating if they have confirmed their part (regardless of full completion)
    can_submit = user_has_confirmed and participant.status in [ParticipantStatus.ACCEPTED, ParticipantStatus.COMPLETED]
    
    # Check if user has already rated
    user_rating = session.exec(
        select(Rating).where(
            Rating.from_user_id == current_user.id,
            Rating.participant_id == participant_id
        )
    ).first()
    has_submitted = user_rating is not None
    
    # Check if other party has rated
    other_rating = session.exec(
        select(Rating).where(
            Rating.from_user_id == other_party_id,
            Rating.participant_id == participant_id
        )
    ).first()
    other_has_rated = other_rating is not None
    
    both_have_rated = has_submitted and other_has_rated
    
    # Determine visibility
    is_visible = both_have_rated
    visibility_deadline = None
    days_until_visible = None
    
    if user_rating:
        visibility_deadline = user_rating.visibility_deadline
        if not both_have_rated:
            days_remaining = (visibility_deadline - datetime.utcnow()).days
            days_until_visible = max(0, days_remaining)
            is_visible = days_until_visible <= 0
    
    # Generate friendly message
    if not user_has_confirmed:
        message = "Confirm completion first, then you can rate the other party."
    elif not has_submitted:
        message = "Share your experience! Your rating helps build trust in our community."
    elif not other_has_rated:
        message = f"Thank you for rating! Your feedback will become visible when the other party submits their rating, or in {days_until_visible} day{'s' if days_until_visible != 1 else ''}."
    else:
        message = "Both ratings are now visible. Thank you for your feedback!"
    
    return RatingStatusResponse(
        participant_id=participant_id,
        can_submit_rating=can_submit and not has_submitted,
        has_submitted_rating=has_submitted,
        other_party_has_rated=other_has_rated,
        both_have_rated=both_have_rated,
        is_visible=is_visible,
        visibility_deadline=visibility_deadline,
        days_until_visible=days_until_visible,
        message=message
    )


@router.get("/user/{user_id}", response_model=RatingListResponse)
def get_user_ratings(
    user_id: int,
    session: Annotated[Session, Depends(get_session)],
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> RatingListResponse:
    """
    Get visible ratings for a user.
    
    Only returns ratings that have passed the blind rating threshold
    (both parties rated or deadline passed).
    """
    # Verify user exists
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get visible ratings (check and update visibility as needed)
    statement = select(Rating).where(
        Rating.to_user_id == user_id
    ).order_by(Rating.created_at.desc())
    
    all_ratings = session.exec(statement).all()
    
    # Filter to only visible ratings
    visible_ratings = []
    for rating in all_ratings:
        if rating.visibility == RatingVisibility.VISIBLE:
            visible_ratings.append(rating)
        elif _check_rating_visibility(session, rating):
            visible_ratings.append(rating)
    
    total = len(visible_ratings)
    
    # Apply pagination
    paginated_ratings = visible_ratings[skip:skip + limit]
    
    items = [_build_rating_response(session, r, check_visibility=False) for r in paginated_ratings]
    
    return RatingListResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/summary/{user_id}", response_model=UserRatingSummary)
def get_user_rating_summary(
    user_id: int,
    session: Annotated[Session, Depends(get_session)],
) -> UserRatingSummary:
    """
    Get aggregated rating summary for a user.
    
    Returns average scores across all visible ratings for each category.
    """
    # Verify user exists
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get visible ratings
    statement = select(Rating).where(
        Rating.to_user_id == user_id,
        Rating.visibility == RatingVisibility.VISIBLE
    )
    ratings = session.exec(statement).all()
    
    if not ratings:
        return UserRatingSummary(
            user_id=user_id,
            total_ratings=0
        )
    
    # Calculate averages
    general_ratings = [r.general_rating for r in ratings]
    reliability_ratings = [r.reliability_rating for r in ratings if r.reliability_rating]
    kindness_ratings = [r.kindness_rating for r in ratings if r.kindness_rating]
    helpfulness_ratings = [r.helpfulness_rating for r in ratings if r.helpfulness_rating]
    
    # Calculate distribution
    distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for r in general_ratings:
        distribution[r] += 1
    
    # Calculate overall average (across all provided ratings)
    all_ratings_values = general_ratings.copy()
    all_ratings_values.extend(reliability_ratings)
    all_ratings_values.extend(kindness_ratings)
    all_ratings_values.extend(helpfulness_ratings)
    
    return UserRatingSummary(
        user_id=user_id,
        total_ratings=len(ratings),
        average_general=sum(general_ratings) / len(general_ratings) if general_ratings else None,
        average_reliability=sum(reliability_ratings) / len(reliability_ratings) if reliability_ratings else None,
        average_kindness=sum(kindness_ratings) / len(kindness_ratings) if kindness_ratings else None,
        average_helpfulness=sum(helpfulness_ratings) / len(helpfulness_ratings) if helpfulness_ratings else None,
        overall_average=sum(all_ratings_values) / len(all_ratings_values) if all_ratings_values else None,
        rating_distribution=distribution
    )


@router.get("/my-pending", response_model=RatingListResponse)
def get_my_pending_ratings(
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
) -> RatingListResponse:
    """
    Get the current user's ratings that are still hidden (pending visibility).
    
    Useful for showing users their submitted ratings that haven't become visible yet.
    """
    statement = select(Rating).where(
        Rating.from_user_id == current_user.id,
        Rating.visibility == RatingVisibility.HIDDEN
    ).order_by(Rating.created_at.desc())
    
    ratings = session.exec(statement).all()
    
    items = [_build_rating_response(session, r, check_visibility=True) for r in ratings]
    
    return RatingListResponse(
        items=items,
        total=len(items),
        skip=0,
        limit=len(items)
    )


@router.get("/exchange/{participant_id}", response_model=RatingListResponse)
def get_exchange_ratings(
    participant_id: int,
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
) -> RatingListResponse:
    """
    Get all ratings for a specific exchange.
    
    Returns both ratings if visible, or just the user's own rating if still hidden.
    """
    participant = session.get(Participant, participant_id)
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exchange not found"
        )
    
    # Get all ratings for this exchange
    statement = select(Rating).where(
        Rating.participant_id == participant_id
    ).order_by(Rating.created_at.desc())
    
    ratings = session.exec(statement).all()
    
    items = []
    for rating in ratings:
        is_own_rating = rating.from_user_id == current_user.id
        response = _build_rating_response(session, rating)
        
        # Show own rating always, others only if visible
        if is_own_rating or response.is_visible:
            items.append(response)
    
    return RatingListResponse(
        items=items,
        total=len(items),
        skip=0,
        limit=len(items)
    )
