"""
Tests for ledger and exchange completion functionality.

Covers:
- FR-7.1: Double-entry bookkeeping
- FR-7.2: Balance updates on both sides
- FR-7.4: Reciprocity limit enforcement (10 hour max debt)
- FR-7.5: Audit trail for all transactions
- FR-7.6: Tracking hours contributed per participant
"""

import pytest
from fastapi import HTTPException
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool

from app.core.ledger import (
    RECIPROCITY_LIMIT,
    check_reciprocity_limit,
    complete_exchange,
    verify_balance_integrity,
)
from app.models.ledger import LedgerEntry, TransactionType, Transfer
from app.models.need import Need, NeedStatus
from app.models.offer import Offer, OfferStatus
from app.models.participant import Participant, ParticipantRole, ParticipantStatus
from app.models.user import User


@pytest.fixture(name="session")
def session_fixture():
    """Create a fresh in-memory database for each test."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture
def provider(session: Session) -> User:
    """Create a provider user."""
    user = User(
        email="provider@test.com",
        username="provider",
        password_hash="hashed",
        full_name="Provider User",
        balance=5.0,
        is_active=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def requester(session: Session) -> User:
    """Create a requester user."""
    user = User(
        email="requester@test.com",
        username="requester",
        password_hash="hashed",
        full_name="Requester User",
        balance=5.0,
        is_active=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def offer_with_accepted_participant(
    session: Session, provider: User, requester: User
) -> Participant:
    """Create an offer with an accepted participant.
    
    In this case:
    - requester creates the offer (wants the service)
    - provider accepts as participant (will provide the service)
    """
    offer = Offer(
        title="Test Service",
        description="Test service description",
        creator_id=requester.id,  # Requester wants the service
        capacity=1,
        accepted_count=1,
        status=OfferStatus.ACTIVE,
    )
    session.add(offer)
    session.commit()
    
    participant = Participant(
        user_id=provider.id,  # Provider will provide the service
        offer_id=offer.id,
        role=ParticipantRole.PROVIDER,
        hours_contributed=3.0,
        status=ParticipantStatus.ACCEPTED,
    )
    session.add(participant)
    session.commit()
    session.refresh(participant)
    return participant


@pytest.fixture
def need_with_accepted_participant(
    session: Session, provider: User, requester: User
) -> Participant:
    """Create a need with an accepted participant."""
    need = Need(
        title="Test Need",
        description="Test need description",
        creator_id=requester.id,
        capacity=1,
        accepted_count=1,
        status=NeedStatus.ACTIVE,
    )
    session.add(need)
    session.commit()
    
    participant = Participant(
        user_id=provider.id,
        need_id=need.id,
        role=ParticipantRole.PROVIDER,
        hours_contributed=2.5,
        status=ParticipantStatus.ACCEPTED,
    )
    session.add(participant)
    session.commit()
    session.refresh(participant)
    return participant


def test_complete_exchange_offer_double_entry_bookkeeping(
    session: Session,
    provider: User,
    requester: User,
    offer_with_accepted_participant: Participant,
):
    """
    Test FR-7.1: Double-entry bookkeeping with mutual confirmation.
    
    Both provider and requester must confirm completion.
    Provider should get CREDIT entry (earning hours).
    Requester should get DEBIT entry (spending hours).
    """
    participant = offer_with_accepted_participant
    hours = participant.hours_contributed
    
    # First confirmation (provider) - should return None (waiting for other party)
    result = complete_exchange(session, participant.id, provider.id)
    assert result == (None, None, None)
    
    # Verify provider_confirmed is set
    session.refresh(participant)
    assert participant.provider_confirmed is True
    assert participant.requester_confirmed is False
    
    # Second confirmation (requester) - should complete the exchange
    provider_entry, requester_entry, transfer = complete_exchange(
        session, participant.id, requester.id
    )
    
    # Provider gets CREDIT (earning)
    assert provider_entry.user_id == provider.id
    assert provider_entry.credit == hours
    assert provider_entry.debit == 0.0
    assert provider_entry.transaction_type == TransactionType.EXCHANGE
    assert "Provided service" in provider_entry.description
    
    # Requester gets DEBIT (spending)
    assert requester_entry.user_id == requester.id
    assert requester_entry.debit == hours
    assert requester_entry.credit == 0.0
    assert requester_entry.transaction_type == TransactionType.EXCHANGE
    assert "Received service" in requester_entry.description
    
    # Both entries reference the same participant
    assert provider_entry.participant_id == participant.id
    assert requester_entry.participant_id == participant.id


def test_complete_exchange_need_double_entry_bookkeeping(
    session: Session,
    provider: User,
    requester: User,
    need_with_accepted_participant: Participant,
):
    """Test double-entry bookkeeping for Need completion with mutual confirmation."""
    participant = need_with_accepted_participant
    hours = participant.hours_contributed
    
    # First confirmation (provider) - should return None
    result = complete_exchange(session, participant.id, provider.id)
    assert result == (None, None, None)
    
    # Second confirmation (requester) - should complete
    provider_entry, requester_entry, transfer = complete_exchange(
        session, participant.id, requester.id
    )
    
    # Provider gets CREDIT (earning)
    assert provider_entry.user_id == provider.id
    assert provider_entry.credit == hours
    assert provider_entry.debit == 0.0
    
    # Requester gets DEBIT (spending)
    assert requester_entry.user_id == requester.id
    assert requester_entry.debit == hours
    assert requester_entry.credit == 0.0


def test_complete_exchange_balance_updates(
    session: Session,
    provider: User,
    requester: User,
    offer_with_accepted_participant: Participant,
):
    """
    Test FR-7.2: Balance updates on both sides with mutual confirmation.
    
    Provider balance should increase by hours.
    Requester balance should decrease by hours.
    """
    participant = offer_with_accepted_participant
    hours = participant.hours_contributed
    
    initial_provider_balance = provider.balance
    initial_requester_balance = requester.balance
    
    # First confirmation - no balance changes yet
    complete_exchange(session, participant.id, provider.id)
    session.refresh(provider)
    session.refresh(requester)
    assert provider.balance == initial_provider_balance
    assert requester.balance == initial_requester_balance
    
    # Second confirmation - balance updates happen
    complete_exchange(session, participant.id, requester.id)
    
    # Refresh to get updated balances
    session.refresh(provider)
    session.refresh(requester)
    
    # Provider balance increased
    assert provider.balance == initial_provider_balance + hours
    
    # Requester balance decreased
    assert requester.balance == initial_requester_balance - hours


def test_complete_exchange_creates_transfer_record(
    session: Session,
    provider: User,
    requester: User,
    offer_with_accepted_participant: Participant,
):
    """
    Test FR-7.5: Audit trail via Transfer record with mutual confirmation.
    
    Every exchange should create a Transfer record linking
    sender and receiver with amount and notes.
    """
    participant = offer_with_accepted_participant
    hours = participant.hours_contributed
    
    # First confirmation - no transfer yet
    result = complete_exchange(session, participant.id, provider.id)
    assert result == (None, None, None)
    
    # Second confirmation - transfer created
    _, _, transfer = complete_exchange(session, participant.id, requester.id)
    
    # Transfer record created
    assert transfer.id is not None
    assert transfer.sender_id == requester.id
    assert transfer.receiver_id == provider.id
    assert transfer.amount == hours
    assert transfer.transaction_type == TransactionType.EXCHANGE
    assert transfer.participant_id == participant.id
    assert "Exchange completed" in transfer.notes
    
    # Transfer persisted to database
    db_transfer = session.get(Transfer, transfer.id)
    assert db_transfer is not None
    assert db_transfer.sender_id == requester.id


def test_complete_exchange_marks_participant_completed(
    session: Session,
    provider: User,
    requester: User,
    offer_with_accepted_participant: Participant,
):
    """
    Test FR-7.6: Participant status updated to COMPLETED after mutual confirmation.
    """
    participant = offer_with_accepted_participant
    assert participant.status == ParticipantStatus.ACCEPTED
    
    # First confirmation - status still ACCEPTED
    complete_exchange(session, participant.id, provider.id)
    session.refresh(participant)
    assert participant.status == ParticipantStatus.ACCEPTED
    assert participant.provider_confirmed is True
    assert participant.requester_confirmed is False
    
    # Second confirmation - status changes to COMPLETED
    complete_exchange(session, participant.id, requester.id)
    session.refresh(participant)
    
    assert participant.status == ParticipantStatus.COMPLETED
    assert participant.provider_confirmed is True
    assert participant.requester_confirmed is True
    assert participant.updated_at is not None


def test_complete_exchange_partial_confirmation(
    session: Session,
    provider: User,
    requester: User,
    offer_with_accepted_participant: Participant,
):
    """
    Test that partial confirmation doesn't create ledger entries.
    
    Only one party confirming should NOT:
    - Create ledger entries
    - Update balances
    - Change status to COMPLETED
    
    But it SHOULD:
    - Record the confirmation flag
    - Keep status as ACCEPTED
    """
    participant = offer_with_accepted_participant
    initial_provider_balance = provider.balance
    initial_requester_balance = requester.balance
    
    # First confirmation - provider confirms
    result = complete_exchange(session, participant.id, provider.id)
    
    # Should return None indicating partial confirmation
    assert result == (None, None, None)
    
    # Refresh participant to get updated fields
    session.refresh(participant)
    
    # Provider should be confirmed, requester not yet
    assert participant.provider_confirmed is True
    assert participant.requester_confirmed is False
    
    # Status should still be ACCEPTED (not COMPLETED)
    assert participant.status == ParticipantStatus.ACCEPTED
    
    # Balances should NOT have changed
    session.refresh(provider)
    session.refresh(requester)
    assert provider.balance == initial_provider_balance
    assert requester.balance == initial_requester_balance
    
    # No ledger entries should exist yet
    statement = select(LedgerEntry).where(
        LedgerEntry.participant_id == participant.id
    )
    entries = session.exec(statement).all()
    assert len(entries) == 0


def test_complete_exchange_ledger_audit_trail(
    session: Session,
    provider: User,
    requester: User,
    offer_with_accepted_participant: Participant,
):
    """
    Test FR-7.5: Ledger entries provide complete audit trail.
    
    Both ledger entries should be persisted and queryable.
    """
    participant = offer_with_accepted_participant
    
    # Both parties must confirm
    complete_exchange(session, participant.id, provider.id)
    complete_exchange(session, participant.id, requester.id)
    
    # Query all ledger entries
    statement = select(LedgerEntry).where(
        LedgerEntry.participant_id == participant.id
    )
    entries = session.exec(statement).all()
    
    # Should have exactly 2 entries (provider credit + requester debit)
    assert len(entries) == 2
    
    # One credit, one debit
    credits = [e for e in entries if e.credit > 0]
    debits = [e for e in entries if e.debit > 0]
    
    assert len(credits) == 1
    assert len(debits) == 1
    assert credits[0].user_id == provider.id
    assert debits[0].user_id == requester.id


def test_complete_exchange_only_accepted_status(
    session: Session,
    provider: User,
    requester: User,
):
    """Test that only ACCEPTED participants can be completed."""
    # Create participant with PENDING status
    offer = Offer(
        title="Test Service",
        description="Test",
        creator_id=requester.id,  # Requester wants the service
        capacity=1,
        accepted_count=0,
        status=OfferStatus.ACTIVE,
    )
    session.add(offer)
    session.commit()
    
    participant = Participant(
        user_id=provider.id,  # Provider will provide
        offer_id=offer.id,
        role=ParticipantRole.PROVIDER,
        hours_contributed=2.0,
        status=ParticipantStatus.PENDING,
    )
    session.add(participant)
    session.commit()
    
    # Should raise error for non-ACCEPTED status
    with pytest.raises(HTTPException) as exc_info:
        complete_exchange(session, participant.id, provider.id)
    
    assert exc_info.value.status_code == 400
    assert "accepted" in exc_info.value.detail.lower()


def test_check_reciprocity_limit_allows_positive_balance(session: Session, requester: User):
    """Test that users with positive balance can always spend."""
    # User has 5.0 balance, wants to spend 3.0
    can_proceed, message = check_reciprocity_limit(session, requester.id, 3.0)
    
    assert can_proceed is True
    assert message == ""


def test_check_reciprocity_limit_allows_within_limit(session: Session, requester: User):
    """Test that users can go into debt up to the limit."""
    # Set balance to 0
    requester.balance = 0.0
    session.add(requester)
    session.commit()
    
    # Try to spend 5.0 hours (within 10 hour limit)
    can_proceed, message = check_reciprocity_limit(session, requester.id, 5.0)
    
    assert can_proceed is True
    assert message == ""


def test_check_reciprocity_limit_warns_at_80_percent(session: Session, requester: User):
    """
    Test FR-7.4: Warn when approaching reciprocity limit.
    
    Should warn when user would exceed 80% of limit (8 hours debt).
    """
    # Set balance to -7.0 (already 7 hours in debt)
    requester.balance = -7.0
    session.add(requester)
    session.commit()
    
    # Try to spend 2.0 more hours (would go to -9.0, within limit but > 80%)
    can_proceed, message = check_reciprocity_limit(session, requester.id, 2.0)
    
    assert can_proceed is True
    assert "warning" in message.lower()
    assert "reciprocity limit" in message.lower()


def test_check_reciprocity_limit_blocks_at_limit(session: Session, requester: User):
    """
    Test FR-7.4: Block when exceeding reciprocity limit.
    
    Users cannot go more than 10 hours into debt.
    """
    # Set balance to -5.0 (5 hours in debt)
    requester.balance = -5.0
    session.add(requester)
    session.commit()
    
    # Try to spend 6.0 more hours (would go to -11.0, exceeding limit)
    can_proceed, message = check_reciprocity_limit(session, requester.id, 6.0)
    
    assert can_proceed is False
    assert "reciprocity limit" in message.lower()
    assert str(RECIPROCITY_LIMIT) in message


def test_check_reciprocity_limit_blocks_exactly_at_limit(session: Session, requester: User):
    """Test that exactly hitting the limit is blocked."""
    # Set balance to -10.0 (exactly at limit)
    requester.balance = -10.0
    session.add(requester)
    session.commit()
    
    # Try to spend 0.1 more hours
    can_proceed, message = check_reciprocity_limit(session, requester.id, 0.1)
    
    assert can_proceed is False


def test_verify_balance_integrity_valid(
    session: Session,
    provider: User,
    requester: User,
    offer_with_accepted_participant: Participant,
):
    """Test balance integrity verification for valid state."""
    # Complete an exchange (both parties confirm)
    complete_exchange(session, offer_with_accepted_participant.id, provider.id)
    complete_exchange(session, offer_with_accepted_participant.id, requester.id)
    
    # Verify both users' balance integrity
    is_valid_provider, msg_provider = verify_balance_integrity(session, provider.id)
    is_valid_requester, msg_requester = verify_balance_integrity(session, requester.id)
    
    assert is_valid_provider is True
    assert "correct" in msg_provider.lower()
    
    assert is_valid_requester is True
    assert "correct" in msg_requester.lower()


def test_verify_balance_integrity_detects_mismatch(session: Session, provider: User):
    """Test that balance integrity check detects discrepancies."""
    # Manually create a ledger entry without updating balance
    entry = LedgerEntry(
        user_id=provider.id,
        credit=5.0,
        debit=0.0,
        balance=provider.balance,  # Wrong - should be provider.balance + 5.0
        transaction_type=TransactionType.INITIAL,
        description="Test entry",
    )
    session.add(entry)
    session.commit()
    
    # Now manually change balance to create mismatch
    provider.balance = 0.0
    session.add(provider)
    session.commit()
    
    # Verify should detect the mismatch
    is_valid, message = verify_balance_integrity(session, provider.id)
    
    assert is_valid is False
    assert "mismatch" in message.lower()


def test_complete_exchange_prevents_concurrent_completion(
    session: Session,
    provider: User,
    requester: User,
    offer_with_accepted_participant: Participant,
):
    """
    Test that completing the same exchange twice fails gracefully.
    
    After both parties confirm, trying to complete again should fail
    because status is already COMPLETED.
    """
    participant = offer_with_accepted_participant
    
    # Both parties confirm (mutual confirmation)
    complete_exchange(session, participant.id, provider.id)
    complete_exchange(session, participant.id, requester.id)
    
    # Try to complete again - should fail as already completed
    with pytest.raises(HTTPException) as exc_info:
        complete_exchange(session, participant.id, provider.id)
    
    assert exc_info.value.status_code == 400
    assert "accepted" in exc_info.value.detail.lower() or "completed" in exc_info.value.detail.lower()


def test_complete_exchange_multiple_exchanges_cumulative_balance(
    session: Session,
    provider: User,
    requester: User,
):
    """
    Test that multiple exchanges correctly accumulate balances.
    """
    initial_provider_balance = provider.balance
    initial_requester_balance = requester.balance
    
    total_hours = 0.0
    
    # Complete 3 different exchanges
    for i in range(3):
        hours = float(i + 1)  # 1.0, 2.0, 3.0 hours
        total_hours += hours
        
        offer = Offer(
            title=f"Service {i}",
            description="Test",
            creator_id=requester.id,  # Requester wants service
            capacity=1,
            accepted_count=1,
            status=OfferStatus.ACTIVE,
        )
        session.add(offer)
        session.commit()
        
        participant = Participant(
            user_id=provider.id,  # Provider provides service
            offer_id=offer.id,
            role=ParticipantRole.PROVIDER,
            hours_contributed=hours,
            status=ParticipantStatus.ACCEPTED,
        )
        session.add(participant)
        session.commit()
        
        # Both parties confirm (mutual confirmation)
        complete_exchange(session, participant.id, provider.id)
        complete_exchange(session, participant.id, requester.id)
    
    # Refresh to get final balances
    session.refresh(provider)
    session.refresh(requester)
    
    # Provider earned total_hours
    assert provider.balance == pytest.approx(initial_provider_balance + total_hours)
    
    # Requester spent total_hours
    assert requester.balance == pytest.approx(initial_requester_balance - total_hours)


def test_ledger_history_endpoint_integration(
    session: Session,
    provider: User,
    requester: User,
    offer_with_accepted_participant: Participant,
):
    """
    Test that ledger entries can be retrieved for audit trail (FR-7.5).
    
    This tests the get_user_ledger function used by /me/ledger endpoint.
    """
    from app.core.ledger import get_user_ledger
    
    # Complete an exchange (both parties confirm)
    complete_exchange(session, offer_with_accepted_participant.id, provider.id)
    complete_exchange(session, offer_with_accepted_participant.id, requester.id)
    
    # Get provider's ledger history
    entries, total = get_user_ledger(session, provider.id, skip=0, limit=10)
    
    # Provider should have entries (at least the exchange credit)
    assert len(entries) >= 1
    assert total >= 1
    
    # Most recent entry should be the exchange
    latest_entry = entries[0]  # Ordered by created_at desc
    assert latest_entry.user_id == provider.id
    assert latest_entry.credit > 0
    assert latest_entry.transaction_type == TransactionType.EXCHANGE


def test_ledger_pagination(
    session: Session,
    provider: User,
    requester: User,
):
    """Test that ledger pagination works correctly."""
    from app.core.ledger import get_user_ledger
    
    # Create multiple exchanges (5 total)
    for i in range(5):
        offer = Offer(
            title=f"Service {i}",
            description="Test",
            creator_id=requester.id,  # Requester wants service
            capacity=1,
            accepted_count=1,
            status=OfferStatus.ACTIVE,
        )
        session.add(offer)
        session.commit()
        
        participant = Participant(
            user_id=provider.id,  # Provider provides service
            offer_id=offer.id,
            role=ParticipantRole.PROVIDER,
            hours_contributed=1.0,
            status=ParticipantStatus.ACCEPTED,
        )
        session.add(participant)
        session.commit()
        
        # Both parties confirm (mutual confirmation)
        complete_exchange(session, participant.id, provider.id)
        complete_exchange(session, participant.id, requester.id)
    
    # Get first page (limit 3)
    entries_page1, total = get_user_ledger(session, provider.id, skip=0, limit=3)
    assert len(entries_page1) == 3
    assert total == 5
    
    # Get second page (limit 3, skip 3)
    entries_page2, _ = get_user_ledger(session, provider.id, skip=3, limit=3)
    assert len(entries_page2) == 2  # Only 2 remaining
    
    # Entries should be different
    page1_ids = {e.id for e in entries_page1}
    page2_ids = {e.id for e in entries_page2}
    assert page1_ids.isdisjoint(page2_ids)
