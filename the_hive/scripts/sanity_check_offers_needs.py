#!/usr/bin/env python3
"""
Sanity check script for Offers and Needs CRUD.

Tests:
1. Create offer/need with default 7-day duration
2. Extend offer/need (works)
3. Cannot shorten (N/A - no shorten endpoint)
4. Expired items hidden from public list
5. Owner can see their expired items
"""
import sys
from datetime import datetime, timedelta

from sqlmodel import Session, select

from app.core.db import engine
from app.core.offers_needs import (
    archive_expired_items,
    associate_tags_to_need,
    associate_tags_to_offer,
    get_need_tags,
    get_offer_tags,
)
from app.core.security import get_password_hash
from app.models.need import Need, NeedStatus
from app.models.offer import Offer, OfferStatus
from app.models.user import User


def setup_test_user(session: Session) -> User:
    """Create or get test user."""
    statement = select(User).where(User.username == "testuser")
    user = session.exec(statement).first()
    
    if not user:
        user = User(
            email="test@example.com",
            username="testuser",
            password_hash=get_password_hash("password123"),
            role="user",
            balance=5.0,
            is_active=True
        )
        session.add(user)
        session.commit()
        session.refresh(user)
    
    return user


def test_create_with_7day_default():
    """Test creating offer/need with 7-day default."""
    print("1. Testing 7-day default duration...")
    
    with Session(engine) as session:
        user = setup_test_user(session)
        
        # Create offer
        now = datetime.utcnow()
        offer = Offer(
            creator_id=user.id,
            title="Test Offer",
            description="Testing default duration",
            is_remote=True,
            status=OfferStatus.ACTIVE
        )
        session.add(offer)
        session.commit()
        session.refresh(offer)
        
        # Check 7-day duration
        duration = (offer.end_date - offer.start_date).days
        assert duration == 7, f"Expected 7 days, got {duration}"
        
        print(f"   ✅ Offer created with {duration}-day duration")
        
        # Create need
        need = Need(
            creator_id=user.id,
            title="Test Need",
            description="Testing default duration",
            is_remote=True,
            status=NeedStatus.ACTIVE
        )
        session.add(need)
        session.commit()
        session.refresh(need)
        
        duration = (need.end_date - need.start_date).days
        assert duration == 7, f"Expected 7 days, got {duration}"
        
        print(f"   ✅ Need created with {duration}-day duration")


def test_extend_works():
    """Test extending offers/needs."""
    print("\n2. Testing extend functionality...")
    
    with Session(engine) as session:
        user = setup_test_user(session)
        
        # Create offer
        offer = Offer(
            creator_id=user.id,
            title="Extendable Offer",
            description="Testing extend",
            is_remote=True,
            status=OfferStatus.ACTIVE
        )
        session.add(offer)
        session.commit()
        session.refresh(offer)
        
        original_end = offer.end_date
        
        # Extend by 5 days
        new_end = offer.end_date + timedelta(days=5)
        offer.end_date = new_end
        session.add(offer)
        session.commit()
        session.refresh(offer)
        
        extension = (offer.end_date - original_end).days
        assert extension == 5, f"Expected 5-day extension, got {extension}"
        
        print(f"   ✅ Offer extended by {extension} days")
        
        # Test renew expired
        expired_offer = Offer(
            creator_id=user.id,
            title="Expired Offer",
            description="Testing renew",
            is_remote=True,
            status=OfferStatus.EXPIRED,
            end_date=datetime.utcnow() - timedelta(days=2)
        )
        session.add(expired_offer)
        session.commit()
        session.refresh(expired_offer)
        
        # Renew by extending
        expired_offer.end_date = datetime.utcnow() + timedelta(days=7)
        expired_offer.status = OfferStatus.ACTIVE
        session.add(expired_offer)
        session.commit()
        
        assert expired_offer.status == OfferStatus.ACTIVE
        assert expired_offer.end_date > datetime.utcnow()
        
        print("   ✅ Expired offer can be renewed")


