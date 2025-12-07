"""Admin API endpoints for managing semantic tags.

SRS Requirements:
- FR-8.4: WikiData-inspired semantic tag management
- Admin-only operations for tag hierarchy and relationships
"""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status
from sqlmodel import Session, select, func

from app.core.auth import AdminUser
from app.core.db import SessionDep
from app.models.tag import Tag
from app.models.semantic_tag import SemanticTagSynonym, SemanticTagProperty
from app.schemas.semantic_tag import (
    SemanticTagCreate,
    SemanticTagUpdate,
    SemanticTagResponse,
    SemanticTagSimple,
    SemanticTagListResponse,
    SemanticTagTree,
    AddSynonymRequest,
    SemanticTagPropertyCreate,
    SemanticTagPropertyResponse,
)
from app.core.semantic_tags import (
    get_tag_with_relationships,
    add_synonym_relationship,
    remove_synonym_relationship,
    get_tag_properties,
    add_tag_property,
    build_tag_tree,
)


router = APIRouter(prefix="/admin/semantic-tags", tags=["admin-semantic-tags"])


def _build_tag_response(
    tag: Tag,
    children: list[Tag] = None,
    synonyms: list[Tag] = None,
    parent: Tag | None = None
) -> SemanticTagResponse:
    """Build a complete SemanticTagResponse with relationships."""
    return SemanticTagResponse(
        id=tag.id,
        name=tag.name,
        description=tag.description,
        aliases=tag.aliases,
        parent_id=tag.parent_id,
        usage_count=tag.usage_count,
        created_at=tag.created_at,
        updated_at=tag.updated_at,
        parent=SemanticTagSimple(
            id=parent.id,
            name=parent.name,
            description=parent.description
        ) if parent else None,
        children=[
            SemanticTagSimple(id=c.id, name=c.name, description=c.description)
            for c in (children or [])
        ],
        synonyms=[
            SemanticTagSimple(id=s.id, name=s.name, description=s.description)
            for s in (synonyms or [])
        ],
    )


@router.post("/", response_model=SemanticTagResponse, status_code=status.HTTP_201_CREATED)
def create_semantic_tag(
    tag_data: SemanticTagCreate,
    admin: AdminUser,
    session: SessionDep,
) -> SemanticTagResponse:
    """Create a new semantic tag (Admin only).
    
    SRS FR-8.4: Admin creates semantic tags with WikiData-style structure
    """
    # Check if name already exists
    existing = session.exec(
        select(Tag).where(Tag.name == tag_data.name)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tag with name '{tag_data.name}' already exists"
        )
    
    # Validate parent exists if specified
    parent = None
    if tag_data.parent_id:
        parent = session.get(Tag, tag_data.parent_id)
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Parent tag {tag_data.parent_id} not found"
            )
    
    # Create tag
    tag = Tag(
        name=tag_data.name,
        description=tag_data.description,
        aliases=tag_data.aliases,
        parent_id=tag_data.parent_id,
    )
    
    session.add(tag)
    session.commit()
    session.refresh(tag)
    
    return _build_tag_response(tag, parent=parent)


