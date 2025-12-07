from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# SRS FR-8.4: WikiData-style semantic tag schemas


class SemanticTagBase(BaseModel):
    """Base schema for semantic tag with WikiData-style fields."""
    
    name: str = Field(max_length=100, description="Primary label for the tag")
    description: Optional[str] = Field(None, max_length=500, description="What this tag represents")
    aliases: Optional[str] = Field(None, max_length=500, description="Comma-separated alternative names")


class SemanticTagCreate(SemanticTagBase):
    """Schema for creating a new semantic tag."""
    
    parent_id: Optional[int] = Field(None, description="Parent tag ID for hierarchy")


class SemanticTagUpdate(BaseModel):
    """Schema for updating an existing semantic tag."""
    
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    aliases: Optional[str] = Field(None, max_length=500)
    parent_id: Optional[int] = None


class SemanticTagResponse(BaseModel):
    """Schema for semantic tag response with full details."""
    
    id: int
    name: str
    description: Optional[str] = None
    aliases: list[str] = []  # Override to return as list instead of comma-separated string
    parent_id: Optional[int] = None
    usage_count: int = 0
    created_at: datetime
    updated_at: datetime
    
    # Nested relationships
    parent: Optional["SemanticTagSimple"] = None
    children: list["SemanticTagSimple"] = []
    synonyms: list["SemanticTagSimple"] = []


class SemanticTagSimple(BaseModel):
    """Simplified tag schema for nested references."""
    
    id: int
    name: str
    description: Optional[str] = None


class SemanticTagTree(BaseModel):
    """Schema for tag with full tree structure (simplified for tree views)."""
    
    id: int
    name: str
    description: Optional[str] = None
    aliases: list[str] = []  # List of alias strings
    usage_count: int = 0
    children: list["SemanticTagTree"] = []


class SemanticTagListResponse(BaseModel):
    """Paginated list of semantic tags."""
    
    tags: list[SemanticTagResponse]
    total: int
    page: int
    page_size: int


class AddSynonymRequest(BaseModel):
    """Request to add a synonym relationship."""
    
    synonym_id: int = Field(description="ID of tag to mark as synonym")


class SemanticTagPropertyCreate(BaseModel):
    """Schema for creating custom tag properties (WikiData-style statements)."""
    
    property_name: str = Field(max_length=100, description="Property key (e.g., 'skill_level', 'category')")
    property_value: str = Field(max_length=500, description="Property value")
    property_tag_id: Optional[int] = Field(None, description="Reference to another tag (for relationships)")


class SemanticTagPropertyResponse(SemanticTagPropertyCreate):
    """Schema for property response."""
    
    id: int
    tag_id: int
    created_at: datetime


# Enable forward references
SemanticTagResponse.model_rebuild()
SemanticTagSimple.model_rebuild()
SemanticTagTree.model_rebuild()
