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
    Participant,
    ParticipantStatus,
    ParticipantRole,
)
from app.models.user import UserTag
from app.models.rating import Rating, RatingVisibility
from app.models.forum import ForumTopic, ForumComment, ForumTopicTag, TopicType


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
    - Participants/applications for handshake workflow
    - Ratings for completed exchanges
    """
    print("\nSeeding comprehensive test data...")
    
    with Session(engine) as session:
        # Check if data already exists
        existing_user = session.exec(select(User).where(User.username == "alice")).first()
        if existing_user:
            print("\n⚠️  Database already contains seed data. Skipping seed process.")
            print("   To reseed, drop and recreate the database first.")
            return
        
        # Create moderator user first (with role=MODERATOR)
        from app.core.security import get_password_hash
        moderator = User(
            email="moderator@thehive.com",
            username="moderator",
            password_hash=get_password_hash("ModeratorPass123!"),
            full_name="System Moderator",
            description="Platform moderator responsible for content review and user safety",
            role=UserRole.MODERATOR,
            balance=5.0,
            location_lat=41.0082,
            location_lon=28.9784,
            location_name="İstanbul, Turkey",
            profile_image="owl",
            profile_image_type="preset",
        )
        session.add(moderator)
        session.commit()
        session.refresh(moderator)
        
        # Create initial ledger entry for moderator
        moderator_ledger = LedgerEntry(
            user_id=moderator.id,
            debit=0.0,
            credit=5.0,
            balance=5.0,
            transaction_type=TransactionType.INITIAL,
            description="Initial TimeBank balance",
        )
        session.add(moderator_ledger)
        session.commit()
        
        print(f"✅ Created MODERATOR: {moderator.username} (ID: {moderator.id}, Role: {moderator.role})")
        print(f"   📧 Email: moderator@thehive.com")
        print(f"   🔑 Password: ModeratorPass123!")
        print()
        
        # Create test users (FR-7.1: each starts with 5 hours)
        # All users are located in various neighborhoods of Istanbul, Turkey
        # Each user has a preset avatar and profile tags
        users_data = [
            {
                "email": "alice@example.com",
                "username": "alice",
                "full_name": "Ayşe Yılmaz",
                "description": "Software developer passionate about teaching Python and web development",
                "location_lat": 41.0082,
                "location_lon": 28.9784,
                "location_name": "Beyoğlu, İstanbul",
                "profile_image": "butterfly",
                "profile_image_type": "preset",
                "tags": ["programming", "web development", "python", "teaching"],
            },
            {
                "email": "bob@example.com",
                "username": "bob",
                "full_name": "Burak Demir",
                "description": "Carpenter with 15 years of experience. Love helping with home repairs!",
                "location_lat": 41.0136,
                "location_lon": 28.9550,
                "location_name": "Fatih, İstanbul",
                "profile_image": "bear",
                "profile_image_type": "preset",
                "tags": ["carpentry", "home repair", "woodworking", "furniture"],
            },
            {
                "email": "carol@example.com",
                "username": "carol",
                "full_name": "Ceren Kaya",
                "description": "Music teacher and performer. Vocal coach for all levels.",
                "location_lat": 41.0422,
                "location_lon": 29.0083,
                "location_name": "Beşiktaş, İstanbul",
                "profile_image": "bird",
                "profile_image_type": "preset",
                "tags": ["music", "singing", "vocal coaching", "performance"],
            },
            {
                "email": "david@example.com",
                "username": "david",
                "full_name": "Deniz Çelik",
                "description": "Professional chef specializing in Turkish cuisine. Cooking classes available!",
                "location_lat": 40.9923,
                "location_lon": 29.0230,
                "location_name": "Kadıköy, İstanbul",
                "profile_image": "mushroom",
                "profile_image_type": "preset",
                "tags": ["cooking", "turkish cuisine", "chef", "meal prep"],
            },
            {
                "email": "emma@example.com",
                "username": "emma",
                "full_name": "Elif Arslan",
                "description": "Urban gardener and sustainability advocate. Let's grow together!",
                "location_lat": 41.0766,
                "location_lon": 29.0310,
                "location_name": "Sarıyer, İstanbul",
                "profile_image": "sunflower",
                "profile_image_type": "preset",
                "tags": ["gardening", "sustainability", "composting", "plants"],
            },
            {
                "email": "frank@example.com",
                "username": "frank",
                "full_name": "Fatih Öztürk",
                "description": "Personal trainer and yoga instructor. Health is wealth!",
                "location_lat": 40.9632,
                "location_lon": 29.1009,
                "location_name": "Maltepe, İstanbul",
                "profile_image": "fox",
                "profile_image_type": "preset",
                "tags": ["fitness", "yoga", "personal training", "wellness"],
            },
            {
                "email": "grace@example.com",
                "username": "grace",
                "full_name": "Gül Şahin",
                "description": "Polyglot offering language tutoring in English, German, and French",
                "location_lat": 41.0553,
                "location_lon": 29.0094,
                "location_name": "Şişli, İstanbul",
                "profile_image": "owl",
                "profile_image_type": "preset",
                "tags": ["languages", "english", "german", "french", "tutoring"],
            },
            {
                "email": "henry@example.com",
                "username": "henry",
                "full_name": "Hakan Yıldız",
                "description": "IT specialist helping seniors with technology. Patient and friendly!",
                "location_lat": 41.1087,
                "location_lon": 29.0259,
                "location_name": "Beykoz, İstanbul",
                "profile_image": "turtle",
                "profile_image_type": "preset",
                "tags": ["tech support", "computers", "seniors", "patience"],
            },
            {
                "email": "iris@example.com",
                "username": "iris",
                "full_name": "İrem Aydın",
                "description": "Visual artist and art therapist. Let's create something beautiful!",
                "location_lat": 40.9828,
                "location_lon": 29.0553,
                "location_name": "Üsküdar, İstanbul",
                "profile_image": "flower",
                "profile_image_type": "preset",
                "tags": ["art", "painting", "art therapy", "creativity"],
            },
            {
                "email": "jack@example.com",
                "username": "jack",
                "full_name": "Cem Koç",
                "description": "Bike mechanic and cycling enthusiast. Free bike repairs for the community!",
                "location_lat": 41.0297,
                "location_lon": 28.8890,
                "location_name": "Bakırköy, İstanbul",
                "profile_image": "bee",
                "profile_image_type": "preset",
                "tags": ["bike repair", "cycling", "mechanics", "community"],
            },
        ]
        
        users = []
        users_with_tags = []
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
                profile_image=user_data.get("profile_image"),
                profile_image_type=user_data.get("profile_image_type", "preset"),
            )
            session.add(user)
            users.append(user)
            users_with_tags.append((user, user_data.get("tags", [])))
        
        session.commit()
        
        # Create initial ledger entries and user tags for all users
        for user, user_tags in users_with_tags:
            session.refresh(user)
            
            # Create initial ledger entry
            ledger_entry = LedgerEntry(
                user_id=user.id,
                debit=0.0,
                credit=5.0,
                balance=5.0,
                transaction_type=TransactionType.INITIAL,
                description="Initial TimeBank balance",
            )
            session.add(ledger_entry)
            
            # Create user profile tags
            for tag_name in user_tags:
                user_tag = UserTag(user_id=user.id, tag_name=tag_name.lower())
                session.add(user_tag)
            
            print(f"✅ Created user: {user.username} (ID: {user.id}, Balance: {user.balance}h, Avatar: {user.profile_image}, Tags: {len(user_tags)})")
        
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
                    },
                    {
                        "date": (datetime.utcnow() + timedelta(days=5)).strftime("%Y-%m-%d"),
                        "time_ranges": [
                            {"start_time": "09:00", "end_time": "11:00"}
                        ],
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
                    },
                    {
                        "date": (datetime.utcnow() + timedelta(days=10)).strftime("%Y-%m-%d"),
                        "time_ranges": [
                            {"start_time": "10:00", "end_time": "13:00"}
                        ],
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
                    },
                    {
                        "date": (datetime.utcnow() + timedelta(days=4)).strftime("%Y-%m-%d"),
                        "time_ranges": [
                            {"start_time": "15:00", "end_time": "16:00"},
                            {"start_time": "17:00", "end_time": "18:00"}
                        ],
                    }
                ]
            },
            {
                "creator": users[2],  # carol
                "title": "Community Choir - Join Us!",
                "description": "Weekly choir practice open to all. No experience necessary, just bring enthusiasm!",
                "is_remote": False,
                "capacity": 5,
                "hours": 2.0,
                "tags": ["music"],
            },
            {
                "creator": users[3],  # david
                "title": "Turkish Cooking Class",
                "description": "Learn to make authentic Turkish dishes like mantı and börek from scratch. Ingredients provided, bring containers for leftovers!",
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
                "hours": 3.0,
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
                "capacity": 5,
                "hours": 2.0,
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
                "capacity": 5,
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
                "hours": 2.0,
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
                    },
                    {
                        "date": (datetime.utcnow() + timedelta(days=9)).strftime("%Y-%m-%d"),
                        "time_ranges": [
                            {"start_time": "18:00", "end_time": "20:00"}
                        ],
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
                    },
                    {
                        "date": (datetime.utcnow() + timedelta(days=3)).strftime("%Y-%m-%d"),
                        "time_ranges": [
                            {"start_time": "07:00", "end_time": "08:00"},
                            {"start_time": "17:00", "end_time": "18:00"}
                        ],
                    }
                ]
            },
            {
                "creator": users[0],  # alice
                "title": "Guitar Lessons Needed",
                "description": "Beginner looking to learn acoustic guitar. Prefer in-person lessons.",
                "is_remote": False,
                "capacity": 1,
                "hours": 2.0,
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
                    },
                    {
                        "date": (datetime.utcnow() + timedelta(days=12)).strftime("%Y-%m-%d"),
                        "time_ranges": [
                            {"start_time": "08:00", "end_time": "09:00"}
                        ],
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
                "hours": 2.0,
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
        
        # =================================================================
        # Create participants/applications for some offers and needs
        # =================================================================
        
        # ===== COMPLETED EXCHANGES (with ratings and ledger entries) =====
        
        # 1. Alice completed Bob's carpentry workshop (Alice REQUESTER, Bob PROVIDER)
        # Bob offered to teach carpentry, Alice learned from him
        participant1 = Participant(
            user_id=users[0].id,  # Alice
            offer_id=offers[3][0].id,  # Basic Carpentry Skills Workshop (Bob's offer)
            role=ParticipantRole.REQUESTER,  # Alice is requesting to learn
            status=ParticipantStatus.COMPLETED,
            message="I'd love to learn basic carpentry! I'm free on weekends.",
            hours_contributed=2.0,
            provider_confirmed=True,
            requester_confirmed=True,
        )
        session.add(participant1)
        
        # 2. Frank completed Emma's composting workshop (Frank REQUESTER, Emma PROVIDER)
        participant3 = Participant(
            user_id=users[5].id,  # Frank
            offer_id=offers[9][0].id,  # Composting Workshop (Emma's offer)
            role=ParticipantRole.REQUESTER,
            status=ParticipantStatus.COMPLETED,
            message="Perfect timing! I've been wanting to start composting.",
            hours_contributed=1.5,
            provider_confirmed=True,
            requester_confirmed=True,
        )
        session.add(participant3)
        
        # 3. Bob helped Henry move furniture (Bob PROVIDER, Henry REQUESTER)
        participant5 = Participant(
            user_id=users[1].id,  # Bob
            need_id=needs[0][0].id,  # Help Moving Furniture (Henry's need)
            role=ParticipantRole.PROVIDER,
            status=ParticipantStatus.COMPLETED,
            message="I can help with the move! I have experience and a dolly for heavy items.",
            hours_contributed=3.0,
            provider_confirmed=True,
            requester_confirmed=True,
        )
        session.add(participant5)
        
        # 4. Carol learned Spanish from Grace (Carol REQUESTER, Grace PROVIDER)
        # Carol completed Grace's Spanish Conversation Practice offer
        participant_spanish = Participant(
            user_id=users[2].id,  # Carol
            offer_id=offers[12][0].id,  # Spanish Conversation Practice (Grace's offer)
            role=ParticipantRole.REQUESTER,
            status=ParticipantStatus.COMPLETED,
            message="I'd love to improve my Spanish conversation skills!",
            hours_contributed=1.0,
            provider_confirmed=True,
            requester_confirmed=True,
        )
        session.add(participant_spanish)
        
        # 5. Alice helped Iris with website design (Alice PROVIDER, Iris REQUESTER)
        participant_web = Participant(
            user_id=users[0].id,  # Alice
            need_id=needs[1][0].id,  # Website Design Help (Iris's need)
            role=ParticipantRole.PROVIDER,
            status=ParticipantStatus.COMPLETED,
            message="I'd be happy to help with your portfolio site! I have web dev experience.",
            hours_contributed=4.0,
            provider_confirmed=True,
            requester_confirmed=True,
        )
        session.add(participant_web)
        
        # ===== PENDING/ACCEPTED EXCHANGES (not yet completed) =====
        
        # PYTHON TUTORING (Alice's offer) - Capacity 3 - FULL with 3 ACCEPTED
        participant_python1 = Participant(
            user_id=users[6].id,  # Grace
            offer_id=offers[0][0].id,
            role=ParticipantRole.REQUESTER,
            status=ParticipantStatus.ACCEPTED,
            message="I'm interested in learning Python for data analysis!",
            hours_contributed=2.0,
        )
        session.add(participant_python1)
        
        participant_python2 = Participant(
            user_id=users[3].id,  # David
            offer_id=offers[0][0].id,
            role=ParticipantRole.REQUESTER,
            status=ParticipantStatus.ACCEPTED,
            message="Would love to learn Python web development!",
            hours_contributed=2.0,
        )
        session.add(participant_python2)
        
        participant_python3 = Participant(
            user_id=users[5].id,  # Frank
            offer_id=offers[0][0].id,
            role=ParticipantRole.REQUESTER,
            status=ParticipantStatus.ACCEPTED,
            message="Interested in data science with Python!",
            hours_contributed=2.0,
        )
        session.add(participant_python3)
        
        # WEB DEVELOPMENT WORKSHOP (Alice's offer) - Capacity 5 - 2 ACCEPTED
        participant_web_workshop1 = Participant(
            user_id=users[7].id,  # Henry
            offer_id=offers[1][0].id,
            role=ParticipantRole.REQUESTER,
            status=ParticipantStatus.ACCEPTED,
            message="Excited to learn web development!",
            hours_contributed=4.0,
        )
        session.add(participant_web_workshop1)
        
        participant_web_workshop2 = Participant(
            user_id=users[9].id,  # Jack
            offer_id=offers[1][0].id,
            role=ParticipantRole.REQUESTER,
            status=ParticipantStatus.ACCEPTED,
            message="I want to build my own website!",
            hours_contributed=4.0,
        )
        session.add(participant_web_workshop2)
        
        # TURKISH COOKING CLASS (David's offer) - Capacity 4 - 1 PENDING, 2 ACCEPTED
        participant_cooking1 = Participant(
            user_id=users[2].id,  # Carol
            offer_id=offers[6][0].id,
            role=ParticipantRole.REQUESTER,
            status=ParticipantStatus.PENDING,
            message="This sounds amazing! I love Turkish food!",
        )
        session.add(participant_cooking1)
        
        participant_cooking2 = Participant(
            user_id=users[8].id,  # Iris
            offer_id=offers[6][0].id,
            role=ParticipantRole.REQUESTER,
            status=ParticipantStatus.ACCEPTED,
            message="Can't wait to learn authentic Turkish recipes!",
            hours_contributed=3.0,
        )
        session.add(participant_cooking2)
        
        participant_cooking3 = Participant(
            user_id=users[0].id,  # Alice
            offer_id=offers[6][0].id,
            role=ParticipantRole.REQUESTER,
            status=ParticipantStatus.ACCEPTED,
            message="Turkish cuisine looks delicious!",
            hours_contributed=3.0,
        )
        session.add(participant_cooking3)
        
        # SPANISH CONVERSATION (Grace's offer) - Capacity 4 - Already has 1 COMPLETED (Carol)
        # Adding 3 more ACCEPTED to make it FULL (4/4 total)
        participant_spanish1 = Participant(
            user_id=users[3].id,  # David
            offer_id=offers[12][0].id,
            role=ParticipantRole.REQUESTER,
            status=ParticipantStatus.ACCEPTED,
            message="Looking to practice Spanish conversation!",
            hours_contributed=1.0,
        )
        session.add(participant_spanish1)
        
        participant_spanish2 = Participant(
            user_id=users[1].id,  # Bob
            offer_id=offers[12][0].id,
            role=ParticipantRole.REQUESTER,
            status=ParticipantStatus.ACCEPTED,
            message="I need to improve my Spanish skills!",
            hours_contributed=1.0,
        )
        session.add(participant_spanish2)
        
        participant_spanish3 = Participant(
            user_id=users[4].id,  # Emma
            offer_id=offers[12][0].id,
            role=ParticipantRole.REQUESTER,
            status=ParticipantStatus.ACCEPTED,
            message="Would love to practice with a native speaker!",
            hours_contributed=1.0,
        )
        session.add(participant_spanish3)
        
        # BIKE TUNE-UPS (Jack's offer) - Capacity 5 - 3 ACCEPTED
        participant_bike1 = Participant(
            user_id=users[2].id,  # Carol
            offer_id=offers[14][0].id,
            role=ParticipantRole.REQUESTER,
            status=ParticipantStatus.ACCEPTED,
            message="My bike needs some maintenance!",
            hours_contributed=1.0,
        )
        session.add(participant_bike1)
        
        participant_bike2 = Participant(
            user_id=users[6].id,  # Grace
            offer_id=offers[14][0].id,
            role=ParticipantRole.REQUESTER,
            status=ParticipantStatus.ACCEPTED,
            message="Great! My chain has been squeaking.",
            hours_contributed=1.0,
        )
        session.add(participant_bike2)
        
        participant_bike3 = Participant(
            user_id=users[4].id,  # Emma
            offer_id=offers[14][0].id,
            role=ParticipantRole.REQUESTER,
            status=ParticipantStatus.ACCEPTED,
            message="Perfect timing, my brakes need adjustment!",
            hours_contributed=1.0,
        )
        session.add(participant_bike3)
        
        # VOCAL COACHING (Carol's offer) - Capacity 2 - 1 ACCEPTED
        participant_vocal = Participant(
            user_id=users[7].id,  # Henry
            offer_id=offers[4][0].id,
            role=ParticipantRole.REQUESTER,
            status=ParticipantStatus.ACCEPTED,
            message="Would love to improve my singing!",
            hours_contributed=1.0,
        )
        session.add(participant_vocal)
        
        # GUITAR LESSONS NEEDED (Alice's need) - Capacity 1 - 1 PENDING
        participant_guitar = Participant(
            user_id=users[2].id,  # Carol
            need_id=needs[3][0].id,
            role=ParticipantRole.PROVIDER,
            status=ParticipantStatus.PENDING,
            message="I can teach you guitar! I've been playing for 10 years.",
        )
        session.add(participant_guitar)
        
        # DOG WALKING (Jack's need) - Capacity 1 - 1 ACCEPTED
        participant_dog = Participant(
            user_id=users[3].id,  # David
            need_id=needs[2][0].id,
            role=ParticipantRole.PROVIDER,
            status=ParticipantStatus.ACCEPTED,
            message="I'd be happy to help walk your dog!",
            hours_contributed=1.0,
        )
        session.add(participant_dog)
        
        # CHILDCARE (Iris's need) - Capacity 1 - 1 ACCEPTED
        participant_childcare = Participant(
            user_id=users[3].id,  # David
            need_id=needs[10][0].id,
            role=ParticipantRole.PROVIDER,
            status=ParticipantStatus.ACCEPTED,
            message="I have experience with kids and would love to help!",
            hours_contributed=2.0,
        )
        session.add(participant_childcare)
        
        # YOGA PARTNER (Emma's need) - Capacity 2 - 2 ACCEPTED (FULL)
        participant_yoga1 = Participant(
            user_id=users[5].id,  # Frank
            need_id=needs[6][0].id,
            role=ParticipantRole.PROVIDER,
            status=ParticipantStatus.ACCEPTED,
            message="I'd love to practice yoga together in the park!",
            hours_contributed=1.0,
        )
        session.add(participant_yoga1)
        
        participant_yoga2 = Participant(
            user_id=users[6].id,  # Grace
            need_id=needs[6][0].id,
            role=ParticipantRole.PROVIDER,
            status=ParticipantStatus.ACCEPTED,
            message="Count me in! Yoga in nature sounds perfect!",
            hours_contributed=1.0,
        )
        session.add(participant_yoga2)
        
        session.commit()
        print(f"✅ Created 28 participant records (5 completed, 23 active: 21 accepted + 2 pending)")
        
        # Refresh participants to get IDs
        session.refresh(participant1)
        session.refresh(participant3)
        session.refresh(participant5)
        session.refresh(participant_spanish)
        session.refresh(participant_web)
        
        # =================================================================
        # Create ledger entries for COMPLETED exchanges
        # =================================================================
        # Completed exchange 1: Alice learned carpentry from Bob (2 hours)
        # Bob (provider) gains 2 hours, Alice (requester) loses 2 hours
        users[1].balance += 2.0
        ledger_bob_earn1 = LedgerEntry(
            user_id=users[1].id,  # Bob
            credit=2.0,
            debit=0.0,
            balance=users[1].balance,
            description="Earned: Basic Carpentry Skills Workshop with Alice",
            transaction_type=TransactionType.EXCHANGE,
            participant_id=participant1.id,
        )
        session.add(ledger_bob_earn1)
        
        users[0].balance -= 2.0
        ledger_alice_spend1 = LedgerEntry(
            user_id=users[0].id,  # Alice
            credit=0.0,
            debit=2.0,
            balance=users[0].balance,
            description="Spent: Basic Carpentry Skills Workshop with Bob",
            transaction_type=TransactionType.EXCHANGE,
            participant_id=participant1.id,
        )
        session.add(ledger_alice_spend1)
        
        # Completed exchange 2: Frank learned composting from Emma (2 hours)
        # Emma (provider) gains 2 hours, Frank (requester) loses 2 hours
        users[4].balance += 2.0
        ledger_emma_earn = LedgerEntry(
            user_id=users[4].id,  # Emma
            credit=2.0,
            debit=0.0,
            balance=users[4].balance,
            description="Earned: Composting Workshop with Frank",
            transaction_type=TransactionType.EXCHANGE,
            participant_id=participant3.id,
        )
        session.add(ledger_emma_earn)
        
        users[5].balance -= 2.0
        ledger_frank_spend = LedgerEntry(
            user_id=users[5].id,  # Frank
            credit=0.0,
            debit=2.0,
            balance=users[5].balance,
            description="Spent: Composting Workshop with Emma",
            transaction_type=TransactionType.EXCHANGE,
            participant_id=participant3.id,
        )
        session.add(ledger_frank_spend)
        
        # Completed exchange 3: Bob helped Henry move furniture (3 hours)
        # Bob (provider) gains 3 hours, Henry (requester) loses 3 hours
        users[1].balance += 3.0
        ledger_bob_earn2 = LedgerEntry(
            user_id=users[1].id,  # Bob
            credit=3.0,
            debit=0.0,
            balance=users[1].balance,
            description="Earned: Help Moving Furniture for Henry",
            transaction_type=TransactionType.EXCHANGE,
            participant_id=participant5.id,
        )
        session.add(ledger_bob_earn2)
        
        users[7].balance -= 3.0
        ledger_henry_spend = LedgerEntry(
            user_id=users[7].id,  # Henry
            credit=0.0,
            debit=3.0,
            balance=users[7].balance,
            description="Spent: Help Moving Furniture with Bob",
            transaction_type=TransactionType.EXCHANGE,
            participant_id=participant5.id,
        )
        session.add(ledger_henry_spend)
        
        # Completed exchange 4: Carol learned Spanish from Grace (1 hour)
        # Grace (provider) gains 1 hour, Carol (requester) loses 1 hour
        users[6].balance += 1.0
        ledger_grace_earn = LedgerEntry(
            user_id=users[6].id,  # Grace
            credit=1.0,
            debit=0.0,
            balance=users[6].balance,
            description="Earned: Spanish Conversation Practice with Carol",
            transaction_type=TransactionType.EXCHANGE,
            participant_id=participant_spanish.id,
        )
        session.add(ledger_grace_earn)
        
        users[2].balance -= 1.0
        ledger_carol_spend = LedgerEntry(
            user_id=users[2].id,  # Carol
            credit=0.0,
            debit=1.0,
            balance=users[2].balance,
            description="Spent: Spanish Conversation Practice with Grace",
            transaction_type=TransactionType.EXCHANGE,
            participant_id=participant_spanish.id,
        )
        session.add(ledger_carol_spend)
        
        # Completed exchange 5: Alice helped Iris with website (4 hours)
        # Alice (provider) gains 4 hours, Iris (requester) loses 4 hours
        users[0].balance += 4.0
        ledger_alice_earn = LedgerEntry(
            user_id=users[0].id,  # Alice
            credit=4.0,
            debit=0.0,
            balance=users[0].balance,
            description="Earned: Website Design Help for Iris",
            transaction_type=TransactionType.EXCHANGE,
            participant_id=participant_web.id,
        )
        session.add(ledger_alice_earn)
        
        users[8].balance -= 4.0
        ledger_iris_spend = LedgerEntry(
            user_id=users[8].id,  # Iris
            credit=0.0,
            debit=4.0,
            balance=users[8].balance,
            description="Spent: Website Design Help with Alice",
            transaction_type=TransactionType.EXCHANGE,
            participant_id=participant_web.id,
        )
        session.add(ledger_iris_spend)
        
        session.commit()
        print(f"✅ Created 10 ledger entries for 5 completed exchanges")
        print(f"   - Bob: {users[1].balance}h, Alice: {users[0].balance}h, Emma: {users[4].balance}h")
        print(f"   - Frank: {users[5].balance}h, Henry: {users[7].balance}h, Grace: {users[6].balance}h")
        print(f"   - Carol: {users[2].balance}h, Iris: {users[8].balance}h")
        
        # Update accepted_count for offers and needs with completed/accepted participants
        # Completed exchanges
        offers[3][0].accepted_count = 1  # Carpentry workshop - COMPLETED
        offers[9][0].accepted_count = 1  # Composting workshop - COMPLETED
        offers[12][0].accepted_count = 1  # Spanish conversation - COMPLETED (old one)
        needs[0][0].accepted_count = 1  # Help Moving Furniture - COMPLETED
        needs[1][0].accepted_count = 1  # Website Design Help - COMPLETED
        
        # Active exchanges with accepted participants
        offers[0][0].accepted_count = 3  # Python Tutoring - FULL (3/3)
        offers[1][0].accepted_count = 2  # Web Development Workshop (2/5)
        offers[4][0].accepted_count = 1  # Vocal Coaching (1/2)
        offers[6][0].accepted_count = 2  # Turkish Cooking (2/4, 1 pending)
        offers[12][0].accepted_count = 4  # Spanish Conversation (1 completed + 3 accepted = 4/4) FULL
        offers[14][0].accepted_count = 3  # Bike Tune-ups (3/5)
        needs[2][0].accepted_count = 1  # Dog Walking (1/1) FULL
        needs[6][0].accepted_count = 2  # Yoga Partner (2/2) FULL
        needs[10][0].accepted_count = 1  # Childcare (1/1) FULL
        
        # Mark offers/needs with completed participants as COMPLETED
        offers[3][0].status = OfferStatus.COMPLETED  # Carpentry workshop - completed
        offers[9][0].status = OfferStatus.COMPLETED  # Composting workshop - completed
        needs[0][0].status = NeedStatus.COMPLETED  # Help Moving Furniture - completed
        needs[1][0].status = NeedStatus.COMPLETED  # Website Design Help - completed
        
        # Mark FULL offers/needs (accepted_count >= capacity)
        offers[0][0].status = OfferStatus.FULL  # Python Tutoring (3/3)
        offers[12][0].status = OfferStatus.FULL  # Spanish Conversation (4/4)
        needs[2][0].status = NeedStatus.FULL  # Dog Walking (1/1)
        needs[6][0].status = NeedStatus.FULL  # Yoga Partner (2/2)
        needs[10][0].status = NeedStatus.FULL  # Childcare (1/1)
        
        session.commit()
        print(f"✅ Updated accepted_count and status for all exchanges")
        print(f"   - Full: Python Tutoring (3/3), Spanish Convo (4/4), Dog Walking (1/1), Yoga (2/2), Childcare (1/1)")
        print(f"   - Partial: Web Workshop (2/5), Vocal (1/2), Turkish Cooking (2/4), Bike Tune-ups (3/5)")
        print(f"   - Empty: 12 exchanges have no participants yet")
        
        # =================================================================
        # Create RATINGS for completed exchanges (FR-10.4)
        # =================================================================
        
        # Rating 1a: Alice rates Bob for carpentry workshop (Bob was provider)
        rating1a = Rating(
            from_user_id=users[0].id,  # Alice
            to_user_id=users[1].id,  # Bob
            participant_id=participant1.id,
            reliability_rating=5,
            kindness_rating=5,
            helpfulness_rating=5,
            general_rating=5,  # avg of (5+5+5)/3 = 5
            public_comment="Bob is an excellent teacher! Very patient and knowledgeable about carpentry.",
            visibility=RatingVisibility.VISIBLE,
        )
        session.add(rating1a)
        
        # Rating 1b: Bob rates Alice (Alice was requester/learner)
        rating1b = Rating(
            from_user_id=users[1].id,  # Bob
            to_user_id=users[0].id,  # Alice
            participant_id=participant1.id,
            reliability_rating=5,
            kindness_rating=5,
            helpfulness_rating=4,
            general_rating=4.7,  # avg of (5+5+4)/3 = 4.67
            public_comment="Alice was a great student - eager to learn and asked great questions!",
            visibility=RatingVisibility.VISIBLE,
        )
        session.add(rating1b)
        
        # Rating 2a: Frank rates Emma for composting workshop
        rating2a = Rating(
            from_user_id=users[5].id,  # Frank
            to_user_id=users[4].id,  # Emma
            participant_id=participant3.id,
            reliability_rating=5,
            kindness_rating=5,
            helpfulness_rating=5,
            general_rating=5,
            public_comment="Emma's workshop was incredibly informative! I feel confident starting my own compost now.",
            visibility=RatingVisibility.VISIBLE,
        )
        session.add(rating2a)
        
        # Rating 2b: Emma rates Frank
        rating2b = Rating(
            from_user_id=users[4].id,  # Emma
            to_user_id=users[5].id,  # Frank
            participant_id=participant3.id,
            reliability_rating=5,
            kindness_rating=4,
            helpfulness_rating=4,
            general_rating=4.3,  # avg of (5+4+4)/3 = 4.33
            public_comment="Frank was enthusiastic and brought great energy to the workshop!",
            visibility=RatingVisibility.VISIBLE,
        )
        session.add(rating2b)
        
        # Rating 3a: Henry rates Bob for moving help
        rating3a = Rating(
            from_user_id=users[7].id,  # Henry
            to_user_id=users[1].id,  # Bob
            participant_id=participant5.id,
            reliability_rating=5,
            kindness_rating=5,
            helpfulness_rating=5,
            general_rating=5,
            public_comment="Bob was amazing! Strong, efficient, and made my move stress-free. Highly recommend!",
            visibility=RatingVisibility.VISIBLE,
        )
        session.add(rating3a)
        
        # Rating 3b: Bob rates Henry
        rating3b = Rating(
            from_user_id=users[1].id,  # Bob
            to_user_id=users[7].id,  # Henry
            participant_id=participant5.id,
            reliability_rating=4,
            kindness_rating=5,
            helpfulness_rating=4,
            general_rating=4.3,  # avg of (4+5+4)/3 = 4.33
            public_comment="Henry was well-prepared for the move. Everything went smoothly!",
            visibility=RatingVisibility.VISIBLE,
        )
        session.add(rating3b)
        
        # Rating 4a: Carol rates Grace for Spanish conversation
        rating4a = Rating(
            from_user_id=users[2].id,  # Carol
            to_user_id=users[6].id,  # Grace
            participant_id=participant_spanish.id,
            reliability_rating=5,
            kindness_rating=5,
            helpfulness_rating=5,
            general_rating=5,
            public_comment="Grace is a fantastic Spanish conversation partner! Very encouraging and helpful with corrections.",
            visibility=RatingVisibility.VISIBLE,
        )
        session.add(rating4a)
        
        # Rating 4b: Grace rates Carol
        rating4b = Rating(
            from_user_id=users[6].id,  # Grace
            to_user_id=users[2].id,  # Carol
            participant_id=participant_spanish.id,
            reliability_rating=5,
            kindness_rating=5,
            helpfulness_rating=4,
            general_rating=4.7,  # avg of (5+5+4)/3 = 4.67
            public_comment="Carol is making great progress! Always comes prepared and is a joy to practice with.",
            visibility=RatingVisibility.VISIBLE,
        )
        session.add(rating4b)
        
        # Rating 5a: Iris rates Alice for website help
        rating5a = Rating(
            from_user_id=users[8].id,  # Iris
            to_user_id=users[0].id,  # Alice
            participant_id=participant_web.id,
            reliability_rating=5,
            kindness_rating=5,
            helpfulness_rating=5,
            general_rating=5,
            public_comment="Alice created the perfect portfolio website for my art! She understood exactly what I needed.",
            visibility=RatingVisibility.VISIBLE,
        )
        session.add(rating5a)
        
        # Rating 5b: Alice rates Iris
        rating5b = Rating(
            from_user_id=users[0].id,  # Alice
            to_user_id=users[8].id,  # Iris
            participant_id=participant_web.id,
            reliability_rating=5,
            kindness_rating=5,
            helpfulness_rating=4,
            general_rating=4.7,  # avg of (5+5+4)/3 = 4.67
            public_comment="Iris had beautiful art content ready and gave clear feedback. Great collaboration!",
            visibility=RatingVisibility.VISIBLE,
        )
        session.add(rating5b)
        
        session.commit()
        print(f"✅ Created 10 ratings for 5 completed exchanges (mutual ratings)")
        
        # ============================================================
        # Create Forum Topics (FR-15: Community Forum)
        # ============================================================
        
        # Discussion 1: Welcome topic
        topic1 = ForumTopic(
            topic_type=TopicType.DISCUSSION,
            creator_id=users[0].id,  # Alice
            title="Welcome to The Hive Community!",
            content="""Hello everyone! 🐝

