#!/usr/bin/env python
"""Database initialization script for The Hive.

This script:
1. Creates all database tables from SQLModel models
2. Seeds basic data (1 user + 1 offer) for sanity checks
3. Validates foreign key constraints

SRS Requirements:
- Database schema from §3.5.1
- User starting balance: 5 hours (FR-7.1)
- Offer default expiration: 7 days
- Capacity default: 1
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import json
from datetime import datetime, timedelta
from sqlmodel import SQLModel, Session, select, func

from app.core.db import engine, check_db_connection

# Import all models to ensure they're registered with SQLModel
from app.models import (
    User,
    UserRole,
    Tag,
    Offer,
    OfferStatus,
    OfferTag,
    Need,
    NeedStatus,
    NeedTag,
    LedgerEntry,
    TransactionType,
    Comment,
    Participant,
    ParticipantStatus,
    ParticipantRole,
)


def create_tables():
    """Create all database tables."""
    print("Creating database tables...")
    SQLModel.metadata.create_all(engine)
    print("✅ All tables created successfully")


def drop_tables():
    """Drop all database tables."""
    print("Dropping all database tables...")
    SQLModel.metadata.drop_all(engine)
    print("✅ All tables dropped successfully")


def create_time_slots_json(slots_data):
    """Create time slots JSON string from structured data.
    
    Args:
        slots_data: List of dicts with 'date' and 'time_ranges' keys
                   Each time_range has 'start_time' and 'end_time'
    
    Returns:
        JSON string representation of time slots
    """
    return json.dumps(slots_data)


def seed_basic_data():
    """Seed database with comprehensive test data.
    
    Creates:
    - 10 test users with 5 hour starting balance each
    - 15 tags across various categories
    - 15 active offers with various configurations
    - 12 needs with various configurations
    - Comments on offers and needs
    - Participants/applications for handshake workflow
    """
    print("\nSeeding comprehensive test data...")
    
    with Session(engine) as session:
        # Check if data already exists
        existing_user = session.exec(select(User).where(User.username == "alice")).first()
        if existing_user:
            print("\n⚠️  Database already contains seed data. Skipping seed process.")
            print("   To reseed, drop and recreate the database first.")
            return
        
        # Create test users (FR-7.1: each starts with 5 hours)
        users_data = [
            {
                "email": "alice@example.com",
                "username": "alice",
                "full_name": "Alice Wonder",
                "description": "Software developer passionate about teaching Python and web development",
                "location_lat": 40.7128,
                "location_lon": -74.0060,
                "location_name": "New York, NY",
                "timezone": "America/New_York",
            },
            {
                "email": "bob@example.com",
                "username": "bob",
                "full_name": "Bob Builder",
                "description": "Carpenter with 15 years of experience. Love helping with home repairs!",
                "location_lat": 34.0522,
                "location_lon": -118.2437,
                "location_name": "Los Angeles, CA",
                "timezone": "America/Los_Angeles",
            },
            {
                "email": "carol@example.com",
                "username": "carol",
                "full_name": "Carol Singer",
                "description": "Music teacher and performer. Vocal coach for all levels.",
                "location_lat": 41.8781,
                "location_lon": -87.6298,
                "location_name": "Chicago, IL",
                "timezone": "America/Chicago",
            },
            {
                "email": "david@example.com",
                "username": "david",
                "full_name": "David Chef",
                "description": "Professional chef specializing in Italian cuisine. Cooking classes available!",
                "location_lat": 37.7749,
                "location_lon": -122.4194,
                "location_name": "San Francisco, CA",
                "timezone": "America/Los_Angeles",
            },
            {
                "email": "emma@example.com",
                "username": "emma",
                "full_name": "Emma Garden",
                "description": "Urban gardener and sustainability advocate. Let's grow together!",
                "location_lat": 47.6062,
                "location_lon": -122.3321,
                "location_name": "Seattle, WA",
                "timezone": "America/Los_Angeles",
            },
            {
                "email": "frank@example.com",
                "username": "frank",
                "full_name": "Frank Fit",
                "description": "Personal trainer and yoga instructor. Health is wealth!",
                "location_lat": 25.7617,
                "location_lon": -80.1918,
                "location_name": "Miami, FL",
                "timezone": "America/New_York",
            },
            {
                "email": "grace@example.com",
                "username": "grace",
                "full_name": "Grace Lang",
                "description": "Polyglot offering language tutoring in Spanish, French, and Mandarin",
                "location_lat": 42.3601,
                "location_lon": -71.0589,
                "location_name": "Boston, MA",
                "timezone": "America/New_York",
            },
            {
                "email": "henry@example.com",
                "username": "henry",
                "full_name": "Henry Tech",
                "description": "IT specialist helping seniors with technology. Patient and friendly!",
                "location_lat": 39.7392,
                "location_lon": -104.9903,
                "location_name": "Denver, CO",
                "timezone": "America/Denver",
            },
            {
                "email": "iris@example.com",
                "username": "iris",
                "full_name": "Iris Artist",
                "description": "Visual artist and art therapist. Let's create something beautiful!",
                "location_lat": 30.2672,
                "location_lon": -97.7431,
                "location_name": "Austin, TX",
                "timezone": "America/Chicago",
            },
            {
                "email": "jack@example.com",
                "username": "jack",
                "full_name": "Jack Wheels",
                "description": "Bike mechanic and cycling enthusiast. Free bike repairs for the community!",
                "location_lat": 45.5152,
                "location_lon": -122.6784,
                "location_name": "Portland, OR",
                "timezone": "America/Los_Angeles",
            },
        ]
        
        users = []
        for user_data in users_data:
            user = User(
                email=user_data["email"],
                username=user_data["username"],
                password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5oDWKZVzZVJ0G",  # password: "password123"
                full_name=user_data["full_name"],
                description=user_data["description"],
                role=UserRole.USER,
                balance=5.0,  # SRS: starting balance
                location_lat=user_data["location_lat"],
                location_lon=user_data["location_lon"],
                location_name=user_data["location_name"],
                timezone=user_data.get("timezone", "UTC"),
            )
            session.add(user)
            users.append(user)
        
        session.commit()
        
        # Create initial ledger entries for all users
        for user in users:
            session.refresh(user)
            ledger_entry = LedgerEntry(
                user_id=user.id,
                debit=0.0,
                credit=5.0,
                balance=5.0,
                transaction_type=TransactionType.INITIAL,
                description="Initial TimeBank balance",
            )
            session.add(ledger_entry)
            print(f"✅ Created user: {user.username} (ID: {user.id}, Balance: {user.balance}h)")
        
        session.commit()
        
        # Create tags across various categories
        tags_data = [
            {"name": "tutoring", "description": "Educational tutoring services"},
            {"name": "programming", "description": "Software development and coding help"},
            {"name": "carpentry", "description": "Woodworking and furniture repair"},
            {"name": "music", "description": "Music lessons and performances"},
            {"name": "cooking", "description": "Culinary skills and meal preparation"},
            {"name": "gardening", "description": "Plant care and landscaping"},
            {"name": "fitness", "description": "Exercise training and wellness"},
            {"name": "language", "description": "Foreign language instruction"},
            {"name": "tech-support", "description": "Computer and technology assistance"},
            {"name": "art", "description": "Visual arts and creative projects"},
            {"name": "bike-repair", "description": "Bicycle maintenance and repair"},
            {"name": "home-repair", "description": "General home maintenance"},
            {"name": "childcare", "description": "Babysitting and child supervision"},
            {"name": "pet-care", "description": "Pet sitting and animal care"},
            {"name": "transportation", "description": "Rides and delivery services"},
        ]
        
        tags = []
        for tag_data in tags_data:
            tag = Tag(
                name=tag_data["name"],
                description=tag_data["description"],
                usage_count=0,
            )
            session.add(tag)
            tags.append(tag)
        
        session.commit()
        for tag in tags:
            session.refresh(tag)
            print(f"✅ Created tag: {tag.name} (ID: {tag.id})")
        
        # Create offers with various configurations
        offers_data = [
            {
                "creator": users[0],  # alice
                "title": "Python Programming Tutoring",
                "description": "Offering help with Python basics, web development with Django/Flask, and data science libraries. Perfect for beginners!",
                "is_remote": True,
                "capacity": 3,
                "hours": 2.0,
                "tags": ["tutoring", "programming"],
                "time_slots": [
                    {
                        "date": (datetime.utcnow() + timedelta(days=2)).strftime("%Y-%m-%d"),
                        "time_ranges": [
                            {"start_time": "10:00", "end_time": "12:00"},
                            {"start_time": "14:00", "end_time": "16:00"}
                        ],
                        "timezone": "America/New_York"
                    },
                    {
                        "date": (datetime.utcnow() + timedelta(days=5)).strftime("%Y-%m-%d"),
                        "time_ranges": [
                            {"start_time": "09:00", "end_time": "11:00"}
                        ],
                        "timezone": "America/New_York"
                    }
                ]
            },
            {
                "creator": users[0],  # alice
                "title": "Web Development Workshop",
                "description": "Learn HTML, CSS, and JavaScript in a hands-on workshop format. Bring your laptop!",
                "is_remote": False,
                "capacity": 5,
                "hours": 4.0,
                "tags": ["tutoring", "programming"],
                "time_slots": [
                    {
                        "date": (datetime.utcnow() + timedelta(days=7)).strftime("%Y-%m-%d"),
                        "time_ranges": [
                            {"start_time": "13:00", "end_time": "17:00"}
                        ],
                        "timezone": "America/New_York"
                    }
                ]
            },
            {
                "creator": users[1],  # bob
                "title": "Furniture Assembly & Repair",
                "description": "Expert help with IKEA furniture, broken chairs, wobbly tables. I bring my own tools!",
                "is_remote": False,
                "capacity": 2,
                "hours": 2.0,
                "tags": ["carpentry", "home-repair"],
            },
            {
                "creator": users[1],  # bob
                "title": "Basic Carpentry Skills Workshop",
                "description": "Learn to use basic tools safely and build a simple wooden project to take home.",
                "is_remote": False,
                "capacity": 4,
                "hours": 3.0,
                "tags": ["carpentry", "tutoring"],
                "time_slots": [
                    {
                        "date": (datetime.utcnow() + timedelta(days=3)).strftime("%Y-%m-%d"),
                        "time_ranges": [
                            {"start_time": "10:00", "end_time": "13:00"}
                        ],
                        "timezone": "America/Los_Angeles"
                    },
                    {
                        "date": (datetime.utcnow() + timedelta(days=10)).strftime("%Y-%m-%d"),
                        "time_ranges": [
                            {"start_time": "10:00", "end_time": "13:00"}
                        ],
                        "timezone": "America/Los_Angeles"
                    }
                ]
            },
            {
                "creator": users[2],  # carol
                "title": "Vocal Coaching Sessions",
                "description": "One-on-one or small group vocal coaching. All styles welcome: pop, classical, jazz.",
                "is_remote": True,
                "capacity": 2,
                "hours": 1.0,
                "tags": ["music", "tutoring"],
                "time_slots": [
                    {
                        "date": (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d"),
                        "time_ranges": [
                            {"start_time": "15:00", "end_time": "16:00"},
                            {"start_time": "16:30", "end_time": "17:30"}
                        ],
                        "timezone": "America/Chicago"
                    },
                    {
                        "date": (datetime.utcnow() + timedelta(days=4)).strftime("%Y-%m-%d"),
                        "time_ranges": [
                            {"start_time": "15:00", "end_time": "16:00"},
                            {"start_time": "17:00", "end_time": "18:00"}
                        ],
                        "timezone": "America/Chicago"
                    }
                ]
            },
            {
                "creator": users[2],  # carol
                "title": "Community Choir - Join Us!",
                "description": "Weekly choir practice open to all. No experience necessary, just bring enthusiasm!",
                "is_remote": False,
                "capacity": 20,
                "hours": 2.0,
                "tags": ["music"],
            },
            {
                "creator": users[3],  # david
                "title": "Italian Cooking Class",
                "description": "Learn to make authentic pasta from scratch. Ingredients provided, bring containers for leftovers!",
                "is_remote": False,
                "capacity": 4,
                "hours": 3.0,
                "tags": ["cooking", "tutoring"],
            },
            {
                "creator": users[3],  # david
                "title": "Meal Prep for Busy People",
                "description": "I'll help you plan and prepare healthy meals for the week. Your kitchen or mine!",
                "is_remote": False,
                "capacity": 2,
                "hours": 2.5,
                "tags": ["cooking"],
            },
            {
                "creator": users[4],  # emma
                "title": "Urban Garden Setup Help",
                "description": "I'll help you start a balcony or backyard garden. Advice on containers, soil, and plant selection.",
                "is_remote": False,
                "capacity": 3,
                "hours": 2.0,
                "tags": ["gardening"],
            },
            {
                "creator": users[4],  # emma
                "title": "Composting Workshop",
                "description": "Learn how to compost at home and reduce kitchen waste. Small-space solutions included!",
                "is_remote": True,
                "capacity": 10,
                "hours": 1.5,
                "tags": ["gardening"],
            },
            {
                "creator": users[5],  # frank
                "title": "Personal Training Sessions",
                "description": "Customized workout plans and motivation. Meet at the park or your home gym.",
                "is_remote": False,
                "capacity": 3,
                "hours": 1.0,
                "tags": ["fitness"],
            },
            {
                "creator": users[5],  # frank
                "title": "Beginner Yoga Classes",
                "description": "Gentle yoga for flexibility and stress relief. Virtual or in-person options available.",
                "is_remote": True,
                "capacity": 8,
                "hours": 1.0,
                "tags": ["fitness"],
            },
            {
                "creator": users[6],  # grace
                "title": "Spanish Conversation Practice",
                "description": "Practice conversational Spanish with a native speaker. All levels welcome!",
                "is_remote": True,
                "capacity": 4,
                "hours": 1.0,
                "tags": ["language", "tutoring"],
            },
            {
                "creator": users[7],  # henry
                "title": "Tech Help for Seniors",
                "description": "Patient help with smartphones, tablets, email, video calls. I come to you!",
                "is_remote": False,
                "capacity": 2,
                "hours": 1.5,
                "tags": ["tech-support"],
            },
            {
                "creator": users[9],  # jack
                "title": "Free Bike Tune-Ups",
                "description": "Basic maintenance: brakes, gears, tire pressure, chain lubrication. Bring your bike!",
                "is_remote": False,
                "capacity": 5,
                "hours": 1.0,
                "tags": ["bike-repair"],
            },
        ]
        
        offers = []
        for offer_data in offers_data:
            creator = offer_data["creator"]
            
            # Convert time slots to JSON if present
            available_slots_json = None
            if "time_slots" in offer_data:
                available_slots_json = create_time_slots_json(offer_data["time_slots"])
            
            offer = Offer(
                creator_id=creator.id,
                title=offer_data["title"],
                description=offer_data["description"],
                is_remote=offer_data["is_remote"],
                location_lat=creator.location_lat if not offer_data["is_remote"] else None,
                location_lon=creator.location_lon if not offer_data["is_remote"] else None,
                location_name=creator.location_name if not offer_data["is_remote"] else None,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=14),  # 2 weeks
                capacity=offer_data["capacity"],
                hours=offer_data.get("hours", 1.0),
                accepted_count=0,
                status=OfferStatus.ACTIVE,
                available_slots=available_slots_json,
            )
            session.add(offer)
            offers.append((offer, offer_data["tags"]))
        
        session.commit()
        
        # Link offers to tags
        for offer, tag_names in offers:
            session.refresh(offer)
            slots_info = f", Time Slots: {len(json.loads(offer.available_slots))}" if offer.available_slots else ""
            print(f"✅ Created offer: {offer.title} (ID: {offer.id}, Capacity: {offer.capacity}{slots_info})")
            for tag_name in tag_names:
                tag = next((t for t in tags if t.name == tag_name), None)
                if tag:
                    offer_tag = OfferTag(offer_id=offer.id, tag_id=tag.id)
                    session.add(offer_tag)
                    tag.usage_count += 1
        
        session.commit()
        
        # Create needs
        needs_data = [
            {
                "creator": users[7],  # henry
                "title": "Help Moving Furniture",
                "description": "Need help moving a couch and bookshelf to my new apartment. Second floor, no elevator.",
                "is_remote": False,
                "capacity": 2,
                "hours": 3.0,
                "tags": ["home-repair", "transportation"],
                "time_slots": [
                    {
                        "date": (datetime.utcnow() + timedelta(days=6)).strftime("%Y-%m-%d"),
                        "time_ranges": [
                            {"start_time": "09:00", "end_time": "12:00"},
                            {"start_time": "13:00", "end_time": "16:00"}
                        ],
                        "timezone": "America/Denver"
                    }
                ]
            },
            {
                "creator": users[8],  # iris
                "title": "Website Design Help",
                "description": "Need someone to help design a portfolio website for my art. I have content ready!",
                "is_remote": True,
                "capacity": 1,
                "hours": 4.0,
                "tags": ["programming"],
                "time_slots": [
                    {
                        "date": (datetime.utcnow() + timedelta(days=2)).strftime("%Y-%m-%d"),
                        "time_ranges": [
                            {"start_time": "18:00", "end_time": "20:00"}
                        ],
                        "timezone": "America/Chicago"
                    },
                    {
                        "date": (datetime.utcnow() + timedelta(days=9)).strftime("%Y-%m-%d"),
                        "time_ranges": [
                            {"start_time": "18:00", "end_time": "20:00"}
                        ],
                        "timezone": "America/Chicago"
                    }
                ]
            },
            {
                "creator": users[9],  # jack
                "title": "Dog Walking Partner",
                "description": "Looking for someone to walk my energetic golden retriever 2-3 times per week.",
                "is_remote": False,
                "capacity": 1,
                "hours": 1.0,
                "tags": ["pet-care"],
                "time_slots": [
                    {
                        "date": (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d"),
                        "time_ranges": [
                            {"start_time": "07:00", "end_time": "08:00"},
                            {"start_time": "17:00", "end_time": "18:00"}
                        ],
                        "timezone": "America/Los_Angeles"
                    },
                    {
                        "date": (datetime.utcnow() + timedelta(days=3)).strftime("%Y-%m-%d"),
                        "time_ranges": [
                            {"start_time": "07:00", "end_time": "08:00"},
                            {"start_time": "17:00", "end_time": "18:00"}
                        ],
                        "timezone": "America/Los_Angeles"
                    }
                ]
            },
            {
                "creator": users[0],  # alice
                "title": "Guitar Lessons Needed",
                "description": "Beginner looking to learn acoustic guitar. Prefer in-person lessons.",
                "is_remote": False,
                "capacity": 1,
                "hours": 1.5,
                "tags": ["music", "tutoring"],
            },
            {
                "creator": users[1],  # bob
                "title": "Garden Design Consultation",
                "description": "Need advice on redesigning my backyard garden. What should I plant in shady areas?",
                "is_remote": False,
                "capacity": 1,
                "hours": 2.0,
                "tags": ["gardening"],
            },
            {
                "creator": users[3],  # david
                "title": "Spanish Language Partner",
                "description": "Looking for conversation practice in Spanish. I'm at intermediate level.",
                "is_remote": True,
                "capacity": 1,
                "hours": 1.0,
                "tags": ["language"],
            },
            {
                "creator": users[4],  # emma
                "title": "Yoga Partner Wanted",
                "description": "Looking for someone to practice yoga with in the park on weekends.",
                "is_remote": False,
                "capacity": 2,
                "hours": 1.0,
                "tags": ["fitness"],
                "time_slots": [
                    {
                        "date": (datetime.utcnow() + timedelta(days=5)).strftime("%Y-%m-%d"),
                        "time_ranges": [
                            {"start_time": "08:00", "end_time": "09:00"}
                        ],
                        "timezone": "America/Los_Angeles"
                    },
                    {
                        "date": (datetime.utcnow() + timedelta(days=12)).strftime("%Y-%m-%d"),
                        "time_ranges": [
                            {"start_time": "08:00", "end_time": "09:00"}
                        ],
                        "timezone": "America/Los_Angeles"
                    }
                ]
            },
            {
                "creator": users[5],  # frank
                "title": "Help with Resume Writing",
                "description": "Career change ahead! Need help updating my resume and cover letter.",
                "is_remote": True,
                "capacity": 1,
                "hours": 2.0,
                "tags": ["tutoring"],
            },
            {
                "creator": users[6],  # grace
                "title": "Photography Session",
                "description": "Need professional photos for my language tutoring website. Outdoor session preferred.",
                "is_remote": False,
                "capacity": 1,
                "hours": 2.0,
                "tags": ["art"],
            },
            {
                "creator": users[2],  # carol
                "title": "Piano Tuning Service",
                "description": "My upright piano hasn't been tuned in years. Looking for an expert!",
                "is_remote": False,
                "capacity": 1,
                "hours": 1.5,
                "tags": ["music"],
            },
            {
                "creator": users[8],  # iris
                "title": "Childcare for Art Classes",
                "description": "Need someone to watch my 5-year-old while I teach evening art classes, 2 hours/session.",
                "is_remote": False,
                "capacity": 1,
                "hours": 2.0,
                "tags": ["childcare"],
            },
            {
                "creator": users[7],  # henry
                "title": "Car Ride to Airport",
                "description": "Need a ride to the airport next week, early morning departure.",
                "is_remote": False,
                "capacity": 1,
                "hours": 1.0,
                "tags": ["transportation"],
            },
        ]
        
        needs = []
        for need_data in needs_data:
            creator = need_data["creator"]
            
            # Convert time slots to JSON if present
            available_slots_json = None
            if "time_slots" in need_data:
                available_slots_json = create_time_slots_json(need_data["time_slots"])
            
            need = Need(
                creator_id=creator.id,
                title=need_data["title"],
                description=need_data["description"],
                is_remote=need_data["is_remote"],
                location_lat=creator.location_lat if not need_data["is_remote"] else None,
                location_lon=creator.location_lon if not need_data["is_remote"] else None,
                location_name=creator.location_name if not need_data["is_remote"] else None,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=14),
                capacity=need_data["capacity"],
                hours=need_data.get("hours", 1.0),
                accepted_count=0,
                status=NeedStatus.ACTIVE,
                available_slots=available_slots_json,
            )
            session.add(need)
            needs.append((need, need_data["tags"]))
        
        session.commit()
        
        # Link needs to tags
        for need, tag_names in needs:
            session.refresh(need)
            slots_info = f", Time Slots: {len(json.loads(need.available_slots))}" if need.available_slots else ""
            print(f"✅ Created need: {need.title} (ID: {need.id}, Capacity: {need.capacity}{slots_info})")
            for tag_name in tag_names:
                tag = next((t for t in tags if t.name == tag_name), None)
                if tag:
                    need_tag = NeedTag(need_id=need.id, tag_id=tag.id)
                    session.add(need_tag)
                    tag.usage_count += 1
        
        session.commit()
        
        # Create participants/applications for some offers and needs
        # Alice applies to Bob's carpentry workshop (Alice is PROVIDER in Bob's offer)
        participant1 = Participant(
            user_id=users[0].id,
            offer_id=offers[3][0].id,  # Basic Carpentry Skills Workshop
            role=ParticipantRole.REQUESTER,  # Alice is requesting to learn
            status=ParticipantStatus.ACCEPTED,
            message="I'd love to learn basic carpentry! I'm free on weekends.",
            hours_contributed=2.0,
        )
        session.add(participant1)
        
        # Carol applies to David's cooking class
        participant2 = Participant(
            user_id=users[2].id,
            offer_id=offers[6][0].id,  # Italian Cooking Class
            role=ParticipantRole.REQUESTER,
            status=ParticipantStatus.PENDING,
            message="This sounds amazing! I love Italian food and want to learn the authentic way.",
        )
        session.add(participant2)
        
        # Frank applies to Emma's composting workshop
        participant3 = Participant(
            user_id=users[5].id,
            offer_id=offers[9][0].id,  # Composting Workshop
            role=ParticipantRole.REQUESTER,
            status=ParticipantStatus.ACCEPTED,
            message="Perfect timing! I've been wanting to start composting.",
            hours_contributed=1.5,
        )
        session.add(participant3)
        
        # Grace applies to Alice's Python tutoring
        participant4 = Participant(
            user_id=users[6].id,
            offer_id=offers[0][0].id,  # Python Programming Tutoring
            role=ParticipantRole.REQUESTER,
            status=ParticipantStatus.PENDING,
            message="I'm interested in learning Python for data analysis. Can we focus on pandas and matplotlib?",
        )
        session.add(participant4)
        
        # Bob applies to Henry's "Help Moving Furniture" need (Bob is PROVIDER)
        participant5 = Participant(
            user_id=users[1].id,
            need_id=needs[0][0].id,
            role=ParticipantRole.PROVIDER,
            status=ParticipantStatus.ACCEPTED,
            message="I can help with the move! I have experience and a dolly for heavy items.",
            hours_contributed=2.0,
        )
        session.add(participant5)
        
        # Alice applies to Iris's "Website Design Help" need (Alice is PROVIDER)
        participant6 = Participant(
            user_id=users[0].id,
            need_id=needs[1][0].id,
            role=ParticipantRole.PROVIDER,
            status=ParticipantStatus.PENDING,
            message="I'd be happy to help with your portfolio site! I have web dev experience.",
        )
        session.add(participant6)
        
        # Carol applies to Alice's "Guitar Lessons Needed" (Carol is PROVIDER)
        participant7 = Participant(
            user_id=users[2].id,
            need_id=needs[3][0].id,
            role=ParticipantRole.PROVIDER,
            status=ParticipantStatus.PENDING,
            message="I can teach you guitar! I've been playing for 10 years. Let's start with the basics.",
        )
        session.add(participant7)
        
        session.commit()
        print(f"✅ Created {7} participant applications")
        
        # Update accepted_count for offers and needs with accepted participants
        # Offer ID 4 (Basic Carpentry Skills Workshop) has 1 accepted participant
        offers[3][0].accepted_count = 1
        session.add(offers[3][0])
        
        # Offer ID 10 (Composting Workshop) has 1 accepted participant
        offers[9][0].accepted_count = 1
        session.add(offers[9][0])
        
        # Need ID 1 (Help Moving Furniture) has 1 accepted participant
        needs[0][0].accepted_count = 1
        session.add(needs[0][0])
        
        session.commit()
        print(f"✅ Updated accepted_count for items with accepted participants")
        
        # Create user-to-user comments/feedback on completed exchanges
        # These are only for completed participants (FR-10.1)
        # For simplicity, we'll create comments for the accepted participants
        
        # Bob (provider) gives feedback to Henry (requester) after moving furniture
        comment1 = Comment(
            from_user_id=users[1].id,  # bob
            to_user_id=users[7].id,  # henry
            content="Henry was very helpful with preparing for the move. Everything went smoothly!",
            participant_id=participant5.id,
            is_approved=True,
        )
        session.add(comment1)
        
        # Henry (requester) gives feedback to Bob (provider)
        comment2 = Comment(
            from_user_id=users[7].id,  # henry
            to_user_id=users[1].id,  # bob
            content="Bob was amazing! Very strong and efficient. Made the move stress-free. Highly recommend!",
            participant_id=participant5.id,
            is_approved=True,
        )
        session.add(comment2)
        
        # Alice gives feedback to Bob after carpentry workshop
        comment3 = Comment(
            from_user_id=users[0].id,  # alice
            to_user_id=users[1].id,  # bob
            content="Great teacher! Bob explained everything clearly and was very patient with beginners.",
            participant_id=participant1.id,
            is_approved=True,
        )
        session.add(comment3)
        
        # Frank gives feedback to Emma after composting workshop
        comment4 = Comment(
            from_user_id=users[5].id,  # frank
            to_user_id=users[4].id,  # emma
            content="Emma's composting workshop was fantastic! I learned so much and feel confident starting my own compost bin.",
            participant_id=participant3.id,
            is_approved=True,
        )
        session.add(comment4)
        
        session.commit()
        print(f"✅ Created {4} user feedback comments")
        
    print("\n✅ Comprehensive seed data created successfully")
    print(f"   - 10 users with unique profiles and locations")
    print(f"   - 15 tags across various service categories")
    print(f"   - 15 offers with remote and in-person options")
    print(f"   - 12 needs with diverse requirements")
    print(f"   - 7 participants/applications in various states")
    print(f"   - 4 user feedback comments on completed exchanges")


def validate_schema():
    """Perform validation of the schema and seeded data."""
    print("\nValidating schema and data...")
    
    with Session(engine) as session:
        # Check users
        users = session.exec(select(User)).all()
        if len(users) < 10:
            raise ValueError(f"❌ Expected at least 10 users, found {len(users)}")
        print(f"✅ Found {len(users)} users")
        
        # Check offers
        offers = session.exec(select(Offer)).all()
        if len(offers) < 15:
            raise ValueError(f"❌ Expected at least 15 offers, found {len(offers)}")
        print(f"✅ Found {len(offers)} offers")
        
        # Check needs
        needs = session.exec(select(Need)).all()
        if len(needs) < 12:
            raise ValueError(f"❌ Expected at least 12 needs, found {len(needs)}")
        print(f"✅ Found {len(needs)} needs")
        
        # Check tags
        tags = session.exec(select(Tag)).all()
        if len(tags) < 15:
            raise ValueError(f"❌ Expected at least 15 tags, found {len(tags)}")
        print(f"✅ Found {len(tags)} tags")
        
        # Check offer-tag associations
        offer_tags = session.exec(select(OfferTag)).all()
        if len(offer_tags) == 0:
            raise ValueError("❌ No offer-tag associations found")
        print(f"✅ Found {len(offer_tags)} offer-tag associations")
        
        # Check need-tag associations
        need_tags = session.exec(select(NeedTag)).all()
        if len(need_tags) == 0:
            raise ValueError("❌ No need-tag associations found")
        print(f"✅ Found {len(need_tags)} need-tag associations")
        
        # Check participants
        participants = session.exec(select(Participant)).all()
        if len(participants) < 7:
            raise ValueError(f"❌ Expected at least 7 participants, found {len(participants)}")
        print(f"✅ Found {len(participants)} participants/applications")
        
        # Check comments
        comments = session.exec(select(Comment)).all()
        if len(comments) < 4:
            raise ValueError(f"❌ Expected at least 4 comments, found {len(comments)}")
        print(f"✅ Found {len(comments)} user feedback comments")
        
        # Check ledger entries
        ledger_entries = session.exec(select(LedgerEntry)).all()
        if len(ledger_entries) < 10:
            raise ValueError(f"❌ Expected at least 10 ledger entries, found {len(ledger_entries)}")
        print(f"✅ Found {len(ledger_entries)} ledger entries")
        
        # Validate FK constraints by checking a few relationships
        alice = session.exec(select(User).where(User.username == "alice")).first()
        if not alice:
            raise ValueError("❌ User 'alice' not found")
        
        alice_offers = session.exec(select(Offer).where(Offer.creator_id == alice.id)).all()
        if len(alice_offers) == 0:
            raise ValueError("❌ No offers found for alice - FK constraint may be broken")
        
        # Check that comments are properly linked to users and participants
        comment_count = session.exec(select(func.count()).select_from(Comment)).one()
        if comment_count == 0:
            raise ValueError("❌ No comments found")
        
        # Verify all comments have valid user references
        for comment in comments:
            from_user = session.get(User, comment.from_user_id)
            to_user = session.get(User, comment.to_user_id)
            if not from_user or not to_user:
                raise ValueError(f"❌ Comment {comment.id} has invalid user references")
        
    print("✅ Schema validation passed - all FK constraints and data integrity checks valid")


def main():
    """Main initialization routine."""
    print("=" * 60)
    print("The Hive - Database Initialization")
    print("=" * 60)
    
    # Check for --reset flag
    reset_db = "--reset" in sys.argv or "--drop" in sys.argv
    
    # Check database connection
    print("\nChecking database connection...")
    if not check_db_connection():
        print("❌ Database connection failed")
        sys.exit(1)
    print("✅ Database connection successful")
    
    # Drop tables if reset flag is present
    if reset_db:
        print("\n⚠️  RESET FLAG DETECTED - Dropping all tables...")
        drop_tables()
    
    # Create tables
    create_tables()
    
    # Seed basic data
    seed_basic_data()
    
    # Validate schema
    validate_schema()
    
    print("\n" + "=" * 60)
    print("✅ Database initialization completed successfully!")
    print("=" * 60)
    print("\nYou can now start the application with:")
    print("  uv run uvicorn app.main:app --reload")
    print("\nTo reset and reseed the database, run:")
    print("  python scripts/init_db.py --reset")


if __name__ == "__main__":
    main()
