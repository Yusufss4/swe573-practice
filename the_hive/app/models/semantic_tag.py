from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class SemanticTagSynonym(SQLModel, table=True):
    """Association table for tag synonyms (many-to-many self-relationship).
    
    SRS Requirements:
    - FR-8.4: WikiData-inspired tag relationships
    - Enables synonym groups for better search matching
    """

    __tablename__ = "semantic_tag_synonyms"

    id: Optional[int] = Field(default=None, primary_key=True)
    tag_id: int = Field(foreign_key="tags.id", index=True)
    synonym_id: int = Field(foreign_key="tags.id", index=True)


class SemanticTagProperty(SQLModel, table=True):
    """Stores custom properties/statements for semantic tags (WikiData-style).
    
    SRS Requirements:
    - FR-8.4: WikiData-inspired semantic structure
    - Enables rich metadata: skill_level, category, domain, etc.
    
    Example properties:
    - property="skill_level", value="intermediate"
    - property="category", value="outdoor_work"
    - property="requires", value="physical_strength"
    """

    __tablename__ = "semantic_tag_properties"

    id: Optional[int] = Field(default=None, primary_key=True)
    tag_id: int = Field(foreign_key="tags.id", index=True)
    
    # Property key (e.g., "skill_level", "category", "related_to")
    property_name: str = Field(max_length=100, index=True)
    
    # Property value (string representation)
    property_value: str = Field(max_length=500)
    
    # Optional: reference to another tag (for relationships)
    property_tag_id: Optional[int] = Field(default=None, foreign_key="tags.id")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