Welcome to The Hive - our community time-banking platform! This is the place to discuss community topics, share ideas, and connect with fellow members.

A few tips for getting started:
- Browse the Map to see available offers and needs in your area
- Create an Offer to share your skills with the community
- Post a Need if you're looking for help with something
- Use tags to make your posts discoverable

Looking forward to building this community together!

Alice""",
            is_approved=True,
            is_visible=True,
            is_pinned=True,  # Pin the welcome message
            view_count=42,
            comment_count=3,
        )
        session.add(topic1)
        session.flush()
        
        # Add tags to topic1
        for tag_name in ["welcome", "community", "getting-started"]:
            tag = session.exec(select(Tag).where(Tag.name == tag_name)).first()
            if not tag:
                tag = Tag(name=tag_name)
                session.add(tag)
                session.flush()
            topic_tag = ForumTopicTag(topic_id=topic1.id, tag_id=tag.id)
            session.add(topic_tag)
        
        print(f"✅ Created forum topic: {topic1.title} (ID: {topic1.id})")
        
        # Discussion 2: Tips for new members
        topic2 = ForumTopic(
            topic_type=TopicType.DISCUSSION,
            creator_id=users[1].id,  # Bob
            title="Tips for a Successful Exchange",
            content="""Hi everyone!

After completing several exchanges, I wanted to share some tips that helped me have great experiences:

