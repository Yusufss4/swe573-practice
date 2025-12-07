"""
Notification API endpoints.
# SRS FR-N.1: REST API for notifications
# SRS FR-N.4: WebSocket endpoint for real-time delivery
"""
from typing import Annotated
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query
from sqlmodel import Session, select, func

from app.core.auth import CurrentUser, get_current_user_ws
from app.core.db import SessionDep
from app.core.websocket import manager
from app.models.notification import Notification
from app.schemas.notification import NotificationResponse, NotificationListResponse

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=NotificationListResponse)
def list_notifications(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    unread_only: bool = Query(False),
) -> NotificationListResponse:
    """
    Get notifications for current user.
    # SRS FR-N.5: List notifications with pagination and filtering
    """
    # Build query
    query = select(Notification).where(Notification.user_id == current_user.id)
    
    if unread_only:
        query = query.where(Notification.is_read == False)
    
    # Order by most recent first
    query = query.order_by(Notification.created_at.desc())
    
    # Get total count
    count_query = select(func.count()).select_from(Notification).where(
        Notification.user_id == current_user.id
    )
    if unread_only:
        count_query = count_query.where(Notification.is_read == False)
    total = session.exec(count_query).one()
    
    # Get unread count
    unread_query = select(func.count()).select_from(Notification).where(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    )
    unread_count = session.exec(unread_query).one()
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    notifications = session.exec(query).all()
    
    return NotificationListResponse(
        notifications=[NotificationResponse.model_validate(n.model_dump()) for n in notifications],
        total=total,
        unread_count=unread_count,
    )


@router.post("/{notification_id}/read", response_model=NotificationResponse)
def mark_as_read(
    notification_id: int,
    session: SessionDep,
    current_user: CurrentUser,
) -> NotificationResponse:
    """
    Mark notification as read.
    # SRS FR-N.6: Update notification read status
    """
    notification = session.get(Notification, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    # Check ownership
    if notification.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Mark as read
    if not notification.is_read:
        notification.is_read = True
        notification.read_at = datetime.utcnow()
        session.add(notification)
        session.commit()
        session.refresh(notification)
    
    return NotificationResponse.model_validate(notification.model_dump())


@router.post("/read-all")
def mark_all_as_read(
    session: SessionDep,
    current_user: CurrentUser,
) -> dict:
    """
    Mark all notifications as read for current user.
    # SRS FR-N.7: Bulk update notification status
    """
    notifications = session.exec(
        select(Notification).where(
            Notification.user_id == current_user.id,
            Notification.is_read == False
        )
    ).all()
    
    count = 0
    for notification in notifications:
        notification.is_read = True
        notification.read_at = datetime.utcnow()
        session.add(notification)
        count += 1
    
    session.commit()
    
    return {"marked_read": count}


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
):
    """
    WebSocket endpoint for real-time notifications.
    # SRS NFR-N.1: WebSocket connection with JWT authentication
    """
    # Authenticate user from token
    try:
        user = await get_current_user_ws(token)
    except Exception as e:
        await websocket.close(code=1008)  # Policy violation
        return
    
    # Connect to manager
    await manager.connect(websocket, user.id)
    
    try:
        # Keep connection alive and listen for messages (ping/pong)
        while True:
            data = await websocket.receive_text()
            # Client can send ping to keep connection alive
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(user.id)
    except Exception as e:
        manager.disconnect(user.id)
