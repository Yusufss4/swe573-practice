"""
Reports API for content moderation.

SRS Requirements:
- FR-11.1: Users can report inappropriate content or behavior
- FR-11.2: Moderators review reports and take action
- FR-11.4: Reports and resolutions are logged
"""
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status
from sqlmodel import Session, select, func

from app.core.auth import CurrentUser, ModeratorUser
from app.core.db import SessionDep
from app.models.report import Report, ReportStatus, ReportReason, ReportAction
from app.models.user import User
from app.models.offer import Offer
from app.models.need import Need
from app.models.forum import ForumComment, ForumTopic
from app.schemas.report import (
    ReportCreate,
    ReportUpdate,
    ReportResponse,
    ReportListResponse,
    ReportStatsResponse,
    ReportedItemDetails,
    ReporterInfo,
    ModeratorInfo,
)


router = APIRouter(prefix="/reports", tags=["reports"])


def _build_report_response(session: Session, report: Report) -> ReportResponse:
    """Build a full report response with related data."""
    
    # Get reporter info
    reporter = session.get(User, report.reporter_id)
    if not reporter:
        raise HTTPException(status_code=404, detail="Reporter not found")
    
    reporter_info = ReporterInfo(
        id=reporter.id,
        username=reporter.username,
        full_name=reporter.full_name,
    )
    
    # Get reported item details
    reported_item = None
    
    if report.reported_user_id:
        user = session.get(User, report.reported_user_id)
        if user:
            reported_item = ReportedItemDetails(
                type="user",
                id=user.id,
                title=user.username,
                content=user.bio,
                creator_username=user.username,
            )
    
    elif report.reported_offer_id:
        offer = session.get(Offer, report.reported_offer_id)
        if offer:
            creator = session.get(User, offer.creator_id)
            reported_item = ReportedItemDetails(
                type="offer",
                id=offer.id,
                title=offer.title,
                content=offer.description,
                creator_username=creator.username if creator else None,
            )
    
    elif report.reported_need_id:
        need = session.get(Need, report.reported_need_id)
        if need:
            creator = session.get(User, need.creator_id)
            reported_item = ReportedItemDetails(
                type="need",
                id=need.id,
                title=need.title,
                content=need.description,
                creator_username=creator.username if creator else None,
            )
    
    elif report.reported_comment_id:
        comment = session.get(ForumComment, report.reported_comment_id)
        if comment:
            creator = session.get(User, comment.author_id)
            reported_item = ReportedItemDetails(
                type="comment",
                id=comment.id,
                title=f"Comment on topic {comment.topic_id}",
                content=comment.content,
                creator_username=creator.username if creator else None,
            )
    
    elif report.reported_forum_topic_id:
        topic = session.get(ForumTopic, report.reported_forum_topic_id)
        if topic:
            creator = session.get(User, topic.creator_id)
            reported_item = ReportedItemDetails(
                type="forum_topic",
                id=topic.id,
                title=topic.title,
                content=topic.content[:200] if topic.content else None,
                creator_username=creator.username if creator else None,
            )
    
    if not reported_item:
        reported_item = ReportedItemDetails(
            type="unknown",
            id=0,
            title="Content no longer available",
            content=None,
            creator_username=None,
        )
    
    # Get moderator info if reviewed
    moderator_info = None
    if report.moderator_id:
        moderator = session.get(User, report.moderator_id)
        if moderator:
            moderator_info = ModeratorInfo(
                id=moderator.id,
                username=moderator.username,
                full_name=moderator.full_name,
            )
    
    return ReportResponse(
        id=report.id,
        reporter=reporter_info,
        reported_item=reported_item,
        reason=report.reason,
        description=report.description,
        status=report.status,
        moderator=moderator_info,
        moderator_action=report.moderator_action,
        moderator_notes=report.moderator_notes,
        created_at=report.created_at,
        reviewed_at=report.reviewed_at,
        resolved_at=report.resolved_at,
    )