**Before the Exchange:**
- Read the offer/need description carefully
- Check the other person's profile and ratings
- Communicate clearly about expectations

**During the Exchange:**
- Be punctual and respectful
- Take your time - quality matters more than speed
- Ask questions if anything is unclear

**After the Exchange:**
- Leave a thoughtful rating
- Thank the other person
- Keep in touch if you'd like!

What tips would you add?""",
            is_approved=True,
            is_visible=True,
            view_count=28,
            comment_count=0,  # Will be updated after adding comments
        )
        session.add(topic2)
        session.flush()
        
        for tag_name in ["tips", "community"]:
            tag = session.exec(select(Tag).where(Tag.name == tag_name)).first()
            if not tag:
                tag = Tag(name=tag_name)
                session.add(tag)
                session.flush()
            topic_tag = ForumTopicTag(topic_id=topic2.id, tag_id=tag.id)
            session.add(topic_tag)
        
        print(f"✅ Created forum topic: {topic2.title} (ID: {topic2.id})")
        
        # Discussion 3: Programming discussion
        topic3 = ForumTopic(
            topic_type=TopicType.DISCUSSION,
            creator_id=users[0].id,  # Alice
            title="Best Practices for Teaching Programming",
            content="""Fellow tutors! 👩‍💻

I've been teaching Python for a while now and wanted to discuss effective teaching methods.

