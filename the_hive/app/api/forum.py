"""
API endpoints for forum.

SRS Requirements:
- FR-15: Basic forum with moderation hooks
- FR-15.1: Create/list topics (types: discussion, event)
- FR-15.2: Search by tag/keyword
- FR-15.3: Link optional Offer/Need to events
- FR-15.4: Events ordered by recency
- FR-15.5: Links visible both ways (bidirectional)
"""
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, func, or_, select

from app.core.auth import CurrentUser
from app.core.db import get_session
from app.models.forum import ForumComment, ForumTopic, ForumTopicTag, TopicType
from app.models.need import Need
from app.models.offer import Offer
from app.models.tag import Tag
from app.models.user import User
from app.schemas.forum import (
    ForumCommentCreate,
    ForumCommentListResponse,
    ForumCommentResponse,
    ForumCommentUpdate,
    ForumTopicCreate,
    ForumTopicListResponse,
    ForumTopicResponse,
    ForumTopicUpdate,
    LinkedItemInfo,
)

router = APIRouter(prefix="/forum", tags=["Forum"])


def get_or_create_tag(session: Session, tag_name: str) -> Tag:
    """Get existing tag or create new one."""
    tag = session.exec(select(Tag).where(Tag.name == tag_name.lower())).first()
    if not tag:
        tag = Tag(name=tag_name.lower())
        session.add(tag)
        session.flush()
    return tag


def associate_tags_to_topic(session: Session, topic_id: int, tag_names: list[str]) -> None:
    """Associate tags with a forum topic."""
    for tag_name in tag_names:
        tag = get_or_create_tag(session, tag_name)
        
        # Check if association already exists
        existing = session.exec(
            select(ForumTopicTag).where(
                ForumTopicTag.topic_id == topic_id,
                ForumTopicTag.tag_id == tag.id
            )
        ).first()
        
        if not existing:
            topic_tag = ForumTopicTag(topic_id=topic_id, tag_id=tag.id)
            session.add(topic_tag)
            
            # Update tag usage count
            tag.usage_count += 1
            session.add(tag)


def get_topic_tags(session: Session, topic_id: int) -> list[str]:
    """Get all tags for a topic."""
    tags = session.exec(
        select(Tag)
        .join(ForumTopicTag, ForumTopicTag.tag_id == Tag.id)
        .where(ForumTopicTag.topic_id == topic_id)
    ).all()
    return [tag.name for tag in tags]


def get_linked_item_info(session: Session, topic: ForumTopic) -> Optional[LinkedItemInfo]:
    """Get information about linked offer/need (FR-15.5)."""
    if topic.linked_offer_id:
        offer = session.get(Offer, topic.linked_offer_id)
        if offer:
            creator = session.get(User, offer.creator_id)
            return LinkedItemInfo(
                id=offer.id,
                type="offer",
                title=offer.title,
                creator_id=offer.creator_id,
                creator_username=creator.username if creator else None
            )
    elif topic.linked_need_id:
        need = session.get(Need, topic.linked_need_id)
        if need:
            creator = session.get(User, need.creator_id)
            return LinkedItemInfo(
                id=need.id,
                type="need",
                title=need.title,
                creator_id=need.creator_id,
                creator_username=creator.username if creator else None
            )
    return None


def build_topic_response(session: Session, topic: ForumTopic) -> ForumTopicResponse:
    """Build a ForumTopicResponse with tags and linked items."""
    tags = get_topic_tags(session, topic.id)
    creator = session.get(User, topic.creator_id)
    linked_item = get_linked_item_info(session, topic)
    
    return ForumTopicResponse(
        id=topic.id,
        topic_type=topic.topic_type.value,
        creator_id=topic.creator_id,
        creator_username=creator.username if creator else None,
        creator_display_name=creator.full_name if creator else None,
        creator_profile_image=creator.profile_image if creator else None,
        creator_profile_image_type=creator.profile_image_type if creator else None,
        title=topic.title,
        content=topic.content,
        tags=tags,
        event_start_time=topic.event_start_time,
        event_end_time=topic.event_end_time,
        event_location=topic.event_location,
        linked_offer_id=topic.linked_offer_id,
        linked_need_id=topic.linked_need_id,
        linked_item=linked_item,
        is_approved=topic.is_approved,
        is_visible=topic.is_visible,
        is_pinned=topic.is_pinned,
        view_count=topic.view_count,
        comment_count=topic.comment_count,
        created_at=topic.created_at,
        updated_at=topic.updated_at,
    )


def build_comment_response(session: Session, comment: ForumComment) -> ForumCommentResponse:
    """Build a ForumCommentResponse with author info."""
    author = session.get(User, comment.author_id)
    
    return ForumCommentResponse(
        id=comment.id,
        topic_id=comment.topic_id,
        author_id=comment.author_id,
        author_username=author.username if author else None,
        author_display_name=author.full_name if author else None,
        author_profile_image=author.profile_image if author else None,
        author_profile_image_type=author.profile_image_type if author else None,
        content=comment.content,
        is_approved=comment.is_approved,
        is_visible=comment.is_visible,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
    )


