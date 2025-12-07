"""
Notification creation helpers.
# SRS FR-N.8: Helper functions for creating notifications
"""
from typing import Optional
from sqlmodel import Session

from app.models.notification import Notification, NotificationType
from app.schemas.notification import NotificationResponse
from app.core.websocket import manager
import asyncio
import logging

logger = logging.getLogger(__name__)


def create_notification(
    session: Session,
    user_id: int,
    notification_type: NotificationType,
    title: str,
    message: str,
    related_offer_id: Optional[int] = None,
    related_need_id: Optional[int] = None,
    related_user_id: Optional[int] = None,
    related_participant_id: Optional[int] = None,
    related_rating_id: Optional[int] = None,
) -> Notification:
    """
    Create a notification and send it via WebSocket if user is connected.
    # SRS FR-N.9: Persist notification and deliver via WebSocket
    """
    notification = Notification(
        user_id=user_id,
        type=notification_type,
        title=title,
        message=message,
        related_offer_id=related_offer_id,
        related_need_id=related_need_id,
        related_user_id=related_user_id,
        related_participant_id=related_participant_id,
        related_rating_id=related_rating_id,
    )
    
    session.add(notification)
    session.commit()
    session.refresh(notification)
    
    # Send via WebSocket (async)
    try:
        notification_data = NotificationResponse.model_validate(notification).model_dump(mode='json')
        # Run async send in event loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(manager.send_notification(user_id, notification_data))
        else:
            asyncio.run(manager.send_notification(user_id, notification_data))
    except Exception as e:
        logger.error(f"Error sending WebSocket notification: {e}")
    
    return notification


def notify_application_received(
    session: Session,
    offer_creator_id: int,
    applicant_username: str,
    offer_title: str,
    offer_id: int,
    participant_id: int,
):
    """
    Notify offer/need creator that someone applied.
    # SRS FR-N.10: Application received notification
    """
    create_notification(
        session=session,
        user_id=offer_creator_id,
        notification_type=NotificationType.APPLICATION_RECEIVED,
        title="New Application",
        message=f"{applicant_username} applied to: {offer_title}",
        related_offer_id=offer_id,
        related_participant_id=participant_id,
    )


def notify_application_accepted(
    session: Session,
    applicant_id: int,
    offer_title: str,
    offer_id: int,
    participant_id: int,
):
    """
    Notify applicant that their application was accepted.
    # SRS FR-N.11: Application accepted notification
    """
    create_notification(
        session=session,
        user_id=applicant_id,
        notification_type=NotificationType.APPLICATION_ACCEPTED,
        title="Application Accepted",
        message=f"Your application to '{offer_title}' was accepted!",
        related_offer_id=offer_id,
        related_participant_id=participant_id,
    )


def notify_application_declined(
    session: Session,
    applicant_id: int,
    offer_title: str,
    offer_id: int,
    participant_id: int,
):
    """
    Notify applicant that their application was declined.
    # SRS FR-N.12: Application declined notification
    """
    create_notification(
        session=session,
        user_id=applicant_id,
        notification_type=NotificationType.APPLICATION_DECLINED,
        title="Application Declined",
        message=f"Your application to '{offer_title}' was declined",
        related_offer_id=offer_id,
        related_participant_id=participant_id,
    )


def notify_participant_cancelled(
    session: Session,
    other_party_id: int,
    cancelled_by_username: str,
    offer_title: str,
    offer_id: int,
    participant_id: int,
):
    """
    Notify other party that participant cancelled.
    # SRS FR-N.13: Participant cancelled notification
    """
    create_notification(
        session=session,
        user_id=other_party_id,
        notification_type=NotificationType.PARTICIPANT_CANCELLED,
        title="Participant Cancelled",
        message=f"{cancelled_by_username} cancelled their participation in '{offer_title}'",
        related_offer_id=offer_id,
        related_participant_id=participant_id,
    )


def notify_exchange_completed(
    session: Session,
    user_id: int,
    other_party_username: str,
    offer_title: str,
    offer_id: int,
    participant_id: int,
):
    """
    Notify user that exchange was completed.
    # SRS FR-N.14: Exchange completed notification
    """
    create_notification(
        session=session,
        user_id=user_id,
        notification_type=NotificationType.EXCHANGE_COMPLETED,
        title="Exchange Completed",
        message=f"Your exchange '{offer_title}' with {other_party_username} is completed",
        related_offer_id=offer_id,
        related_participant_id=participant_id,
    )


def notify_exchange_awaiting_confirmation(
    session: Session,
    user_id: int,
    other_party_username: str,
    offer_title: str,
    offer_id: int,
    participant_id: int,
):
    """
    Notify user that other party confirmed and waiting for their confirmation.
    # SRS FR-N.16: Exchange awaiting confirmation notification
    """
    create_notification(
        session=session,
        user_id=user_id,
        notification_type=NotificationType.EXCHANGE_AWAITING_CONFIRMATION,
        title="Confirmation Needed",
        message=f"{other_party_username} confirmed '{offer_title}'. Please confirm to complete the exchange.",
        related_offer_id=offer_id,
        related_participant_id=participant_id,
    )


def notify_rating_received(
    session: Session,
    rated_user_id: int,
    rater_username: str,
    rating_value: float,
    rating_id: int,
):
    """
    Notify user that they received a rating.
    # SRS FR-N.15: Rating received notification
    """
    create_notification(
        session=session,
        user_id=rated_user_id,
        notification_type=NotificationType.RATING_RECEIVED,
        title="New Rating",
        message=f"{rater_username} rated you {rating_value:.1f} stars",
        related_rating_id=rating_id,
    )