What I've found works well:
- Start with practical examples, not theory
- Use pair programming for hands-on learning
- Build small projects instead of isolated exercises
- Celebrate small wins!

What teaching approaches have worked for you? Any tools or resources you recommend?""",
            is_approved=True,
            is_visible=True,
            view_count=19,
            comment_count=0,  # Will be updated after adding comments
        )
        session.add(topic3)
        session.flush()
        
        for tag_name in ["programming", "tutoring", "education"]:
            tag = session.exec(select(Tag).where(Tag.name == tag_name)).first()
            if not tag:
                tag = Tag(name=tag_name)
                session.add(tag)
                session.flush()
            topic_tag = ForumTopicTag(topic_id=topic3.id, tag_id=tag.id)
            session.add(topic_tag)
        
        print(f"✅ Created forum topic: {topic3.title} (ID: {topic3.id})")
        
        # Event 1: Community gardening day
        event1 = ForumTopic(
            topic_type=TopicType.EVENT,
            creator_id=users[4].id,  # Emma
            title="🌱 Community Garden Day - All Welcome!",
            content="""Join us for a fun day of gardening in our community space!

**What we'll do:**
- Plant new vegetables and herbs
- Learn composting basics
- Share gardening tips
- Enjoy homemade refreshments

No experience necessary - everyone is welcome, from beginners to green thumbs!