@router.post("/topics", response_model=ForumTopicResponse, status_code=status.HTTP_201_CREATED)
def create_topic(
    topic_data: ForumTopicCreate,
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
) -> ForumTopicResponse:
    """
    Create a new forum topic (discussion or event).
    
    SRS FR-15.1: Create topics of type discussion or event
    SRS FR-15.3: Link optional Offer/Need to events
    """
    # Verify linked offer/need exists if provided
    if topic_data.linked_offer_id:
        offer = session.get(Offer, topic_data.linked_offer_id)
        if not offer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Linked offer not found"
            )
    
    if topic_data.linked_need_id:
        need = session.get(Need, topic_data.linked_need_id)
        if not need:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Linked need not found"
            )
    
    # Create topic
    topic = ForumTopic(
        topic_type=TopicType(topic_data.topic_type),
        creator_id=current_user.id,
        title=topic_data.title,
        content=topic_data.content,
        event_start_time=topic_data.event_start_time,
        event_end_time=topic_data.event_end_time,
        event_location=topic_data.event_location,
        linked_offer_id=topic_data.linked_offer_id,
        linked_need_id=topic_data.linked_need_id,
    )
    
    session.add(topic)
    session.commit()
    session.refresh(topic)
    
    # Associate tags
    if topic_data.tags:
        associate_tags_to_topic(session, topic.id, topic_data.tags)
        session.commit()
    
    return build_topic_response(session, topic)


