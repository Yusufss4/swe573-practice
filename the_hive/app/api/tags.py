"""Public API for browsing semantic tags (non-admin).

SRS Requirements:
- FR-8.4: Users can browse tag hierarchy for discovery
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.core.db import SessionDep
from app.models.tag import Tag
from app.core.semantic_tags import build_tag_tree, get_tag_with_relationships
from app.schemas.semantic_tag import SemanticTagTree, SemanticTagResponse, SemanticTagSimple


router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("/tree", response_model=list[SemanticTagTree])
def get_public_tag_tree(
    session: SessionDep,
) -> list[dict]:
    """Get hierarchical tree of all tags (public access).
    
    SRS FR-8.4: Browse complete tag taxonomy for discovery
    """
    return build_tag_tree(session, root_id=None)


@router.get("/{tag_id}", response_model=SemanticTagResponse)
def get_public_tag(
    tag_id: int,
    session: SessionDep,
) -> SemanticTagResponse:
    """Get a tag with relationships (public access).
    
    SRS FR-8.4: View tag details including parent/children/synonyms
    """
    tag, children, synonyms, ancestors = get_tag_with_relationships(session, tag_id)
    
    if not tag:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag {tag_id} not found"
        )
    
    parent = session.get(Tag, tag.parent_id) if tag.parent_id else None
    
    # Convert comma-separated aliases string to list
    aliases_list = []
    if tag.aliases:
        aliases_list = [a.strip() for a in tag.aliases.split(',') if a.strip()]
    
    return SemanticTagResponse(
        id=tag.id,
        name=tag.name,
        description=tag.description,
        aliases=aliases_list,
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
            for c in children
        ],
        synonyms=[
            SemanticTagSimple(id=s.id, name=s.name, description=s.description)
            for s in synonyms
        ],
    )


@router.get("/", response_model=list[SemanticTagResponse])
def list_public_tags(
    session: SessionDep,
) -> list[SemanticTagResponse]:
    """List all tags with basic info (public access).
    
    SRS FR-8.4: Browse all available tags
    """
    tags = session.exec(select(Tag)).all()
    
    results = []
    for tag in tags:
        _, children, synonyms, _ = get_tag_with_relationships(session, tag.id)
        parent = session.get(Tag, tag.parent_id) if tag.parent_id else None
        
        # Convert comma-separated aliases string to list
        aliases_list = []
        if tag.aliases:
            aliases_list = [a.strip() for a in tag.aliases.split(',') if a.strip()]
        
        results.append(SemanticTagResponse(
            id=tag.id,
            name=tag.name,
            description=tag.description,
            aliases=aliases_list,
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
                for c in children
            ],
            synonyms=[
                SemanticTagSimple(id=s.id, name=s.name, description=s.description)
                for s in synonyms
            ],
        ))
    
    return results