Please bring:
- Comfortable clothes that can get dirty
- A water bottle
- Enthusiasm! 🌻

See you there!""",
            event_start_time=datetime.utcnow() + timedelta(days=7),
            event_end_time=datetime.utcnow() + timedelta(days=7, hours=4),
            event_location="Community Garden, Kadıköy",
            is_approved=True,
            is_visible=True,
            view_count=35,
            comment_count=0,  # Will be updated after adding comments
        )
        session.add(event1)
        session.flush()
        
        for tag_name in ["gardening", "community", "event"]:
            tag = session.exec(select(Tag).where(Tag.name == tag_name)).first()
            if not tag:
                tag = Tag(name=tag_name)
                session.add(tag)
                session.flush()
            topic_tag = ForumTopicTag(topic_id=event1.id, tag_id=tag.id)
            session.add(topic_tag)
        
        print(f"✅ Created forum event: {event1.title} (ID: {event1.id})")
        
        # Event 2: Cooking workshop
        topic5 = ForumTopic(
            topic_type=TopicType.EVENT,
            creator_id=users[2].id,  # Carol
            title="🍳 Turkish Cooking Workshop",
            content="""Learn to make traditional Turkish dishes!

**Menu:**
- Mercimek Çorbası (Red Lentil Soup)
- Yaprak Sarma (Stuffed Grape Leaves)
- İmam Bayıldı (Stuffed Eggplant)

