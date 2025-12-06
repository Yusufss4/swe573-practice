"""
API endpoints for comments.

SRS Requirements:
- FR-10.1: Comments only after completed exchange
- FR-10.2: Basic content moderation
- FR-10.3: Comments visible on profiles
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, func, select

from app.core.auth import CurrentUser
from app.core.db import get_session
from app.core.moderation import moderate_content, sanitize_content
from app.models.comment import Comment
from app.models.participant import Participant, ParticipantStatus
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentFilter, CommentListResponse, CommentResponse

router = APIRouter(prefix="/comments", tags=["Comments"])


def verify_completed_exchange(
    session: Session,
    commenter_id: int,
    recipient_id: int,
    participant_id: int
) -> Participant:
    """
    Verify that the commenter and recipient have completed an exchange together.
    
    SRS Requirement FR-10.1: Comments only after completed exchange
    
    Args:
        session: Database session
        commenter_id: User creating the comment
        recipient_id: User receiving the comment
        participant_id: Participant record linking the exchange
        
    Returns:
        The verified Participant record
        
    Raises:
        HTTPException: If verification fails
    """
    # Get the participant record
    participant = session.get(Participant, participant_id)
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant record not found"
        )
    
    # Must be completed
    if participant.status != ParticipantStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only comment on completed exchanges"
        )
    
    # Verify both users were part of the exchange
    # Get the offer or need to find the other party
    if participant.offer_id:
        from app.models.offer import Offer
        offer = session.get(Offer, participant.offer_id)
        if not offer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Associated offer not found"
            )
        
        # For offers: creator is requester, participant user is provider
        provider_id = participant.user_id
        requester_id = offer.creator_id
        
    elif participant.need_id:
        from app.models.need import Need
        need = session.get(Need, participant.need_id)
        if not need:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Associated need not found"
            )
        
        # For needs: creator is requester, participant user is provider
        provider_id = participant.user_id
        requester_id = need.creator_id
        
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Participant has no associated offer or need"
        )
    
    # Verify commenter and recipient are the two parties
    exchange_parties = {provider_id, requester_id}
    comment_parties = {commenter_id, recipient_id}
    
    if exchange_parties != comment_parties:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only comment on exchanges you participated in"
        )
    
    # Cannot comment on yourself
    if commenter_id == recipient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot comment on your own profile"
        )
    
    return participant


@router.post("", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    comment_data: CommentCreate,
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)]
) -> Comment:
    """
    Create a new comment after completing an exchange.
    
    SRS Requirements:
    - FR-10.1: Comments only after completed exchange
    - FR-10.2: Basic content moderation
    - FR-10.3: Comments visible on profiles
    
    Business Rules:
    - Can only comment on completed exchanges
    - Both users must have participated in the exchange
    - Cannot comment on yourself
    - Content must pass moderation
    - One comment per exchange per direction (can update later if needed)
    """
    if not current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found"
        )
    
    commenter_id = current_user.id
    
    # Verify the exchange was completed between these two users
    participant = verify_completed_exchange(
        session,
        commenter_id,
        comment_data.recipient_id,
        comment_data.participant_id
    )
    
    # Check if comment already exists for this exchange from this user
    existing_comment = session.exec(
        select(Comment).where(
            Comment.from_user_id == commenter_id,
            Comment.to_user_id == comment_data.recipient_id,
            Comment.participant_id == comment_data.participant_id
        )
    ).first()
    
    if existing_comment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already commented on this exchange"
        )
    
    # Sanitize content
    sanitized_content = sanitize_content(comment_data.content)
    
    # Moderate content (FR-10.2)
    is_approved, moderation_reason = moderate_content(sanitized_content)
    
    # Create comment
    comment = Comment(
        from_user_id=commenter_id,
        to_user_id=comment_data.recipient_id,
        participant_id=comment_data.participant_id,
        content=sanitized_content,
        is_moderated=True,
        is_approved=is_approved,
        moderation_reason=moderation_reason if not is_approved else None,
        is_visible=is_approved,  # Only visible if approved
    )
    
    session.add(comment)
    session.commit()
    session.refresh(comment)
    
    # If flagged, return error
    if not is_approved:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Comment rejected: {moderation_reason}"
        )
    
    return comment


@router.get("/user/{user_id}", response_model=CommentListResponse)
def get_user_comments(
    user_id: int,
    session: Annotated[Session, Depends(get_session)],
    skip: int = 0,
    limit: int = 20,
    exclude_flagged: bool = True
) -> CommentListResponse:
    """
    Get comments on a user's profile.
    
    SRS Requirement FR-10.3: Comments publicly visible on profiles
    
    Args:
        user_id: User whose comments to retrieve
        skip: Pagination offset
        limit: Pagination limit
        exclude_flagged: Whether to exclude flagged comments
        
    Returns:
        Paginated list of comments
    """
    # Verify user exists
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Build query
    query = select(Comment).where(
        Comment.to_user_id == user_id,
        Comment.is_visible == True
    )
    
    if exclude_flagged:
        query = query.where(Comment.is_approved == True)
    
    # Get total count
    count_query = select(func.count(Comment.id)).where(
        Comment.to_user_id == user_id,
        Comment.is_visible == True
    )
    if exclude_flagged:
        count_query = count_query.where(Comment.is_approved == True)
    
    total = session.exec(count_query).one()
    
    # Get paginated results
    query = query.order_by(Comment.timestamp.desc()).offset(skip).limit(limit)
    comments = session.exec(query).all()
    
    # Enrich with usernames
    comment_responses = []
    for comment in comments:
        commenter = session.get(User, comment.from_user_id)
        recipient = session.get(User, comment.to_user_id)
        
        comment_response = CommentResponse(
            id=comment.id,
            from_user_id=comment.from_user_id,
            from_username=commenter.username if commenter else None,
            to_user_id=comment.to_user_id,
            to_username=recipient.username if recipient else None,
            participant_id=comment.participant_id,
            content=comment.content,
            is_approved=comment.is_approved,
            timestamp=comment.timestamp
        )
        comment_responses.append(comment_response)
    
    return CommentListResponse(
        items=comment_responses,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/username/{username}", response_model=CommentListResponse)
def get_user_comments_by_username(
    username: str,
    session: Annotated[Session, Depends(get_session)],
    skip: int = 0,
    limit: int = 20,
    exclude_flagged: bool = True
) -> CommentListResponse:
    """
    Get comments on a user's profile by username.
    
    SRS Requirement FR-10.3: Comments publicly visible on profiles
    
    Args:
        username: Username whose comments to retrieve
        skip: Pagination offset
        limit: Pagination limit
        exclude_flagged: Whether to exclude flagged comments
        
    Returns:
        Paginated list of comments
    """
    # Find user by username
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user_id = user.id
    
    # Build query
    query = select(Comment).where(
        Comment.to_user_id == user_id,
        Comment.is_visible == True
    )
    
    if exclude_flagged:
        query = query.where(Comment.is_approved == True)
    
    # Get total count
    count_query = select(func.count(Comment.id)).where(
        Comment.to_user_id == user_id,
        Comment.is_visible == True
    )
    if exclude_flagged:
        count_query = count_query.where(Comment.is_approved == True)
    
    total = session.exec(count_query).one()
    
    # Get paginated results
    query = query.order_by(Comment.timestamp.desc()).offset(skip).limit(limit)
    comments = session.exec(query).all()
    
    # Enrich with usernames
    comment_responses = []
    for comment in comments:
        commenter = session.get(User, comment.from_user_id)
        recipient = session.get(User, comment.to_user_id)
        
        comment_response = CommentResponse(
            id=comment.id,
            from_user_id=comment.from_user_id,
            from_username=commenter.username if commenter else None,
            to_user_id=comment.to_user_id,
            to_username=recipient.username if recipient else None,
            participant_id=comment.participant_id,
            content=comment.content,
            is_approved=comment.is_approved,
            timestamp=comment.timestamp
        )
        comment_responses.append(comment_response)
    
    return CommentListResponse(
        items=comment_responses,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/my-comments", response_model=CommentListResponse)
def get_my_comments(
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
    skip: int = 0,
    limit: int = 20
) -> CommentListResponse:
    """
    Get comments written by the current user.
    
    Args:
        skip: Pagination offset
        limit: Pagination limit
        
    Returns:
        Paginated list of comments
    """
    if not current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found"
        )
    
    # Get total count
    count_query = select(func.count(Comment.id)).where(
        Comment.from_user_id == current_user.id
    )
    total = session.exec(count_query).one()
    
    # Get paginated results
    query = (
        select(Comment)
        .where(Comment.from_user_id == current_user.id)
        .order_by(Comment.timestamp.desc())
        .offset(skip)
        .limit(limit)
    )
    comments = session.exec(query).all()
    
    # Enrich with usernames
    comment_responses = []
    for comment in comments:
        recipient = session.get(User, comment.to_user_id)
        
        comment_response = CommentResponse(
            id=comment.id,
            from_user_id=comment.from_user_id,
            from_username=current_user.username,
            to_user_id=comment.to_user_id,
            to_username=recipient.username if recipient else None,
            participant_id=comment.participant_id,
            content=comment.content,
            is_approved=comment.is_approved,
            timestamp=comment.timestamp
        )
        comment_responses.append(comment_response)
    
    return CommentListResponse(
        items=comment_responses,
        total=total,
        skip=skip,
        limit=limit
    )
