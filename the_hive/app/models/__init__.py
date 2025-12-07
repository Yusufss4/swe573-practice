"""Database models for The Hive.

This module exports all SQLModel table definitions for the application.
Models are organized by domain:
- User: Authentication and profiles
- Offer/Need: Service posts
- Tag: Semantic categorization
- Participant: Handshake mechanism and exchange tracking
- Ledger/Transfer: TimeBank accounting
- Rating: User feedback after exchanges
- Report: Moderation system
"""

from app.models.user import User, UserRole
from app.models.tag import Tag
from app.models.offer import Offer, OfferStatus
from app.models.need import Need, NeedStatus
from app.models.associations import OfferTag, NeedTag
from app.models.participant import Participant, ParticipantRole, ParticipantStatus
from app.models.ledger import LedgerEntry, Transfer, TransactionType
from app.models.rating import Rating, RatingVisibility
from app.models.report import Report, ReportReason, ReportStatus, ReportAction
from app.models.forum import ForumTopic, ForumComment, ForumTopicTag, TopicType
from app.models.notification import Notification, NotificationType

__all__ = [
    # User
    "User",
    "UserRole",
    # Tags
    "Tag",
    # Offers and Needs
    "Offer",
    "OfferStatus",
    "Need",
    "NeedStatus",
    # Associations
    "OfferTag",
    "NeedTag",
    # Participants (Handshake)
    "Participant",
    "ParticipantRole",
    "ParticipantStatus",
    # TimeBank Ledger
    "LedgerEntry",
    "Transfer",
    "TransactionType",
    # Ratings
    "Rating",
    "RatingVisibility",
    # Reports
    "Report",
    "ReportReason",
    "ReportStatus",
    "ReportAction",
    # Forum
    "ForumTopic",
    "ForumComment",
    "ForumTopicTag",
    "TopicType",
    # Notifications
    "Notification",
    "NotificationType",
]


