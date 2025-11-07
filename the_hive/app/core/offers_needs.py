"""
Utility functions for Offers and Needs.
"""
from datetime import datetime
from typing import Type

from sqlmodel import Session, select

from app.models.associations import NeedTag, OfferTag
from app.models.need import Need, NeedStatus
from app.models.offer import Offer, OfferStatus
from app.models.tag import Tag


def get_or_create_tag(session: Session, tag_name: str) -> Tag:
    """
    Get existing tag or create a new one.
    
    SRS FR-8.3: Users can create new tags freely.
    """
    tag_name = tag_name.strip().lower()
    
    # Try to find existing tag
    statement = select(Tag).where(Tag.name == tag_name)
    tag = session.exec(statement).first()
    
    if tag:
        # Increment usage count
        tag.usage_count += 1
        tag.updated_at = datetime.utcnow()
        session.add(tag)
        return tag
    
    # Create new tag
    new_tag = Tag(name=tag_name, usage_count=1)
    session.add(new_tag)
    session.flush()  # Get the ID without committing
    
    return new_tag


def associate_tags_to_offer(session: Session, offer_id: int, tag_names: list[str]) -> list[Tag]:
    """Associate tags with an offer."""
    tags = []
    
    for tag_name in tag_names:
        tag = get_or_create_tag(session, tag_name)
        tags.append(tag)
        
        # Create association
        offer_tag = OfferTag(offer_id=offer_id, tag_id=tag.id)
        session.add(offer_tag)
    
    return tags


def associate_tags_to_need(session: Session, need_id: int, tag_names: list[str]) -> list[Tag]:
    """Associate tags with a need."""
    tags = []
    
    for tag_name in tag_names:
        tag = get_or_create_tag(session, tag_name)
        tags.append(tag)
        
        # Create association
        need_tag = NeedTag(need_id=need_id, tag_id=tag.id)
        session.add(need_tag)
    
    return tags


def get_offer_tags(session: Session, offer_id: int) -> list[str]:
    """Get all tag names for an offer."""
    statement = (
        select(Tag.name)
        .join(OfferTag, OfferTag.tag_id == Tag.id)
        .where(OfferTag.offer_id == offer_id)
    )
    tags = session.exec(statement).all()
    return list(tags)


def get_need_tags(session: Session, need_id: int) -> list[str]:
    """Get all tag names for a need."""
    statement = (
        select(Tag.name)
        .join(NeedTag, NeedTag.tag_id == Tag.id)
        .where(NeedTag.need_id == need_id)
    )
    tags = session.exec(statement).all()
    return list(tags)


def update_offer_tags(session: Session, offer_id: int, new_tag_names: list[str]):
    """Update tags for an offer by replacing all associations."""
    # Remove old associations
    statement = select(OfferTag).where(OfferTag.offer_id == offer_id)
    old_associations = session.exec(statement).all()
    for assoc in old_associations:
        session.delete(assoc)
    
    # Create new associations
    associate_tags_to_offer(session, offer_id, new_tag_names)


def update_need_tags(session: Session, need_id: int, new_tag_names: list[str]):
    """Update tags for a need by replacing all associations."""
    # Remove old associations
    statement = select(NeedTag).where(NeedTag.need_id == need_id)
    old_associations = session.exec(statement).all()
    for assoc in old_associations:
        session.delete(assoc)
    
    # Create new associations
    associate_tags_to_need(session, need_id, new_tag_names)


def archive_expired_items(session: Session):
    """
    Archive expired offers and needs.
    
    SRS FR-3.3: Offers and needs shall automatically archive after expiration.
    SRS FR-12.1: System shall automatically archive expired or completed items.
    
    This is a simple implementation that runs on-demand.
    In production, this would be a scheduled background job.
    """
    now = datetime.utcnow()
    
    # Archive expired offers
    statement = select(Offer).where(
        Offer.end_date < now,
        Offer.status == OfferStatus.ACTIVE
    )
    expired_offers = session.exec(statement).all()
    for offer in expired_offers:
        offer.status = OfferStatus.EXPIRED
        offer.updated_at = now
        session.add(offer)
    
    # Archive expired needs
    statement = select(Need).where(
        Need.end_date < now,
        Need.status == NeedStatus.ACTIVE
    )
    expired_needs = session.exec(statement).all()
    for need in expired_needs:
        need.status = NeedStatus.EXPIRED
        need.updated_at = now
        session.add(need)
    
    session.commit()
    
    return len(expired_offers), len(expired_needs)


def check_and_archive_item(session: Session, item: Offer | Need) -> bool:
    """
    Check if an item is expired and archive it.
    
    Returns True if item was archived, False otherwise.
    This is the 'archive expired on read' hook mentioned in requirements.
    """
    now = datetime.utcnow()
    
    if item.end_date < now and item.status in [OfferStatus.ACTIVE, NeedStatus.ACTIVE]:
        item.status = OfferStatus.EXPIRED if isinstance(item, Offer) else NeedStatus.EXPIRED
        item.updated_at = now
        session.add(item)
        session.commit()
        return True
    
    return False
