"""
Rating model for community feedback after completed exchanges.

SRS Requirements:
- FR-10: Participants may leave feedback after completing exchange
- FR-10.4: Multi-category rating system (general, reliability, kindness, helpfulness)
- FR-10.5: Blind ratings - visible only after both submit or deadline passes

Design Philosophy:
- Peace-oriented, community-focused language
- Encourages constructive, positive feedback
- All category ratings except general are optional
"""
from datetime import datetime, timedelta
from typing import Optional
from enum import Enum

from sqlmodel import Field, SQLModel


# Default deadline for blind ratings (7 days after exchange completion)
RATING_VISIBILITY_DEADLINE_DAYS = 7


class RatingVisibility(str, Enum):
    """Rating visibility status for blind rating system."""
    HIDDEN = "hidden"  # Waiting for other party or deadline
    VISIBLE = "visible"  # Both submitted or deadline passed


class Rating(SQLModel, table=True):
    """
    Rating/feedback left after exchange completion.
    
    Implements blind rating system where ratings become visible only when:
    1. Both parties have submitted their ratings, OR
    2. The visibility deadline has passed
    
    Rating Categories (1-5 scale) - ALL REQUIRED:
    - Reliability & Commitment: Punctuality, follow-through, communication
    - Kindness & Respect: Politeness, comfort, mutual respect
    - Helpfulness & Quality: Meaningfulness and supportiveness
    
    General Rating is calculated as the average of the three category ratings.
    
    Human-friendly labels for each score:
    1 = "Needs Improvement" (gentle framing)
    2 = "Below Expectations"
    3 = "Met Expectations"
    4 = "Above Expectations"
    5 = "Exceptional"
    """

    __tablename__ = "ratings"

    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Users involved in the rating
    from_user_id: int = Field(foreign_key="users.id", index=True)  # Who is giving the rating
    to_user_id: int = Field(foreign_key="users.id", index=True)    # Who is receiving the rating
    
    # Reference to the completed exchange
    participant_id: int = Field(foreign_key="participants.id", index=True)
    
    # ===== Rating Categories (1-5 scale) - ALL REQUIRED =====
    
    # Reliability & Commitment (REQUIRED)
    # Did they show up on time, follow through, communicate clearly?
    reliability_rating: int = Field(ge=1, le=5)
    
    # Kindness & Respect (REQUIRED)
    # Was the interaction polite, comfortable, and respectful?
    kindness_rating: int = Field(ge=1, le=5)
    
    # Helpfulness & Quality of Support (REQUIRED)
    # Did the exchange feel meaningful and supportive?
    helpfulness_rating: int = Field(ge=1, le=5)
    
    # General Rating - Calculated as average of the three categories
    # Stored for query performance and historical consistency
    general_rating: int = Field(ge=1, le=5)
    
    # ===== Public Comment (Optional) =====
    # Shown on profile - should be constructive and peace-oriented
    public_comment: Optional[str] = Field(default=None, max_length=1000)
    
    # Moderation for public comment
    comment_is_moderated: bool = Field(default=False)
    comment_is_approved: bool = Field(default=True)  # Auto-approved unless flagged
    moderation_reason: Optional[str] = Field(default=None, max_length=500)
    
    # ===== Blind Rating System =====
    # Ratings are hidden until both parties submit or deadline passes
    visibility: RatingVisibility = Field(default=RatingVisibility.HIDDEN, index=True)
    visibility_deadline: datetime = Field(
        default_factory=lambda: datetime.utcnow() + timedelta(days=RATING_VISIBILITY_DEADLINE_DAYS)
    )
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    made_visible_at: Optional[datetime] = Field(default=None)  # When rating became visible

    def calculate_average(self) -> float:
        """Calculate average rating from the three category ratings."""
        return (self.reliability_rating + self.kindness_rating + self.helpfulness_rating) / 3
    
    @staticmethod
    def compute_general_rating(reliability: int, kindness: int, helpfulness: int) -> int:
        """Compute the general rating as rounded average of the three categories."""
        avg = (reliability + kindness + helpfulness) / 3
        return round(avg)

    def is_past_deadline(self) -> bool:
        """Check if the visibility deadline has passed."""
        return datetime.utcnow() >= self.visibility_deadline

    def should_be_visible(self, other_rating_exists: bool) -> bool:
        """
        Determine if this rating should be visible.
        
        Args:
            other_rating_exists: Whether the other party has submitted their rating
            
        Returns:
            True if rating should be visible (both submitted or deadline passed)
        """
        return other_rating_exists or self.is_past_deadline()