@router.post("/", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def create_report(
    report_data: ReportCreate,
    current_user: CurrentUser,
    session: SessionDep,
) -> ReportResponse:
    """
    Create a new report.
    
    SRS FR-11.1: Users can report inappropriate content or behavior
    
    Users can report:
    - Other users (profiles)
    - Offers
    - Needs
    - Forum comments
    """
    # Validate that exactly one reported item is provided
    reported_items = [
        report_data.reported_user_id,
        report_data.reported_offer_id,
        report_data.reported_need_id,
        report_data.reported_comment_id,
        report_data.reported_forum_topic_id,
    ]
    
    if sum(x is not None for x in reported_items) != 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Exactly one reported item must be specified"
        )
    
    # Prevent self-reporting
    if report_data.reported_user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot report yourself"
        )
    
    # Verify reported item exists
    if report_data.reported_user_id:
        user = session.get(User, report_data.reported_user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
    
    elif report_data.reported_offer_id:
        offer = session.get(Offer, report_data.reported_offer_id)
        if not offer:
            raise HTTPException(status_code=404, detail="Offer not found")
    
    elif report_data.reported_need_id:
        need = session.get(Need, report_data.reported_need_id)
        if not need:
            raise HTTPException(status_code=404, detail="Need not found")
    
    elif report_data.reported_comment_id:
        comment = session.get(ForumComment, report_data.reported_comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
    
    elif report_data.reported_forum_topic_id:
        topic = session.get(ForumTopic, report_data.reported_forum_topic_id)
        if not topic:
            raise HTTPException(status_code=404, detail="Forum topic not found")
    
    # Create report
    report = Report(
        reporter_id=current_user.id,
        reported_user_id=report_data.reported_user_id,
        reported_offer_id=report_data.reported_offer_id,
        reported_need_id=report_data.reported_need_id,
        reported_comment_id=report_data.reported_comment_id,
        reported_forum_topic_id=report_data.reported_forum_topic_id,
        reason=report_data.reason,
        description=report_data.description,
    )
    
    session.add(report)
    session.commit()
    session.refresh(report)
    
    return _build_report_response(session, report)


@router.get("/", response_model=ReportListResponse)
def list_reports(
    moderator: ModeratorUser,
    session: SessionDep,
    status_filter: ReportStatus | None = Query(None, description="Filter by status"),
    reason_filter: ReportReason | None = Query(None, description="Filter by reason"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> ReportListResponse:
    """
    List all reports (moderators only).
    
    SRS FR-11.2: Moderators can view and review reports
    """
    # Build query
    query = select(Report).order_by(Report.created_at.desc())
    
    if status_filter:
        query = query.where(Report.status == status_filter)
    
    if reason_filter:
        query = query.where(Report.reason == reason_filter)
    
    # Get total count
    count_query = select(func.count()).select_from(Report)
    if status_filter:
        count_query = count_query.where(Report.status == status_filter)
    if reason_filter:
        count_query = count_query.where(Report.reason == reason_filter)
    
    total = session.exec(count_query).one()
    
    # Get paginated results
    query = query.offset(skip).limit(limit)
    reports = session.exec(query).all()
    
    # Get status counts
    pending_count = session.exec(
        select(func.count()).select_from(Report).where(Report.status == ReportStatus.PENDING)
    ).one()
    
    under_review_count = session.exec(
        select(func.count()).select_from(Report).where(Report.status == ReportStatus.UNDER_REVIEW)
    ).one()
    
    resolved_count = session.exec(
        select(func.count()).select_from(Report).where(Report.status == ReportStatus.RESOLVED)
    ).one()
    
    # Build responses
    report_responses = [_build_report_response(session, report) for report in reports]
    
    return ReportListResponse(
        reports=report_responses,
        total=total,
        pending_count=pending_count,
        under_review_count=under_review_count,
        resolved_count=resolved_count,
        page=skip // limit + 1,
        page_size=limit,
    )


@router.get("/stats", response_model=ReportStatsResponse)
def get_report_stats(
    moderator: ModeratorUser,
    session: SessionDep,
) -> ReportStatsResponse:
    """
    Get report statistics for moderator dashboard.
    
    SRS FR-11.2: Moderators can monitor reporting activity
    """
    # Status counts
    total = session.exec(select(func.count()).select_from(Report)).one()
    pending = session.exec(select(func.count()).select_from(Report).where(Report.status == ReportStatus.PENDING)).one()
    under_review = session.exec(select(func.count()).select_from(Report).where(Report.status == ReportStatus.UNDER_REVIEW)).one()
    resolved = session.exec(select(func.count()).select_from(Report).where(Report.status == ReportStatus.RESOLVED)).one()
    dismissed = session.exec(select(func.count()).select_from(Report).where(Report.status == ReportStatus.DISMISSED)).one()
    
    # Type counts
    user_reports = session.exec(select(func.count()).select_from(Report).where(Report.reported_user_id.is_not(None))).one()
    offer_reports = session.exec(select(func.count()).select_from(Report).where(Report.reported_offer_id.is_not(None))).one()
    need_reports = session.exec(select(func.count()).select_from(Report).where(Report.reported_need_id.is_not(None))).one()
    comment_reports = session.exec(select(func.count()).select_from(Report).where(Report.reported_comment_id.is_not(None))).one()
    forum_topic_reports = session.exec(select(func.count()).select_from(Report).where(Report.reported_forum_topic_id.is_not(None))).one()
    
    # Reason counts
    spam = session.exec(select(func.count()).select_from(Report).where(Report.reason == ReportReason.SPAM)).one()
    harassment = session.exec(select(func.count()).select_from(Report).where(Report.reason == ReportReason.HARASSMENT)).one()
    inappropriate = session.exec(select(func.count()).select_from(Report).where(Report.reason == ReportReason.INAPPROPRIATE)).one()
    scam = session.exec(select(func.count()).select_from(Report).where(Report.reason == ReportReason.SCAM)).one()
    misinformation = session.exec(select(func.count()).select_from(Report).where(Report.reason == ReportReason.MISINFORMATION)).one()
    other = session.exec(select(func.count()).select_from(Report).where(Report.reason == ReportReason.OTHER)).one()
    
    return ReportStatsResponse(
        total_reports=total,
        pending=pending,
        under_review=under_review,
        resolved=resolved,
        dismissed=dismissed,
        user_reports=user_reports,
        offer_reports=offer_reports,
        need_reports=need_reports,
        comment_reports=comment_reports,
        forum_topic_reports=forum_topic_reports,
        spam_reports=spam,
        harassment_reports=harassment,
        inappropriate_reports=inappropriate,
        scam_reports=scam,
        misinformation_reports=misinformation,
        other_reports=other,
    )


@router.get("/{report_id}", response_model=ReportResponse)
def get_report(
    report_id: int,
    moderator: ModeratorUser,
    session: SessionDep,
) -> ReportResponse:
    """
    Get a specific report by ID (moderators only).
    
    SRS FR-11.2: Moderators can view report details
    """
    report = session.get(Report, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return _build_report_response(session, report)


@router.put("/{report_id}", response_model=ReportResponse)
def update_report(
    report_id: int,
    report_update: ReportUpdate,
    moderator: ModeratorUser,
    session: SessionDep,
) -> ReportResponse:
    """
    Update report status and take moderation action.
    
    SRS FR-11.2: Moderators review and take action on reports
    SRS FR-11.4: Report resolutions are logged with timestamps
    """
    report = session.get(Report, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Update status
    old_status = report.status
    report.status = report_update.status
    report.moderator_id = moderator.id
    report.moderator_action = report_update.moderator_action
    report.moderator_notes = report_update.moderator_notes
    
    # Update timestamps
    if old_status == ReportStatus.PENDING and report_update.status == ReportStatus.UNDER_REVIEW:
        report.reviewed_at = datetime.utcnow()
    
    if report_update.status in [ReportStatus.RESOLVED, ReportStatus.DISMISSED]:
        if not report.reviewed_at:
            report.reviewed_at = datetime.utcnow()
        report.resolved_at = datetime.utcnow()
    
    session.add(report)
    session.commit()
    session.refresh(report)
    
    return _build_report_response(session, report)


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_report(
    report_id: int,
    moderator: ModeratorUser,
    session: SessionDep,
) -> None:
    """
    Delete a report (admin/moderator only).
    
    Use with caution - only for spam reports or mistakes.
    """
    report = session.get(Report, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    session.delete(report)
    session.commit()