@router.get("/topics", response_model=ForumTopicListResponse)
def list_topics(
    session: Annotated[Session, Depends(get_session)],
    topic_type: Optional[str] = Query(None, description="Filter by topic type: discussion or event"),
    tags: Optional[str] = Query(None, description="Comma-separated tags to filter by"),
    keyword: Optional[str] = Query(None, description="Search keyword in title or content"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> ForumTopicListResponse:
    """
    List forum topics with optional filtering.
    
    SRS FR-15.2: Search by tag/keyword
    SRS FR-15.4: Events ordered by recency
    """
    # Base query - only visible topics
    query = select(ForumTopic).where(ForumTopic.is_visible == True)
    
    # Filter by topic type
    if topic_type:
        if topic_type not in ['discussion', 'event']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="topic_type must be 'discussion' or 'event'"
            )
        query = query.where(ForumTopic.topic_type == TopicType(topic_type))
    
    # Filter by keyword (FR-15.2)
    if keyword:
        keyword_filter = f"%{keyword.lower()}%"
        query = query.where(
            or_(
                func.lower(ForumTopic.title).like(keyword_filter),
                func.lower(ForumTopic.content).like(keyword_filter)
            )
        )
    
    # Filter by tags (FR-15.2)
    if tags:
        tag_list = [t.strip().lower() for t in tags.split(",") if t.strip()]
        if tag_list:
            # Find topics with any of the specified tags
            tag_subquery = (
                select(ForumTopicTag.topic_id)
                .join(Tag, Tag.id == ForumTopicTag.tag_id)
                .where(Tag.name.in_(tag_list))
            )
            query = query.where(ForumTopic.id.in_(tag_subquery))
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = session.exec(count_query).one()
    
    # Order by recency (FR-15.4), pinned topics first
    query = query.order_by(
        ForumTopic.is_pinned.desc(),
        ForumTopic.created_at.desc()
    )
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    # Execute query
    topics = session.exec(query).all()
    
    # Build responses
    items = [build_topic_response(session, topic) for topic in topics]
    
    return ForumTopicListResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/topics/{topic_id}", response_model=ForumTopicResponse)
def get_topic(
    topic_id: int,
    session: Annotated[Session, Depends(get_session)],
) -> ForumTopicResponse:
    """
    Get a specific forum topic by ID.
    """
    topic = session.get(ForumTopic, topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    
    if not topic.is_visible:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    
    # Increment view count
    topic.view_count += 1
    session.add(topic)
    session.commit()
    session.refresh(topic)
    
    return build_topic_response(session, topic)


@router.patch("/topics/{topic_id}", response_model=ForumTopicResponse)
def update_topic(
    topic_id: int,
    topic_data: ForumTopicUpdate,
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
) -> ForumTopicResponse:
    """
    Update a forum topic. Only the creator can update.
    """
    topic = session.get(ForumTopic, topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    
    # Only creator can update
    if topic.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the topic creator can update it"
        )
    
    # Update fields
    if topic_data.title is not None:
        topic.title = topic_data.title
    if topic_data.content is not None:
        topic.content = topic_data.content
    if topic_data.event_start_time is not None:
        topic.event_start_time = topic_data.event_start_time
    if topic_data.event_end_time is not None:
        topic.event_end_time = topic_data.event_end_time
    if topic_data.event_location is not None:
        topic.event_location = topic_data.event_location
    
    # Update tags if provided
    if topic_data.tags is not None:
        # Remove existing tags
        existing_topic_tags = session.exec(
            select(ForumTopicTag).where(ForumTopicTag.topic_id == topic_id)
        ).all()
        for topic_tag in existing_topic_tags:
            session.delete(topic_tag)
        
        # Add new tags
        associate_tags_to_topic(session, topic_id, topic_data.tags)
    
    from datetime import datetime
    topic.updated_at = datetime.utcnow()
    
    session.add(topic)
    session.commit()
    session.refresh(topic)
    
    return build_topic_response(session, topic)


@router.delete("/topics/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_topic(
    topic_id: int,
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
) -> None:
    """
    Delete a forum topic. Only the creator can delete.
    """
    topic = session.get(ForumTopic, topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    
    # Only creator can delete
    if topic.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the topic creator can delete it"
        )
    
    # Soft delete - just hide it
    topic.is_visible = False
    session.add(topic)
    session.commit()


# Comment endpoints

@router.post("/topics/{topic_id}/comments", response_model=ForumCommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    topic_id: int,
    comment_data: ForumCommentCreate,
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
) -> ForumCommentResponse:
    """
    Create a comment on a forum topic.
    
    SRS FR-15: Comments with moderation hooks
    """
    # Verify topic exists and is visible
    topic = session.get(ForumTopic, topic_id)
    if not topic or not topic.is_visible:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    
    # Create comment
    comment = ForumComment(
        topic_id=topic_id,
        author_id=current_user.id,
        content=comment_data.content,
    )
    
    session.add(comment)
    
    # Increment topic comment count
    topic.comment_count += 1
    session.add(topic)
    
    session.commit()
    session.refresh(comment)
    
    return build_comment_response(session, comment)


@router.get("/topics/{topic_id}/comments", response_model=ForumCommentListResponse)
def list_comments(
    topic_id: int,
    session: Annotated[Session, Depends(get_session)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> ForumCommentListResponse:
    """
    List comments for a forum topic.
    """
    # Verify topic exists and is visible
    topic = session.get(ForumTopic, topic_id)
    if not topic or not topic.is_visible:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    
    # Query visible comments
    query = select(ForumComment).where(
        ForumComment.topic_id == topic_id,
        ForumComment.is_visible == True
    )
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = session.exec(count_query).one()
    
    # Order by creation time (oldest first)
    query = query.order_by(ForumComment.created_at.asc())
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    # Execute query
    comments = session.exec(query).all()
    
    # Build responses
    items = [build_comment_response(session, comment) for comment in comments]
    
    return ForumCommentListResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.patch("/comments/{comment_id}", response_model=ForumCommentResponse)
def update_comment(
    comment_id: int,
    comment_data: ForumCommentUpdate,
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
) -> ForumCommentResponse:
    """
    Update a forum comment. Only the author can update.
    """
    comment = session.get(ForumComment, comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    # Only author can update
    if comment.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the comment author can update it"
        )
    
    # Update content
    comment.content = comment_data.content
    
    from datetime import datetime
    comment.updated_at = datetime.utcnow()
    
    session.add(comment)
    session.commit()
    session.refresh(comment)
    
    return build_comment_response(session, comment)


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: int,
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
) -> None:
    """
    Delete a forum comment. Only the author can delete.
    """
    comment = session.get(ForumComment, comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    # Only author can delete
    if comment.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the comment author can delete it"
        )
    
    # Get topic to decrement comment count
    topic = session.get(ForumTopic, comment.topic_id)
    if topic:
        topic.comment_count = max(0, topic.comment_count - 1)
        session.add(topic)
    
    # Soft delete - just hide it
    comment.is_visible = False
    session.add(comment)
    session.commit()


@router.get("/topics/{topic_id}/linked-from", response_model=ForumTopicListResponse)
def get_topics_linking_to_item(
    topic_id: int,
    session: Annotated[Session, Depends(get_session)],
    item_type: str = Query(..., description="Type of item: 'offer' or 'need'"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> ForumTopicListResponse:
    """
    Get forum topics that link to a specific offer or need.
    
    SRS FR-15.5: Links visible both ways (bidirectional)
    
    This allows viewing which forum discussions/events reference a specific offer/need.
    """
    if item_type not in ['offer', 'need']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="item_type must be 'offer' or 'need'"
        )
    
    # Build query based on item type
    if item_type == 'offer':
        query = select(ForumTopic).where(
            ForumTopic.linked_offer_id == topic_id,
            ForumTopic.is_visible == True
        )
    else:  # need
        query = select(ForumTopic).where(
            ForumTopic.linked_need_id == topic_id,
            ForumTopic.is_visible == True
        )
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = session.exec(count_query).one()
    
    # Order by recency
    query = query.order_by(ForumTopic.created_at.desc())
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    # Execute query
    topics = session.exec(query).all()
    
    # Build responses
    items = [build_topic_response(session, topic) for topic in topics]
    
    return ForumTopicListResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit,
    )
