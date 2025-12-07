"""Core business logic for semantic tags.

SRS Requirements:
- FR-8.4: WikiData-inspired semantic tag system
- Provides hierarchy traversal, synonym resolution, and tag expansion for search
"""

from collections.abc import Sequence
from sqlmodel import Session, select, or_

from app.models.tag import Tag
from app.models.semantic_tag import SemanticTagSynonym, SemanticTagProperty


def get_tag_with_relationships(session: Session, tag_id: int) -> tuple[Tag | None, list[Tag], list[Tag], list[Tag]]:
    """Get a tag with its parent, children, and synonyms.
    
    Returns:
        tuple: (tag, children, synonyms, ancestors)
    """
    tag = session.get(Tag, tag_id)
    if not tag:
        return None, [], [], []
    
    # Get children
    children = session.exec(
        select(Tag).where(Tag.parent_id == tag_id)
    ).all()
    
    # Get synonyms (bidirectional)
    synonym_ids = set()
    
    # Get tags where current tag is listed as synonym
    syn_links_1 = session.exec(
        select(SemanticTagSynonym).where(SemanticTagSynonym.tag_id == tag_id)
    ).all()
    synonym_ids.update(link.synonym_id for link in syn_links_1)
    
    # Get tags where current tag is the synonym of another
    syn_links_2 = session.exec(
        select(SemanticTagSynonym).where(SemanticTagSynonym.synonym_id == tag_id)
    ).all()
    synonym_ids.update(link.tag_id for link in syn_links_2)
    
    synonyms = []
    if synonym_ids:
        synonyms = session.exec(
            select(Tag).where(Tag.id.in_(synonym_ids))
        ).all()
    
    # Get ancestors (parent chain)
    ancestors = []
    current = tag
    visited = {tag_id}  # Prevent cycles
    
    while current.parent_id and current.parent_id not in visited:
        parent = session.get(Tag, current.parent_id)
        if parent:
            ancestors.append(parent)
            visited.add(parent.id)
            current = parent
        else:
            break
    
    return tag, list(children), list(synonyms), ancestors


def get_tag_descendants(session: Session, tag_id: int, include_self: bool = True) -> list[int]:
    """Get all descendant tag IDs (children, grandchildren, etc.) recursively.
    
    SRS FR-8.4: Enable hierarchical search expansion
    """
    descendants = {tag_id} if include_self else set()
    to_process = [tag_id]
    visited = set()
    
    while to_process:
        current_id = to_process.pop()
        if current_id in visited:
            continue
        visited.add(current_id)
        
        children = session.exec(
            select(Tag.id).where(Tag.parent_id == current_id)
        ).all()
        
        for child_id in children:
            if child_id not in visited:
                descendants.add(child_id)
                to_process.append(child_id)
    
    return list(descendants)


def get_tag_ancestors(session: Session, tag_id: int, include_self: bool = True) -> list[int]:
    """Get all ancestor tag IDs (parent, grandparent, etc.) recursively.
    
    SRS FR-8.4: Enable hierarchical search expansion
    """
    ancestors = {tag_id} if include_self else set()
    current_id = tag_id
    visited = set()
    
    while current_id and current_id not in visited:
        visited.add(current_id)
        tag = session.get(Tag, current_id)
        
        if tag and tag.parent_id:
            ancestors.add(tag.parent_id)
            current_id = tag.parent_id
        else:
            break
    
    return list(ancestors)


def get_related_tags(session: Session, tag_id: int) -> list[int]:
    """Get all synonyms of a tag (bidirectional).
    
    SRS FR-8.4: Enable synonym-based search expansion
    """
    related = {tag_id}
    
    # Get direct synonyms
    syn_links = session.exec(
        select(SemanticTagSynonym).where(
            or_(
                SemanticTagSynonym.tag_id == tag_id,
                SemanticTagSynonym.synonym_id == tag_id
            )
        )
    ).all()
    
    for link in syn_links:
        related.add(link.tag_id)
        related.add(link.synonym_id)
    
    return list(related)


