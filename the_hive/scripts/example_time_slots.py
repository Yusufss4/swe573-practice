#!/usr/bin/env python
"""
Example: Creating offers and needs with available time slots.

This demonstrates how to use the time slots feature to specify
when services are available.
"""

import json

# Example 1: Create an offer with time slots (like in the UI image)
offer_with_slots = {
    "title": "Web Development Tutoring",
    "description": "I can help you learn HTML, CSS, JavaScript, and React. Perfect for beginners or those looking to improve their skills.",
    "is_remote": True,
    "location_name": None,
    "capacity": 3,
    "tags": ["Coding", "Education", "Web Development"],
    "available_slots": [
        {
            "date": "2025-10-22",  # Wednesday
            "time_ranges": [
                {"start_time": "14:00", "end_time": "15:00"},
                {"start_time": "15:00", "end_time": "16:00"}
            ]
        },
        {
            "date": "2025-10-23",  # Thursday
            "time_ranges": [
                {"start_time": "10:00", "end_time": "11:00"},
                {"start_time": "14:00", "end_time": "15:00"}
            ]
        },
        {
            "date": "2025-10-24",  # Friday
            "time_ranges": [
                {"start_time": "14:00", "end_time": "15:00"}
            ]
        }
    ]
}

print("Example 1: Offer with time slots")
print("=" * 60)
print(json.dumps(offer_with_slots, indent=2))
print()

# Example 2: Create a need with time slots
need_with_slots = {
    "title": "Need help with Python project",
    "description": "Looking for someone to help debug my Django application. I have specific times when I'm available to work together.",
    "is_remote": True,
    "location_name": None,
    "capacity": 1,
    "tags": ["Coding", "Python", "Django"],
    "available_slots": [
        {
            "date": "2025-11-15",
            "time_ranges": [
                {"start_time": "09:00", "end_time": "10:00"},
                {"start_time": "10:00", "end_time": "11:00"}
            ]
        },
        {
            "date": "2025-11-16",
            "time_ranges": [
                {"start_time": "14:00", "end_time": "16:00"}
            ]
        }
    ]
}

print("Example 2: Need with time slots")
print("=" * 60)
print(json.dumps(need_with_slots, indent=2))
print()

# Example 3: In-person offer with specific availability
inperson_offer = {
    "title": "Guitar Lessons in Manhattan",
    "description": "Beginner to intermediate guitar lessons at my studio in Manhattan.",
    "is_remote": False,
    "location_lat": 40.7589,
    "location_lon": -73.9851,
    "location_name": "Manhattan, New York",
    "capacity": 2,
    "tags": ["Music", "Education", "Arts"],
    "available_slots": [
        {
            "date": "2025-11-20",
            "time_ranges": [
                {"start_time": "16:00", "end_time": "17:00"},
                {"start_time": "17:00", "end_time": "18:00"},
                {"start_time": "18:00", "end_time": "19:00"}
            ]
        },
        {
            "date": "2025-11-21",
            "time_ranges": [
                {"start_time": "16:00", "end_time": "17:00"},
                {"start_time": "17:00", "end_time": "18:00"}
            ]
        }
    ]
}

print("Example 3: In-person offer with time slots")
print("=" * 60)
print(json.dumps(inperson_offer, indent=2))
print()

# Example 4: Offer without time slots (flexible scheduling)
flexible_offer = {
    "title": "General Programming Help",
    "description": "Available to help with various programming questions. We can schedule on an ad-hoc basis.",
    "is_remote": True,
    "location_name": None,
    "capacity": 5,
    "tags": ["Coding", "Programming"],
    "available_slots": None  # No specific slots - flexible scheduling
}

print("Example 4: Offer without specific time slots")
print("=" * 60)
print(json.dumps(flexible_offer, indent=2))
print()

print("=" * 60)
print("API Usage:")
print("=" * 60)
print("""
To create an offer with time slots:

POST /api/offers
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "title": "Your offer title",
  "description": "Your offer description",
  "is_remote": true,
  "capacity": 3,
  "tags": ["tag1", "tag2"],
  "available_slots": [
    {
      "date": "2025-11-20",
      "time_ranges": [
        {"start_time": "14:00", "end_time": "15:00"}
      ]
    }
  ]
}

To update time slots:

PATCH /api/offers/{offer_id}
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "available_slots": [
    {
      "date": "2025-11-25",
      "time_ranges": [
        {"start_time": "10:00", "end_time": "12:00"}
      ]
    }
  ]
}

The same applies for /api/needs endpoints.
""")