**What's included:**
- All ingredients
- Recipe cards to take home
- Leftovers to share!

Space is limited to 6 people to ensure hands-on participation.

Requirements:
- No cooking experience needed
- Please inform me of any allergies

Afiyet olsun! 😋""",
            event_start_time=datetime.utcnow() + timedelta(days=14),
            event_end_time=datetime.utcnow() + timedelta(days=14, hours=3),
            event_location="Carol's Kitchen, Beşiktaş",
            is_approved=True,
            is_visible=True,
            view_count=48,
            comment_count=0,  # Will be updated after adding comments
        )
        session.add(topic5)
        session.flush()
        
        for tag_name in ["cooking", "workshop", "turkish-cuisine"]:
            tag = session.exec(select(Tag).where(Tag.name == tag_name)).first()
            if not tag:
                tag = Tag(name=tag_name)
                session.add(tag)
                session.flush()
            topic_tag = ForumTopicTag(topic_id=topic5.id, tag_id=tag.id)
            session.add(topic_tag)
        
        print(f"✅ Created forum event: {topic5.title} (ID: {topic5.id})")
        
        # Event 3: Fitness meetup
        topic6 = ForumTopic(
            topic_type=TopicType.EVENT,
            creator_id=users[5].id,  # Frank
            title="🏃 Morning Run & Stretch Session",
            content="""Rise and shine! Join our weekly morning run.