def expand_tag_for_search(
    session: Session,
    tag_id: int,
    include_children: bool = True,
    include_parents: bool = True,
    include_synonyms: bool = True
) -> list[int]:
    """Expand a tag ID to include related tags for semantic search.
    
    SRS FR-8.4: Core function for semantic search enhancement
    
    Args:
        tag_id: The base tag to expand
        include_children: Include all descendant tags
        include_parents: Include all ancestor tags
        include_synonyms: Include synonym tags
    
    Returns:
        List of tag IDs to search (includes original tag_id)
    """
    expanded = {tag_id}
    
    if include_synonyms:
        synonyms = get_related_tags(session, tag_id)
        expanded.update(synonyms)
    
    if include_children:
        descendants = get_tag_descendants(session, tag_id, include_self=False)
        expanded.update(descendants)
    
    if include_parents:
        ancestors = get_tag_ancestors(session, tag_id, include_self=False)
        expanded.update(ancestors)
    
    return list(expanded)


def expand_tags_for_search(
    session: Session,
    tag_ids: list[int],
    include_children: bool = True,
    include_parents: bool = True,
    include_synonyms: bool = True
) -> list[int]:
    """Expand multiple tag IDs for semantic search.
    
    SRS FR-8.4: Batch version for search queries with multiple tags
    """
    all_expanded = set()
    
    for tag_id in tag_ids:
        expanded = expand_tag_for_search(
            session, tag_id, include_children, include_parents, include_synonyms
        )
        all_expanded.update(expanded)
    
    return list(all_expanded)


def add_synonym_relationship(session: Session, tag_id: int, synonym_id: int) -> bool:
    """Add a bidirectional synonym relationship between two tags.
    
    Returns:
        bool: True if added, False if already exists
    """
    # Check if relationship already exists (either direction)
    existing = session.exec(
        select(SemanticTagSynonym).where(
            or_(
                (SemanticTagSynonym.tag_id == tag_id) & (SemanticTagSynonym.synonym_id == synonym_id),
                (SemanticTagSynonym.tag_id == synonym_id) & (SemanticTagSynonym.synonym_id == tag_id)
            )
        )
    ).first()
    
    if existing:
        return False
    
    # Add the relationship
    synonym_link = SemanticTagSynonym(tag_id=tag_id, synonym_id=synonym_id)
    session.add(synonym_link)
    session.commit()
    return True


def remove_synonym_relationship(session: Session, tag_id: int, synonym_id: int) -> bool:
    """Remove synonym relationship between two tags.
    
    Returns:
        bool: True if removed, False if not found
    """
    # Delete both directions
    links = session.exec(
        select(SemanticTagSynonym).where(
            or_(
                (SemanticTagSynonym.tag_id == tag_id) & (SemanticTagSynonym.synonym_id == synonym_id),
                (SemanticTagSynonym.tag_id == synonym_id) & (SemanticTagSynonym.synonym_id == tag_id)
            )
        )
    ).all()
    
    if not links:
        return False
    
    for link in links:
        session.delete(link)
    
    session.commit()
    return True


def get_tag_properties(session: Session, tag_id: int) -> list[SemanticTagProperty]:
    """Get all custom properties for a tag."""
    return list(session.exec(
        select(SemanticTagProperty).where(SemanticTagProperty.tag_id == tag_id)
    ).all())


def add_tag_property(
    session: Session,
    tag_id: int,
    property_name: str,
    property_value: str,
    property_tag_id: int | None = None
) -> SemanticTagProperty:
    """Add a custom property to a tag (WikiData-style statement)."""
    prop = SemanticTagProperty(
        tag_id=tag_id,
        property_name=property_name,
        property_value=property_value,
        property_tag_id=property_tag_id
    )
    session.add(prop)
    session.commit()
    session.refresh(prop)
    return prop


def build_tag_tree(session: Session, root_id: int | None = None) -> list[dict]:
    """Build a hierarchical tree of tags.
    
    Args:
        root_id: Start from this tag, or None for top-level tags
    
    Returns:
        List of tag dicts with nested children
    """
    tags = session.exec(
        select(Tag).where(Tag.parent_id == root_id)
    ).all()
    
    tree = []
    for tag in tags:
        # Convert comma-separated aliases string to list
        aliases_list = []
        if tag.aliases:
            aliases_list = [a.strip() for a in tag.aliases.split(',') if a.strip()]
        
        node = {
            "id": tag.id,
            "name": tag.name,
            "description": tag.description,
            "aliases": aliases_list,  # Now a list instead of string
            "usage_count": tag.usage_count,
            "children": build_tag_tree(session, tag.id)
        }
        tree.append(node)
    
    return tree
