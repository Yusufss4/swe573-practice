"""
Schemas for rating operations.

SRS Requirements:
- FR-10.4: Multi-category rating system
- FR-10.5: Blind ratings with visibility control

Design Philosophy:
- Peace-oriented, calm, community-focused language
- Human-friendly labels for rating values
- Encourages constructive feedback
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


# ===== Human-Friendly Rating Labels =====
# These labels encourage positive framing even for lower ratings

RATING_LABELS = {
    1: "Needs Improvement",
    2: "Below Expectations",
    3: "Met Expectations",
    4: "Above Expectations",
    5: "Exceptional",
}

# Category descriptions for UI display
CATEGORY_INFO = {
    "reliability": {
        "name": "Reliability & Commitment",
        "description": "Did they show up as agreed, communicate clearly, and follow through on commitments?",
        "icon": "schedule",
        "required": True,
    },
    "kindness": {
        "name": "Kindness & Respect",
        "description": "Was the interaction warm, respectful, and comfortable?",
        "icon": "favorite",
        "required": True,
    },
    "helpfulness": {
        "name": "Helpfulness & Support",
        "description": "Did the exchange feel meaningful and genuinely supportive?",
        "icon": "support",
        "required": True,
    },
}


def get_rating_label(value: int) -> str:
    """Get human-friendly label for a rating value."""
    return RATING_LABELS.get(value, "Unknown")


class RatingCreate(BaseModel):
    """
    Schema for creating a new rating.
    
    The rating system is designed to be constructive and community-oriented:
    - All three category ratings are required (1-5)
    - General rating is calculated as the average of the three categories
    - Public comment is optional and should be constructive
    """
    
    # Target of the rating
    recipient_id: int = Field(..., description="User receiving the rating")
    participant_id: int = Field(..., description="Completed exchange/participant record")
    
    # Required: All three category ratings (1-5 each)
    # General rating will be calculated as average of these
    reliability_rating: int = Field(
        ...,
        ge=1,
        le=5,
        description="Reliability & Commitment: punctuality, communication, follow-through (Required)"
    )
    
    kindness_rating: int = Field(
        ...,
        ge=1,
        le=5,
        description="Kindness & Respect: warmth, comfort, mutual respect (Required)"
    )
    
    helpfulness_rating: int = Field(
        ...,
        ge=1,
        le=5,
        description="Helpfulness & Support: meaningfulness, supportiveness (Required)"
    )
    
    # Optional: Public Comment (shown on profile)
    public_comment: Optional[str] = Field(
        None,
        max_length=1000,
        description="Optional public comment (visible on recipient's profile)"
    )
    
    @field_validator('public_comment')
    @classmethod
    def validate_comment(cls, v: Optional[str]) -> Optional[str]:
        """Validate and clean public comment."""
        if v is None:
            return None
        
        v = v.strip()
        if not v:
            return None
        
        # Minimum length for meaningful comments
        if len(v) < 10:
            raise ValueError("Comment must be at least 10 characters if provided")
        
        return v


class RatingResponse(BaseModel):
    """
    Schema for rating response.
    
    Includes human-friendly labels and visibility information.
    """
    id: int
    from_user_id: int
    from_username: Optional[str] = None
    to_user_id: int
    to_username: Optional[str] = None
    participant_id: int
    
    # Rating values with labels
    general_rating: int
    general_rating_label: str = ""
    
    reliability_rating: int
    reliability_rating_label: str = ""
    
    kindness_rating: int
    kindness_rating_label: str = ""
    
    helpfulness_rating: int
    helpfulness_rating_label: str = ""
    
    # Calculated average
    average_rating: float
    
    # Public comment
    public_comment: Optional[str] = None
    comment_is_approved: bool = True
    
    # Visibility status
    visibility: str
    is_visible: bool
    visibility_deadline: datetime
    
    # Timestamps
    created_at: datetime
    
    model_config = {"from_attributes": True}
    
    @classmethod
    def from_rating(cls, rating, from_username: str = None, to_username: str = None, is_visible: bool = False):
        """Create response from Rating model with labels."""
        return cls(
            id=rating.id,
            from_user_id=rating.from_user_id,
            from_username=from_username,
            to_user_id=rating.to_user_id,
            to_username=to_username,
            participant_id=rating.participant_id,
            general_rating=rating.general_rating,
            general_rating_label=get_rating_label(rating.general_rating),
            reliability_rating=rating.reliability_rating,
            reliability_rating_label=get_rating_label(rating.reliability_rating),
            kindness_rating=rating.kindness_rating,
            kindness_rating_label=get_rating_label(rating.kindness_rating),
            helpfulness_rating=rating.helpfulness_rating,
            helpfulness_rating_label=get_rating_label(rating.helpfulness_rating),
            average_rating=rating.calculate_average(),
            public_comment=rating.public_comment if is_visible and rating.comment_is_approved else None,
            comment_is_approved=rating.comment_is_approved,
            visibility=rating.visibility.value,
            is_visible=is_visible,
            visibility_deadline=rating.visibility_deadline,
            created_at=rating.created_at,
        )


class RatingListResponse(BaseModel):
    """Schema for paginated rating list."""
    items: list[RatingResponse]
    total: int
    skip: int
    limit: int


class RatingCategoryLabelsResponse(BaseModel):
    """
    Schema returning all category information and rating labels.
    Used by frontend to display rating UI with proper labels.
    """
    rating_labels: dict[int, str] = RATING_LABELS
    categories: dict = CATEGORY_INFO


class RatingStatusResponse(BaseModel):
    """
    Schema for checking rating status between two users for an exchange.
    
    Helps frontend determine if user can/should rate and current visibility state.
    """
    participant_id: int
    can_submit_rating: bool
    has_submitted_rating: bool
    other_party_has_rated: bool
    both_have_rated: bool
    is_visible: bool
    visibility_deadline: Optional[datetime] = None
    days_until_visible: Optional[int] = None
    message: str  # Human-friendly status message


class UserRatingSummary(BaseModel):
    """
    Aggregated rating summary for a user's profile.
    
    Shows average scores across all categories from visible ratings.
    """
    user_id: int
    total_ratings: int
    
    # Average scores (only from visible ratings)
    average_general: Optional[float] = None
    average_reliability: Optional[float] = None
    average_kindness: Optional[float] = None
    average_helpfulness: Optional[float] = None
    overall_average: Optional[float] = None
    
    # Distribution of general ratings (for display)
    rating_distribution: dict[int, int] = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}


class BlindRatingExplanation(BaseModel):
    """
    Explanation of the blind rating system for users.
    
    Displayed in UI to help users understand how ratings work.
    """
    title: str = "How Ratings Work"
    explanation: str = (
        "To encourage honest and thoughtful feedback, ratings remain private "
        "until both parties have submitted their reviews, or until 7 days have passed. "
        "This helps ensure authentic reflections on your exchange experience."
    )
    benefits: list[str] = [
        "Encourages honest, unbiased feedback",
        "Both parties can share their true experience",
        "Builds trust within our community",
    ]