@router.get("/", response_model=SemanticTagListResponse)
def list_semantic_tags(
    admin: AdminUser,
    session: SessionDep,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    parent_id: int | None = Query(None, description="Filter by parent tag ID (null for root tags)"),
    search: str | None = Query(None, description="Search in name, description, aliases"),
) -> SemanticTagListResponse:
    """List semantic tags with pagination and filtering (Admin only).
    
    SRS FR-8.4: Browse tag hierarchy
    """
    query = select(Tag)
    
    # Filter by parent
    if parent_id is not None:
        query = query.where(Tag.parent_id == parent_id)
    elif parent_id is None and "parent_id" in dict(Query):
        # Explicitly filtering for root tags (parent_id IS NULL)
        query = query.where(Tag.parent_id.is_(None))
    
    # Search filter
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            (Tag.name.ilike(search_pattern)) |
            (Tag.description.ilike(search_pattern)) |
            (Tag.aliases.ilike(search_pattern))
        )
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = session.exec(count_query).one()
    
    # Paginate
    query = query.offset((page - 1) * page_size).limit(page_size)
    tags = session.exec(query).all()
    
    # Build responses with relationships
    tag_responses = []
    for tag in tags:
        _, children, synonyms, _ = get_tag_with_relationships(session, tag.id)
        parent = session.get(Tag, tag.parent_id) if tag.parent_id else None
        tag_responses.append(_build_tag_response(tag, children, synonyms, parent))
    
    return SemanticTagListResponse(
        tags=tag_responses,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/tree", response_model=list[SemanticTagTree])
def get_tag_tree(
    admin: AdminUser,
    session: SessionDep,
    root_id: int | None = Query(None, description="Start from this tag (null for top level)"),
) -> list[dict]:
    """Get hierarchical tree of tags (Admin only).
    
    SRS FR-8.4: Visualize complete tag taxonomy
    """
    return build_tag_tree(session, root_id)


@router.get("/{tag_id}", response_model=SemanticTagResponse)
def get_semantic_tag(
    tag_id: int,
    admin: AdminUser,
    session: SessionDep,
) -> SemanticTagResponse:
    """Get a semantic tag with all relationships (Admin only).
    
    SRS FR-8.4: View complete tag entity details
    """
    tag, children, synonyms, ancestors = get_tag_with_relationships(session, tag_id)
    
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag {tag_id} not found"
        )
    
    parent = session.get(Tag, tag.parent_id) if tag.parent_id else None
    
    return _build_tag_response(tag, children, synonyms, parent)


@router.patch("/{tag_id}", response_model=SemanticTagResponse)
def update_semantic_tag(
    tag_id: int,
    tag_data: SemanticTagUpdate,
    admin: AdminUser,
    session: SessionDep,
) -> SemanticTagResponse:
    """Update a semantic tag (Admin only).
    
    SRS FR-8.4: Modify tag properties and relationships
    """
    tag = session.get(Tag, tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag {tag_id} not found"
        )
    
    # Check name uniqueness if changing
    if tag_data.name and tag_data.name != tag.name:
        existing = session.exec(
            select(Tag).where(Tag.name == tag_data.name)
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tag with name '{tag_data.name}' already exists"
            )
        tag.name = tag_data.name
    
    # Update fields
    if tag_data.description is not None:
        tag.description = tag_data.description
    
    if tag_data.aliases is not None:
        tag.aliases = tag_data.aliases
    
    # Validate parent if changing
    if tag_data.parent_id is not None:
        if tag_data.parent_id == tag_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tag cannot be its own parent"
            )
        
        if tag_data.parent_id > 0:
            parent = session.get(Tag, tag_data.parent_id)
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Parent tag {tag_data.parent_id} not found"
                )
        
        tag.parent_id = tag_data.parent_id if tag_data.parent_id > 0 else None
    
    from datetime import datetime
    tag.updated_at = datetime.utcnow()
    
    session.add(tag)
    session.commit()
    session.refresh(tag)
    
    _, children, synonyms, _ = get_tag_with_relationships(session, tag_id)
    parent = session.get(Tag, tag.parent_id) if tag.parent_id else None
    
    return _build_tag_response(tag, children, synonyms, parent)


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_semantic_tag(
    tag_id: int,
    admin: AdminUser,
    session: SessionDep,
):
    """Delete a semantic tag (Admin only).
    
    SRS FR-8.4: Remove tags from system
    
    Warning: This will orphan child tags (set their parent_id to NULL)
    """
    tag = session.get(Tag, tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag {tag_id} not found"
        )
    
    # Orphan children instead of cascade delete
    children = session.exec(
        select(Tag).where(Tag.parent_id == tag_id)
    ).all()
    
    for child in children:
        child.parent_id = None
        session.add(child)
    
    # Delete synonym relationships
    session.exec(
        select(SemanticTagSynonym).where(
            (SemanticTagSynonym.tag_id == tag_id) |
            (SemanticTagSynonym.synonym_id == tag_id)
        )
    ).all()
    
    # Delete properties
    props = session.exec(
        select(SemanticTagProperty).where(SemanticTagProperty.tag_id == tag_id)
    ).all()
    for prop in props:
        session.delete(prop)
    
    session.delete(tag)
    session.commit()


