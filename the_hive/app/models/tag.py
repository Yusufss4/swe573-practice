from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Tag(SQLModel, table=True):
    """Semantic tag model for categorizing Offers and Needs.
    
    SRS Requirements:
    - FR-8.1: Semantic tags to describe Offers and Needs
    - FR-8.3: Users can create new tags freely
    - FR-8.4: WikiData-inspired semantic structure with hierarchies and relationships
    
    Enhanced with WikiData-style features:
    - Label (name) + Description + Aliases for rich entity representation
    - Parent-child hierarchies for taxonomies
    - Synonym relationships (via SemanticTagSynonym)
    - Custom properties/statements (via SemanticTagProperty)
    """

    __tablename__ = "tags"

    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Label: primary name of the tag
    name: str = Field(unique=True, index=True, max_length=100)
    
    # Description: what this tag means/represents
    description: Optional[str] = Field(default=None, max_length=500)
    
    # Aliases: comma-separated alternative names/synonyms (simple storage)
    # For complex synonym relationships, use SemanticTagSynonym table
    aliases: Optional[str] = Field(default=None, max_length=500)
    
    # Hierarchy: parent tag for categorization (e.g., "gardening" parent of "lawn-mowing")
    parent_id: Optional[int] = Field(default=None, foreign_key="tags.id", index=True)
    
    # Usage tracking
    usage_count: int = Field(default=0)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
