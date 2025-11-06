from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Comment(SQLModel, table=True):
    """Comment/feedback left on user profiles after exchange completion.
    
    SRS Requirements:
    - FR-10.1: Participants may leave comments after completing exchange
    - FR-10.2: Comments pass through automated text moderation
    - FR-10.3: Comments publicly visible on profiles
    - Database schema requirement (§3.5.1)
    """

    __tablename__ = "comments"

    id: Optional[int] = Field(default=None, primary_key=True)
    
    # From user (commenter) and to user (profile owner)
    from_user_id: int = Field(foreign_key="users.id", index=True)
    to_user_id: int = Field(foreign_key="users.id", index=True)
    
    # Comment content
    content: str = Field(max_length=1000)
    
    # Reference to the exchange this comment is about
    participant_id: Optional[int] = Field(default=None, foreign_key="participants.id")
    
    # Moderation status (FR-10.2)
    is_moderated: bool = Field(default=False)
    is_approved: bool = Field(default=True)  # Auto-approved unless flagged
    moderation_reason: Optional[str] = Field(default=None, max_length=500)
    
    # Visibility (FR-10.3)
    is_visible: bool = Field(default=True)
    
    # Timestamps
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    moderated_at: Optional[datetime] = Field(default=None)