@router.post("/{tag_id}/synonyms", status_code=status.HTTP_201_CREATED)
def add_synonym(
    tag_id: int,
    request: AddSynonymRequest,
    admin: AdminUser,
    session: SessionDep,
) -> dict:
    """Add a synonym relationship between tags (Admin only).
    
    SRS FR-8.4: Create semantic relationships
    """
    tag = session.get(Tag, tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag {tag_id} not found"
        )
    
    synonym = session.get(Tag, request.synonym_id)
    if not synonym:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Synonym tag {request.synonym_id} not found"
        )
    
    if tag_id == request.synonym_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag cannot be synonym of itself"
        )
    
    added = add_synonym_relationship(session, tag_id, request.synonym_id)
    
    if not added:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Synonym relationship already exists"
        )
    
    return {"message": f"Synonym relationship added between '{tag.name}' and '{synonym.name}'"}


@router.delete("/{tag_id}/synonyms/{synonym_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_synonym(
    tag_id: int,
    synonym_id: int,
    admin: AdminUser,
    session: SessionDep,
):
    """Remove a synonym relationship (Admin only).
    
    SRS FR-8.4: Manage semantic relationships
    """
    removed = remove_synonym_relationship(session, tag_id, synonym_id)
    
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Synonym relationship not found"
        )


@router.get("/{tag_id}/properties", response_model=list[SemanticTagPropertyResponse])
def list_tag_properties(
    tag_id: int,
    admin: AdminUser,
    session: SessionDep,
) -> list[SemanticTagPropertyResponse]:
    """List all custom properties for a tag (Admin only).
    
    SRS FR-8.4: View WikiData-style statements
    """
    tag = session.get(Tag, tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag {tag_id} not found"
        )
    
    properties = get_tag_properties(session, tag_id)
    
    return [
        SemanticTagPropertyResponse(
            id=prop.id,
            tag_id=prop.tag_id,
            property_name=prop.property_name,
            property_value=prop.property_value,
            property_tag_id=prop.property_tag_id,
            created_at=prop.created_at,
        )
        for prop in properties
    ]


@router.post("/{tag_id}/properties", response_model=SemanticTagPropertyResponse, status_code=status.HTTP_201_CREATED)
def create_tag_property(
    tag_id: int,
    property_data: SemanticTagPropertyCreate,
    admin: AdminUser,
    session: SessionDep,
) -> SemanticTagPropertyResponse:
    """Add a custom property to a tag (Admin only).
    
    SRS FR-8.4: Create WikiData-style statements
    
    Examples:
    - property_name="skill_level", property_value="intermediate"
    - property_name="category", property_value="outdoor_work"
    - property_name="requires", property_tag_id=<another_tag_id>
    """
    tag = session.get(Tag, tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag {tag_id} not found"
        )
    
    # Validate property_tag_id if provided
    if property_data.property_tag_id:
        ref_tag = session.get(Tag, property_data.property_tag_id)
        if not ref_tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Referenced tag {property_data.property_tag_id} not found"
            )
    
    prop = add_tag_property(
        session,
        tag_id,
        property_data.property_name,
        property_data.property_value,
        property_data.property_tag_id,
    )
    
    return SemanticTagPropertyResponse(
        id=prop.id,
        tag_id=prop.tag_id,
        property_name=prop.property_name,
        property_value=prop.property_value,
        property_tag_id=prop.property_tag_id,
        created_at=prop.created_at,
    )
