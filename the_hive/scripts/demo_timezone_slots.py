#!/usr/bin/env python3
"""
Example demonstrating timezone-aware time slot handling.
"""

import json
from datetime import date
from zoneinfo import ZoneInfo

# Simulate importing from your app
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.schemas.time_slot import TimeRange, AvailableTimeSlot

print("=" * 70)
print("TIMEZONE-AWARE TIME SLOTS - DEMONSTRATION")
print("=" * 70)
print()

# Example 1: User in Istanbul creates an offer
print("Example 1: User in Istanbul offers tutoring")
print("-" * 70)

istanbul_slot = AvailableTimeSlot(
    date="2025-12-01",
    time_ranges=[
        TimeRange(start_time="14:00", end_time="15:00"),
        TimeRange(start_time="16:00", end_time="17:00")
    ],
    timezone="Europe/Istanbul"
)

print(f"Date: {istanbul_slot.date}")
print(f"Timezone: {istanbul_slot.timezone}")
print(f"Time ranges:")
for i, tr in enumerate(istanbul_slot.time_ranges, 1):
    duration = tr.duration_minutes()
    print(f"  {i}. {tr.start_time} - {tr.end_time} ({duration} minutes)")

# Convert to UTC for comparison
date_obj = istanbul_slot.get_date_object()
for i, tr in enumerate(istanbul_slot.time_ranges, 1):
    start_dt, end_dt = tr.to_datetime_range(date_obj, "Europe/Istanbul")
    start_utc = start_dt.astimezone(ZoneInfo("UTC"))
    end_utc = end_dt.astimezone(ZoneInfo("UTC"))
    print(f"     → In UTC: {start_utc.strftime('%H:%M')} - {end_utc.strftime('%H:%M')}")

print()

# Example 2: User in New York sees the offer
print("Example 2: Converting to New York time for display")
print("-" * 70)

for i, tr in enumerate(istanbul_slot.time_ranges, 1):
    start_dt, end_dt = tr.to_datetime_range(date_obj, "Europe/Istanbul")
    start_ny = start_dt.astimezone(ZoneInfo("America/New_York"))
    end_ny = end_dt.astimezone(ZoneInfo("America/New_York"))
    print(f"  {i}. Istanbul 14:00-15:00 = New York {start_ny.strftime('%H:%M')}-{end_ny.strftime('%H:%M')}")

print()

# Example 3: User in New York creates a need (same actual time!)
print("Example 3: User in New York needs help")
print("-" * 70)

ny_slot = AvailableTimeSlot(
    date="2025-12-01",
    time_ranges=[
        TimeRange(start_time="06:00", end_time="07:00")  # 6 AM NYC time
    ],
    timezone="America/New_York"
)

print(f"New York user available: {ny_slot.time_ranges[0].start_time} - {ny_slot.time_ranges[0].end_time}")

# Convert both to UTC to check if they overlap
ny_start, ny_end = ny_slot.time_ranges[0].to_datetime_range(date_obj, "America/New_York")
istanbul_start, istanbul_end = istanbul_slot.time_ranges[0].to_datetime_range(date_obj, "Europe/Istanbul")

ny_start_utc = ny_start.astimezone(ZoneInfo("UTC"))
istanbul_start_utc = istanbul_start.astimezone(ZoneInfo("UTC"))

print(f"New York 06:00 in UTC: {ny_start_utc.strftime('%H:%M')}")
print(f"Istanbul 14:00 in UTC: {istanbul_start_utc.strftime('%H:%M')}")

if ny_start_utc == istanbul_start_utc:
    print("✅ MATCH! These times are exactly the same!")
else:
    print(f"❌ Different times (offset: {(istanbul_start_utc - ny_start_utc).total_seconds() / 3600:.1f} hours)")

print()

# Example 4: Validation - overlapping ranges
print("Example 4: Validation prevents overlapping time ranges")
print("-" * 70)

try:
    bad_slot = AvailableTimeSlot(
        date="2025-12-01",
        time_ranges=[
            TimeRange(start_time="14:00", end_time="15:30"),
            TimeRange(start_time="15:00", end_time="16:00")  # Overlaps with previous!
        ],
        timezone="UTC"
    )
    print("❌ Should have raised an error!")
except ValueError as e:
    print(f"✅ Correctly caught overlap: {e}")

print()

# Example 5: Duration calculation
print("Example 5: Duration calculations")
print("-" * 70)

ranges = [
    TimeRange(start_time="09:00", end_time="10:00"),
    TimeRange(start_time="14:00", end_time="15:30"),
    TimeRange(start_time="16:00", end_time="18:15"),
]

for tr in ranges:
    duration = tr.duration_minutes()
    hours = duration // 60
    mins = duration % 60
    print(f"  {tr.start_time} - {tr.end_time}: {duration} minutes ({hours}h {mins}m)")

print()

# Example 6: JSON serialization (how it's stored in database)
print("Example 6: JSON storage format")
print("-" * 70)

slot_with_tz = AvailableTimeSlot(
    date="2025-12-15",
    time_ranges=[
        TimeRange(start_time="10:00", end_time="11:00")
    ],
    timezone="Europe/Istanbul"
)

# This is what gets stored in the database
json_data = slot_with_tz.model_dump()
print("Stored as JSON:")
print(json.dumps(json_data, indent=2))

print()
print("=" * 70)
print("KEY TAKEAWAYS:")
print("=" * 70)
print("""
1. ✅ Times are stored as simple strings (HH:MM) - easy to read/input
2. ✅ Timezone is stored separately - explicit and clear
3. ✅ Can convert to any timezone when needed
4. ✅ Can convert to UTC for accurate time comparisons
5. ✅ Duration calculations are straightforward
6. ✅ Validation prevents common mistakes (overlaps, invalid times)
7. ✅ Backward compatible - timezone field is optional

RECOMMENDATION:
- Store user's timezone in their profile (auto-detect from browser)
- Include timezone when creating time slots
- Display times with context: "2:00 PM (Istanbul time)"
- Optionally show converted time for viewer: "6:00 AM your time"
""")