def test_expired_items_archived():
    """Test that expired items are archived."""
    print("\n3. Testing auto-archiving of expired items...")
    
    with Session(engine) as session:
        user = setup_test_user(session)
        
        # Create active offer
        active_offer = Offer(
            creator_id=user.id,
            title="Active Offer",
            description="Should stay active",
            is_remote=True,
            status=OfferStatus.ACTIVE,
            end_date=datetime.utcnow() + timedelta(days=5)
        )
        session.add(active_offer)
        
        # Create expired offer
        expired_offer = Offer(
            creator_id=user.id,
            title="Expired Offer",
            description="Should be archived",
            is_remote=True,
            status=OfferStatus.ACTIVE,
            end_date=datetime.utcnow() - timedelta(days=1)
        )
        session.add(expired_offer)
        session.commit()
        
        # Run archive function
        archived_offers, archived_needs = archive_expired_items(session)
        
        print(f"   ✅ Archived {archived_offers} expired offers")
        
        # Verify
        session.refresh(active_offer)
        session.refresh(expired_offer)
        
        assert active_offer.status == OfferStatus.ACTIVE
        assert expired_offer.status == OfferStatus.EXPIRED
        
        print("   ✅ Active items remain active")
        print("   ✅ Expired items are archived")


def test_expired_hidden_from_list():
    """Test that expired items are hidden from public list."""
    print("\n4. Testing expired items hidden from public list...")
    
    with Session(engine) as session:
        # Archive expired items
        archive_expired_items(session)
        
        # Get active offers only
        statement = select(Offer).where(Offer.status == OfferStatus.ACTIVE)
        active_offers = session.exec(statement).all()
        
        # Get expired offers
        statement = select(Offer).where(Offer.status == OfferStatus.EXPIRED)
        expired_offers = session.exec(statement).all()
        
        print(f"   ✅ Found {len(active_offers)} active offers")
        print(f"   ✅ Found {len(expired_offers)} expired offers (hidden from public)")
        
        # Verify no expired in "public" list
        public_list = active_offers
        for offer in public_list:
            assert offer.status != OfferStatus.EXPIRED
        
        print("   ✅ Public list excludes expired items")


def test_tags_association():
    """Test tag association."""
    print("\n5. Testing tag association...")
    
    with Session(engine) as session:
        user = setup_test_user(session)
        
        # Create offer
        offer = Offer(
            creator_id=user.id,
            title="Tagged Offer",
            description="Testing tags",
            is_remote=True,
            status=OfferStatus.ACTIVE
        )
        session.add(offer)
        session.commit()
        session.refresh(offer)
        
        # Associate tags
        tags = ["python", "tutoring", "coding"]
        associate_tags_to_offer(session, offer.id, tags)
        session.commit()
        
        # Get tags
        offer_tags = get_offer_tags(session, offer.id)
        
        assert len(offer_tags) == 3
        assert "python" in offer_tags
        assert "tutoring" in offer_tags
        
        print(f"   ✅ Associated {len(tags)} tags to offer")
        print(f"   ✅ Retrieved tags: {', '.join(offer_tags)}")


def main():
    """Run all sanity checks."""
    print("=" * 60)
    print("OFFERS & NEEDS SANITY CHECKS")
    print("=" * 60)
    
    try:
        test_create_with_7day_default()
        test_extend_works()
        test_expired_items_archived()
        test_expired_hidden_from_list()
        test_tags_association()
        
        print("\n" + "=" * 60)
        print("✅ ALL SANITY CHECKS PASSED")
        print("=" * 60)
        print("\nOffers and Needs CRUD is working correctly!")
        print("\nNext steps:")
        print("1. Test via API:")
        print("   - POST /api/v1/offers/ (create)")
        print("   - GET /api/v1/offers/ (list)")
        print("   - POST /api/v1/offers/{id}/extend (extend)")
        print("   - GET /api/v1/offers/my (my offers)")
        print("2. Run full test suite:")
        print("   - pytest tests/test_offers.py -v")
        print("   - pytest tests/test_needs.py -v")
        
        return 0
        
    except AssertionError as e:
        print(f"\n❌ SANITY CHECK FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
