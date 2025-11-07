from datetime import datetime, date, time
from typing import Optional
from zoneinfo import ZoneInfo
from pydantic import BaseModel, Field, field_validator, model_validator


class TimeRange(BaseModel):
    """Represents a time range with timezone awareness.
    
    Times are stored as strings in HH:MM format for simplicity,
    but are always interpreted in the context of the user's timezone.
    """
    start_time: str = Field(
        ..., 
        pattern=r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$",
        description="Start time in HH:MM format (24-hour)"
    )
    end_time: str = Field(
        ..., 
        pattern=r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$",
        description="End time in HH:MM format (24-hour)"
    )
    
    @field_validator('end_time')
    @classmethod
    def validate_end_after_start(cls, v, info):
        """Ensure end_time is after start_time"""
        if 'start_time' in info.data:
            start = info.data['start_time']
            if v <= start:
                raise ValueError("end_time must be after start_time")
        return v
    
    def to_datetime_range(self, date_obj: date, timezone: str = "UTC") -> tuple[datetime, datetime]:
        """Convert time range to datetime objects with timezone.
        
        Args:
            date_obj: The date for this time range
            timezone: IANA timezone (e.g., "America/New_York", "Europe/Istanbul")
        
        Returns:
            Tuple of (start_datetime, end_datetime) with timezone info
        """
        tz = ZoneInfo(timezone)
        start_hour, start_min = map(int, self.start_time.split(':'))
        end_hour, end_min = map(int, self.end_time.split(':'))
        
        start_dt = datetime(
            date_obj.year, date_obj.month, date_obj.day,
            start_hour, start_min,
            tzinfo=tz
        )
        end_dt = datetime(
            date_obj.year, date_obj.month, date_obj.day,
            end_hour, end_min,
            tzinfo=tz
        )
        
        return start_dt, end_dt
    
    def duration_minutes(self) -> int:
        """Calculate duration in minutes."""
        start_hour, start_min = map(int, self.start_time.split(':'))
        end_hour, end_min = map(int, self.end_time.split(':'))
        
        start_total = start_hour * 60 + start_min
        end_total = end_hour * 60 + end_min
        
        return end_total - start_total


class AvailableTimeSlot(BaseModel):
    """Represents available time slots for a specific date.
    
    Best Practices:
    - Store date as YYYY-MM-DD string for simplicity
    - Store times in user's local timezone context
    - Frontend should send user's timezone separately
    - Backend converts to UTC for storage/comparison if needed
    """
    date: str = Field(
        ..., 
        pattern=r"^\d{4}-\d{2}-\d{2}$", 
        description="Date in YYYY-MM-DD format"
    )
    time_ranges: list[TimeRange] = Field(
        ..., 
        min_length=1, 
        description="Available time ranges for this date"
    )
    timezone: Optional[str] = Field(
        None,
        description="IANA timezone (e.g., 'America/New_York', 'Europe/Istanbul'). Defaults to UTC."
    )
    
    @field_validator('date')
    @classmethod
    def validate_date_format(cls, v):
        """Validate date format and ensure it's not in the past."""
        try:
            year, month, day = map(int, v.split('-'))
            slot_date = date(year, month, day)
            
            # Optional: Warn if date is in the past (commented out for flexibility)
            # if slot_date < date.today():
            #     raise ValueError(f"Date {v} is in the past")
            
        except ValueError as e:
            raise ValueError(f"Invalid date format: {v}") from e
        return v
    
    @field_validator('timezone')
    @classmethod
    def validate_timezone(cls, v):
        """Validate timezone string."""
        if v is not None:
            try:
                ZoneInfo(v)
            except Exception as e:
                raise ValueError(f"Invalid timezone: {v}. Use IANA timezone names like 'America/New_York'") from e
        return v
    
    @model_validator(mode='after')
    def check_no_overlapping_ranges(self):
        """Ensure time ranges don't overlap."""
        ranges = self.time_ranges
        for i in range(len(ranges)):
            for j in range(i + 1, len(ranges)):
                # Simple overlap check using string comparison (works for HH:MM format)
                r1, r2 = ranges[i], ranges[j]
                # Overlap if: r1.start < r2.end AND r2.start < r1.end
                if r1.start_time < r2.end_time and r2.start_time < r1.end_time:
                    raise ValueError(
                        f"Overlapping time ranges: {r1.start_time}-{r1.end_time} and {r2.start_time}-{r2.end_time}"
                    )
        return self
    
    def get_date_object(self) -> date:
        """Convert date string to date object."""
        year, month, day = map(int, self.date.split('-'))
        return date(year, month, day)
