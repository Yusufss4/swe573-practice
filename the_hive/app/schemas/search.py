"""
Search schemas for filtering offers and needs.
"""
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class SearchType(str, Enum):
    """Type of items to search for."""
    OFFER = "offer"
    NEED = "need"
    ALL = "all"


class TagMatchMode(str, Enum):
    """How to match tags in search."""
    ANY = "any"  # Match if item has ANY of the provided tags
    ALL = "all"  # Match if item has ALL of the provided tags


class SortOrder(str, Enum):
    """Sort order for search results."""
    RECENCY = "recency"  # Most recent first
    DISTANCE = "distance"  # Closest first (placeholder for now)
    RELEVANCE = "relevance"  # Most relevant first (based on tag matches)


class SearchFilters(BaseModel):
    """Search filters for offers and needs.
    
    SRS Requirements:
    - FR-8: Search and discovery with semantic tags
    - FR-8.5: Order by distance (placeholder), recency
    """
    
    # What to search
    query: Optional[str] = Field(
        None,
        description="Text search in title and description (ILIKE)"
    )
    
    # Type filter
    type: SearchType = Field(
        default=SearchType.ALL,
        description="Filter by type: offer, need, or all"
    )
    
    # Tag filters
    tags: Optional[list[str]] = Field(
        None,
        min_length=1,
        description="List of tags to filter by"
    )
    tag_match: TagMatchMode = Field(
        default=TagMatchMode.ANY,
        description="Match ANY or ALL tags"
    )
    
    # Location filters
    is_remote: Optional[bool] = Field(
        None,
        description="Filter by remote flag (true=remote only, false=in-person only, null=both)"
    )
    
    # Ordering
    sort_by: SortOrder = Field(
        default=SortOrder.RECENCY,
        description="Sort order: recency (default), distance (placeholder), relevance"
    )
    
    # Pagination
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=100)


class SearchResult(BaseModel):
    """Single search result item."""
    id: int
    type: str  # "offer" or "need"
    title: str
    description: str
    creator_id: int
    is_remote: bool
    location_name: Optional[str]
    capacity: int
    accepted_count: int
    status: str
    tags: list[str]
    created_at: str
    
    # Optional relevance score (for future use)
    relevance_score: Optional[float] = None


class SearchResponse(BaseModel):
    """Search response with results and metadata."""
    items: list[SearchResult]
    total: int
    filters_applied: dict
    skip: int
    limit: int