**Schedule:**
- 7:00 - Warm-up stretches
- 7:15 - 5K run along the Bosphorus
- 8:00 - Cool-down and yoga
- 8:30 - Coffee (optional)

**All fitness levels welcome!**
We maintain a supportive pace - walk, jog, or run at your own speed.

Meet at the Ortaköy Mosque steps. Look for me in the orange shirt!

Rain or shine - we're doing this! ☀️🌧️""",
            event_start_time=datetime.utcnow() + timedelta(days=3),
            event_end_time=datetime.utcnow() + timedelta(days=3, hours=2),
            event_location="Ortaköy, Istanbul",
            is_approved=True,
            is_visible=True,
            view_count=22,
            comment_count=0,  # Will be updated after adding comments
        )
        session.add(topic6)
        session.flush()
        
        for tag_name in ["fitness", "running", "yoga"]:
            tag = session.exec(select(Tag).where(Tag.name == tag_name)).first()
            if not tag:
                tag = Tag(name=tag_name)
                session.add(tag)
                session.flush()
            topic_tag = ForumTopicTag(topic_id=topic6.id, tag_id=tag.id)
            session.add(topic_tag)
        
        print(f"✅ Created forum event: {topic6.title} (ID: {topic6.id})")
        
        # Add some comments to topics
        comment1 = ForumComment(
            topic_id=topic1.id,
            author_id=users[1].id,  # Bob
            content="Welcome everyone! Excited to be part of this community. Looking forward to learning and sharing skills!",
            is_approved=True,
            is_visible=True,
        )
        session.add(comment1)
        
        comment2 = ForumComment(
            topic_id=topic1.id,
            author_id=users[2].id,  # Carol
            content="This is such a great initiative! The time-banking concept really resonates with me.",
            is_approved=True,
            is_visible=True,
        )
        session.add(comment2)
        
        comment3 = ForumComment(
            topic_id=topic1.id,
            author_id=users[3].id,  # David
            content="Happy to be here! 👋 If anyone needs help with home repairs or carpentry, check out my offers!",
            is_approved=True,
            is_visible=True,
        )
        session.add(comment3)
        
        comment4 = ForumComment(
            topic_id=topic2.id,
            author_id=users[4].id,  # Emma
            content="Great tips! I'd add: take photos during the exchange (with permission) - they help with ratings and make nice memories!",
            is_approved=True,
            is_visible=True,
        )
        session.add(comment4)
        
        comment5 = ForumComment(
            topic_id=event1.id,
            author_id=users[6].id,  # Grace
            content="I'll be there! Should I bring any specific tools?",
            is_approved=True,
            is_visible=True,
        )
        session.add(comment5)
        
        comment6 = ForumComment(
            topic_id=event1.id,
            author_id=users[4].id,  # Emma (reply)
            content="@Grace No need! We have all the tools. Just bring yourself and some enthusiasm! 🌱",
            is_approved=True,
            is_visible=True,
        )
        session.add(comment6)
        
        session.flush()
        
        # Update comment_count for each topic based on actual comments
        topic1.comment_count = 3  # comment1, comment2, comment3
        topic2.comment_count = 1  # comment4
        topic3.comment_count = 0  # no comments
        event1.comment_count = 2  # comment5, comment6
        topic5.comment_count = 0  # no comments
        topic6.comment_count = 0  # no comments
        
        session.commit()
        print(f"✅ Created 6 forum topics (3 discussions, 3 events) with 6 comments")
        
    print("\n✅ Comprehensive seed data created successfully")
    print(f"   - 10 users with unique profiles and locations")
    print(f"   - 15 tags across various service categories")
    print(f"   - 15 offers with remote and in-person options")
    print(f"   - 12 needs with diverse requirements")
    print(f"   - 28 participant records (5 completed, 21 accepted, 2 pending)")
    print(f"   - 20 ledger entries (10 initial + 10 from exchanges)")
    print(f"   - 10 ratings (mutual ratings for 5 completed exchanges)")
    print(f"   - 6 forum topics with comments")


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
        if len(participants) < 23:
            raise ValueError(f"❌ Expected at least 23 participants, found {len(participants)}")
        print(f"✅ Found {len(participants)} participants/applications")
        
        # Check completed participants
        completed_participants = [p for p in participants if p.status == ParticipantStatus.COMPLETED]
        if len(completed_participants) < 5:
            raise ValueError(f"❌ Expected at least 5 completed participants, found {len(completed_participants)}")
        print(f"✅ Found {len(completed_participants)} completed participants")
        
        # Check ratings
        ratings = session.exec(select(Rating)).all()
        if len(ratings) < 10:
            raise ValueError(f"❌ Expected at least 10 ratings, found {len(ratings)}")
        print(f"✅ Found {len(ratings)} ratings")
        
        # Check ledger entries (10 initial + 10 from 5 completed exchanges)
        ledger_entries = session.exec(select(LedgerEntry)).all()
        if len(ledger_entries) < 20:
            raise ValueError(f"❌ Expected at least 20 ledger entries, found {len(ledger_entries)}")
        print(f"✅ Found {len(ledger_entries)} ledger entries")
        
        # Check forum topics
        forum_topics = session.exec(select(ForumTopic)).all()
        if len(forum_topics) < 6:
            raise ValueError(f"❌ Expected at least 6 forum topics, found {len(forum_topics)}")
        print(f"✅ Found {len(forum_topics)} forum topics")
        
        # Check forum comments
        forum_comments = session.exec(select(ForumComment)).all()
        if len(forum_comments) < 6:
            raise ValueError(f"❌ Expected at least 6 forum comments, found {len(forum_comments)}")
        print(f"✅ Found {len(forum_comments)} forum comments")
        
        # Validate FK constraints by checking a few relationships
        alice = session.exec(select(User).where(User.username == "alice")).first()
        if not alice:
            raise ValueError("❌ User 'alice' not found")
        
        alice_offers = session.exec(select(Offer).where(Offer.creator_id == alice.id)).all()
        if len(alice_offers) == 0:
            raise ValueError("❌ No offers found for alice - FK constraint may be broken")
        
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
