"""
Search API endpoints for offers and needs.

SRS Requirements:
- FR-8: Search and discovery with semantic tags
- FR-8.2: Search by tags, type, location
- FR-8.4: WikiData-inspired semantic search with hierarchies
- FR-8.5: Order by distance (placeholder), recency
"""
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select, or_, and_, func

from app.core.db import get_session
from app.core.offers_needs import get_offer_tags, get_need_tags
from app.core.semantic_tags import expand_tags_for_search
from app.models.offer import Offer, OfferStatus
from app.models.need import Need, NeedStatus
from app.models.tag import Tag
from app.models.associations import OfferTag, NeedTag
from app.schemas.search import (
    SearchFilters,
    SearchResponse,
    SearchResult,
    SearchType,
    TagMatchMode,
    SortOrder,
)

router = APIRouter(prefix="/search", tags=["Search"])


def _build_search_result(
    session: Session,
    item_id: int,
    item_type: str,
    item: Offer | Need
) -> SearchResult:
    """Build a search result from an offer or need."""
    if item_type == "offer":
        tags = get_offer_tags(session, item_id)
    else:
        tags = get_need_tags(session, item_id)
    
    return SearchResult(
        id=item.id,
        type=item_type,
        title=item.title,
        description=item.description,
        creator_id=item.creator_id,
        is_remote=item.is_remote,
        location_name=item.location_name,
        capacity=item.capacity,
        accepted_count=item.accepted_count,
        status=item.status.value,
        tags=tags,
        created_at=item.created_at.isoformat(),
    )


