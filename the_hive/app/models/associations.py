from typing import Optional

from sqlmodel import Field, SQLModel


class OfferTag(SQLModel, table=True):
    """Association table linking Offers to Tags.
    
    SRS Requirements:
    - FR-3.5: Users assign one or more semantic tags when posting
    - FR-8.1: Semantic tags describe Offers and Needs
    """

    __tablename__ = "offer_tags"

    id: Optional[int] = Field(default=None, primary_key=True)
    offer_id: int = Field(foreign_key="offers.id", index=True)
    tag_id: int = Field(foreign_key="tags.id", index=True)


class NeedTag(SQLModel, table=True):
    """Association table linking Needs to Tags.
    
    SRS Requirements:
    - FR-3.5: Users assign one or more semantic tags when posting
    - FR-8.1: Semantic tags describe Offers and Needs
    """

    __tablename__ = "need_tags"

    id: Optional[int] = Field(default=None, primary_key=True)
    need_id: int = Field(foreign_key="needs.id", index=True)
    tag_id: int = Field(foreign_key="tags.id", index=True)