@router.get("/", response_model=SearchResponse)
def search(
    session: Annotated[Session, Depends(get_session)],
    query: str | None = Query(None, description="Text search in title/description"),
    type: SearchType = Query(SearchType.ALL, description="Filter by type: offer, need, or all"),
    tags: list[str] | None = Query(None, description="Tags to filter by"),
    tag_match: TagMatchMode = Query(TagMatchMode.ANY, description="Match ANY or ALL tags"),
    semantic: bool = Query(True, description="Enable semantic tag expansion (parents/children/synonyms)"),
    is_remote: bool | None = Query(None, description="Filter by remote flag"),
    sort_by: SortOrder = Query(SortOrder.RECENCY, description="Sort order"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> SearchResponse:
    """
    Search for offers and needs with filters.
    
    SRS FR-8: Search and discovery with semantic tags.
    SRS FR-8.4: Semantic search expands tags using hierarchies and synonyms.
    
    Features:
    - Text search (ILIKE) in title and description
    - Filter by type (offer/need/all)
    - Filter by tags (any/all matching)
    - **Semantic expansion**: Automatically includes related tags (parents, children, synonyms)
    - Filter by remote flag
    - Sort by recency, distance (placeholder), or relevance
    
    Examples:
    - /search?query=python&type=offer
    - /search?tags=coding&tags=education&tag_match=all
    - /search?tags=gardening&semantic=true  (also finds lawn-mowing, landscaping, etc.)
    - /search?is_remote=true&sort_by=recency
    """
    results = []
    
    # Resolve tag names to IDs and expand semantically if enabled
    expanded_tag_ids = []
    if tags:
        # Normalize: lowercase, replace spaces with hyphens
        normalized_tags = [t.strip().lower().replace(' ', '-') for t in tags]
        
        # Get tag IDs from names - support both exact match and prefix match
        tag_ids = []
        for norm_tag in normalized_tags:
            # Try exact match first
            exact_match = session.exec(
                select(Tag).where(Tag.name == norm_tag)
            ).first()
            
            if exact_match:
                tag_ids.append(exact_match.id)
            else:
                # Try prefix match (e.g., "physical" matches "physical-work")
                prefix_matches = session.exec(
                    select(Tag).where(Tag.name.startswith(norm_tag))
                ).all()
                tag_ids.extend([t.id for t in prefix_matches])
        
        if semantic and tag_ids:
            # SRS FR-8.4: Expand tags using semantic relationships
            expanded_tag_ids = expand_tags_for_search(
                session,
                tag_ids,
                include_children=True,
                include_parents=True,
                include_synonyms=True
            )
        else:
            expanded_tag_ids = tag_ids
    
    # Determine which types to search
    search_offers = type in [SearchType.OFFER, SearchType.ALL]
    search_needs = type in [SearchType.NEED, SearchType.ALL]
    
    # Search offers
    if search_offers:
        offer_query = select(Offer).where(Offer.status == OfferStatus.ACTIVE)
        
        # Text search
        if query:
            search_pattern = f"%{query}%"
            offer_query = offer_query.where(
                or_(
                    Offer.title.ilike(search_pattern),
                    Offer.description.ilike(search_pattern)
                )
            )
        
        # Remote filter
        if is_remote is not None:
            offer_query = offer_query.where(Offer.is_remote == is_remote)
        
        # Tag filter with semantic expansion
        if expanded_tag_ids:
            if tag_match == TagMatchMode.ANY:
                # Match if offer has ANY of the expanded tags
                offer_query = offer_query.join(OfferTag).where(
                    OfferTag.tag_id.in_(expanded_tag_ids)
                ).distinct()
            else:
                # Match if offer has ALL of the original tags (not expanded for ALL mode)
                # This prevents over-matching in ALL mode
                original_tag_ids = [t.id for t in session.exec(
                    select(Tag).where(Tag.name.in_([t.strip().lower() for t in tags]))
                ).all()] if tags else []
                
                for tag_id in original_tag_ids:
                    offer_query = offer_query.where(
                        Offer.id.in_(
                            select(OfferTag.offer_id).where(OfferTag.tag_id == tag_id)
                        )
                    )
        
        # Sorting
        if sort_by == SortOrder.RECENCY:
            offer_query = offer_query.order_by(Offer.created_at.desc())
        elif sort_by == SortOrder.DISTANCE:
            # TODO: Implement distance-based sorting using location_lat/lon
            # For now, fall back to recency
            offer_query = offer_query.order_by(Offer.created_at.desc())
        elif sort_by == SortOrder.RELEVANCE:
            # Sort by number of matching tags (for tag searches)
            if tags:
                # Count matching tags per offer
                offer_query = offer_query.order_by(Offer.created_at.desc())
            else:
                offer_query = offer_query.order_by(Offer.created_at.desc())
        
        # Execute query (before pagination to get total count)
        all_offers = session.exec(offer_query).all()
        
        # Build results
        for offer in all_offers:
            results.append(_build_search_result(session, offer.id, "offer", offer))
    
    # Search needs
    if search_needs:
        need_query = select(Need).where(Need.status == NeedStatus.ACTIVE)
        
        # Text search
        if query:
            search_pattern = f"%{query}%"
            need_query = need_query.where(
                or_(
                    Need.title.ilike(search_pattern),
                    Need.description.ilike(search_pattern)
                )
            )
        
        # Remote filter
        if is_remote is not None:
            need_query = need_query.where(Need.is_remote == is_remote)
        
        # Tag filter with semantic expansion
        if expanded_tag_ids:
            if tag_match == TagMatchMode.ANY:
                # Match if need has ANY of the expanded tags
                need_query = need_query.join(NeedTag).where(
                    NeedTag.tag_id.in_(expanded_tag_ids)
                ).distinct()
            else:
                # Match if need has ALL of the original tags
                original_tag_ids = [t.id for t in session.exec(
                    select(Tag).where(Tag.name.in_([t.strip().lower() for t in tags]))
                ).all()] if tags else []
                
                for tag_id in original_tag_ids:
                    need_query = need_query.where(
                        Need.id.in_(
                            select(NeedTag.need_id).where(NeedTag.tag_id == tag_id)
                        )
                    )
        
        # Sorting
        if sort_by == SortOrder.RECENCY:
            need_query = need_query.order_by(Need.created_at.desc())
        elif sort_by == SortOrder.DISTANCE:
            # TODO: Implement distance-based sorting
            need_query = need_query.order_by(Need.created_at.desc())
        elif sort_by == SortOrder.RELEVANCE:
            need_query = need_query.order_by(Need.created_at.desc())
        
        # Execute query
        all_needs = session.exec(need_query).all()
        
        # Build results
        for need in all_needs:
            results.append(_build_search_result(session, need.id, "need", need))
    
    # Sort combined results if searching both types
    if search_offers and search_needs and sort_by == SortOrder.RECENCY:
        results.sort(key=lambda x: x.created_at, reverse=True)
    
    # Apply pagination
    total = len(results)
    paginated_results = results[skip:skip + limit]
    
    # Build response
    return SearchResponse(
        items=paginated_results,
        total=total,
        filters_applied={
            "query": query,
            "type": type.value,
            "tags": tags,
            "tag_match": tag_match.value if tags else None,
            "is_remote": is_remote,
            "sort_by": sort_by.value,
        },
        skip=skip,
        limit=limit,
    )


@router.get("/tags", response_model=list[dict])
def list_tags(
    session: Annotated[Session, Depends(get_session)],
    query: str | None = Query(None, description="Search tags by name"),
    limit: int = Query(50, ge=1, le=200),
) -> list[dict]:
    """
    List available tags with usage counts.
    
    Useful for:
    - Tag autocomplete in frontend
    - Discovering popular tags
    - Tag suggestions
    """
    tag_query = select(Tag)
    
    if query:
        search_pattern = f"%{query}%"
        tag_query = tag_query.where(Tag.name.ilike(search_pattern))
    
    tag_query = tag_query.order_by(Tag.usage_count.desc()).limit(limit)
    
    tags = session.exec(tag_query).all()
    
    return [
        {
            "id": tag.id,
            "name": tag.name,
            "description": tag.description,
            "usage_count": tag.usage_count,
        }
        for tag in tags
    ]
