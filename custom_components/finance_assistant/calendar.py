"""Calendar platform for Finance Assistant integration."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import (
    ATTR_QUERY_ID,
    ATTR_QUERY_NAME,
    ATTR_QUERY_DESCRIPTION,
    ATTR_LAST_UPDATED,
    ATTR_QUERY_TYPE,
    DEVICE_INFO,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Finance Assistant calendar based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # Create calendars for each CALENDAR query
    calendars = []
    if coordinator.data and "queries" in coordinator.data:
        for query in coordinator.data["queries"]:
            if query.get("output_type") == "CALENDAR":
                calendar = FinanceAssistantCalendar(coordinator, query)
                calendars.append(calendar)

    async_add_entities(calendars)


class FinanceAssistantCalendar(CalendarEntity):
    """Representation of a Finance Assistant calendar."""

    def __init__(self, coordinator, query: dict[str, Any]) -> None:
        """Initialize the calendar."""
        self.coordinator = coordinator
        self.query = query
        self.query_id = query["id"]
        self._attr_unique_id = f"{DOMAIN}_{self.query_id}"
        self._attr_name = query.get("ha_friendly_name", query["name"])
        self._attr_device_info = DEVICE_INFO

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming event."""
        events = self.events
        if not events:
            return None
        
        # Return the first event (assuming events are sorted by date)
        return events[0]

    @property
    def events(self) -> list[CalendarEvent]:
        """Return all events in the calendar."""
        _LOGGER.debug("Calendar %s: Checking for events", self.query_id)
        _LOGGER.debug("Calendar %s: Coordinator data keys: %s", self.query_id, list(self.coordinator.data.keys()) if self.coordinator.data else "None")
        
        if (
            self.coordinator.data
            and "calendars" in self.coordinator.data
            and self.query_id in self.coordinator.data["calendars"]
        ):
            calendar_data = self.coordinator.data["calendars"][self.query_id]
            _LOGGER.debug("Calendar %s: Found calendar data: %s", self.query_id, type(calendar_data))
            _LOGGER.debug("Calendar %s: Calendar data content: %s", self.query_id, calendar_data)
            events = []
            
            # Handle empty data gracefully
            if not calendar_data or not isinstance(calendar_data, list):
                _LOGGER.debug("Calendar %s: No data or invalid format", self.query_id)
                return events
            
            _LOGGER.debug("Calendar %s: Processing %d events", self.query_id, len(calendar_data))
            
            for event_data in calendar_data:
                try:
                    # Parse event data with better error handling
                    start_date = self._parse_date(event_data.get("dtstart") or event_data.get("start"))
                    if not start_date:
                        _LOGGER.warning("Calendar %s: Event missing start date, skipping", self.query_id)
                        continue
                    
                    # Parse end date, with fallback to start date + 1 day
                    end_date = self._parse_date(event_data.get("dtend") or event_data.get("end"))
                    if not end_date:
                        # If no end date, set to start date + 1 day (default duration)
                        end_date = start_date + timedelta(days=1)
                        _LOGGER.debug("Calendar %s: Event missing end date, using start + 1 day", self.query_id)
                    
                    # Create calendar event with enhanced attributes
                    event = CalendarEvent(
                        summary=self._get_event_summary(event_data),
                        start=start_date,
                        end=end_date,
                        description=self._get_event_description(event_data),
                        location=self._get_event_location(event_data),
                        uid=str(event_data.get("id", "")),
                    )
                    
                    events.append(event)
                    
                except Exception as e:
                    _LOGGER.error("Calendar %s: Error processing event %s: %s", self.query_id, event_data, e)
                    continue
            
            # Sort events by start date
            events.sort(key=lambda x: x.start)
            _LOGGER.debug("Calendar %s: Successfully processed %d events", self.query_id, len(events))
            return events
        
        return []

    def _get_event_summary(self, event_data: dict) -> str:
        """Extract event summary from event data."""
        # Try multiple possible summary fields
        summary_fields = ["summary", "title", "name", "description", "memo"]
        
        for field in summary_fields:
            if field in event_data and event_data[field]:
                summary = str(event_data[field])
                if summary.strip():
                    return summary.strip()
        
        # Fallback to query name if no summary found
        return f"{self.query.get('name', 'Finance Event')}"

    def _get_event_description(self, event_data: dict) -> str | None:
        """Extract event description from event data."""
        # Try multiple possible description fields
        desc_fields = ["description", "memo", "notes", "details", "summary"]
        
        for field in desc_fields:
            if field in event_data and event_data[field]:
                desc = str(event_data[field])
                if desc.strip():
                    return desc.strip()
        
        return None

    def _get_event_location(self, event_data: dict) -> str | None:
        """Extract event location from event data."""
        # Try multiple possible location fields
        location_fields = ["location", "place", "address", "venue"]
        
        for field in location_fields:
            if field in event_data and event_data[field]:
                location = str(event_data[field])
                if location.strip():
                    return location.strip()
        
        return None

    def _parse_date(self, date_value) -> datetime | None:
        """Parse date from various formats with enhanced error handling."""
        if not date_value:
            return None
        
        try:
            # Import dt_util for timezone handling
            from homeassistant.util import dt as dt_util
            # Handle datetime objects directly
            if isinstance(date_value, datetime):
                # Ensure timezone awareness
                if date_value.tzinfo is None:
                    return dt_util.as_local(date_value)
                return date_value
            
            # Handle date objects
            if hasattr(date_value, 'date'):  # datetime.date objects
                naive_dt = datetime.combine(date_value, datetime.min.time())
                return dt_util.as_local(naive_dt)
            
            # Handle string dates
            if isinstance(date_value, str):
                # Remove any timezone info for now (can be enhanced later)
                date_str = date_value.split('+')[0].split('Z')[0].strip()
                
                # Try multiple date formats
                date_formats = [
                    "%Y-%m-%dT%H:%M:%S",      # ISO format without timezone
                    "%Y-%m-%d %H:%M:%S",      # Space-separated format
                    "%Y-%m-%dT%H:%M",         # ISO format without seconds
                    "%Y-%m-%d %H:%M",         # Space-separated without seconds
                    "%Y-%m-%d",               # Date only
                    "%m/%d/%Y",               # US format
                    "%d/%m/%Y",               # European format
                    "%Y-%m-%d %H:%M:%S.%f",  # With microseconds
                ]
                
                for fmt in date_formats:
                    try:
                        naive_dt = datetime.strptime(date_str, fmt)
                        return dt_util.as_local(naive_dt)
                    except ValueError:
                        continue
                
                # If no format works, try to parse with dateutil (if available)
                try:
                    from dateutil import parser
                    naive_dt = parser.parse(date_str)
                    return dt_util.as_local(naive_dt)
                except ImportError:
                    pass
                
                _LOGGER.warning("Calendar %s: Could not parse date string: %s", self.query_id, date_value)
                return None
            
            # Handle numeric timestamps
            if isinstance(date_value, (int, float)):
                try:
                    # Try as Unix timestamp (seconds since epoch)
                    if date_value > 1e10:  # Likely milliseconds
                        date_value = date_value / 1000
                    naive_dt = datetime.fromtimestamp(date_value)
                    return dt_util.as_local(naive_dt)
                except (ValueError, OSError):
                    pass
            
            # Handle dict objects with date components
            if isinstance(date_value, dict):
                # Look for common date fields
                if "year" in date_value and "month" in date_value and "day" in date_value:
                    year = int(date_value["year"])
                    month = int(date_value["month"])
                    day = int(date_value["day"])
                    
                    # Handle optional time components
                    hour = int(date_value.get("hour", 0))
                    minute = int(date_value.get("minute", 0))
                    second = int(date_value.get("second", 0))
                    
                    naive_dt = datetime(year, month, day, hour, minute, second)
                    return dt_util.as_local(naive_dt)
                
                # Try to extract from other common fields
                for key in ["date", "time", "timestamp"]:
                    if key in date_value:
                        parsed = self._parse_date(date_value[key])
                        if parsed:
                            return parsed
            
            _LOGGER.warning("Calendar %s: Unsupported date format: %s (type: %s)", 
                           self.query_id, date_value, type(date_value))
            return None
            
        except Exception as e:
            _LOGGER.error("Calendar %s: Error parsing date %s: %s", self.query_id, date_value, e)
            return None

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        """Return calendar events within a datetime range."""
        events = self.events
        
        # Filter events within the specified range
        filtered_events = []
        for event in events:
            # Check if event overlaps with the specified range
            if (event.start <= end_date and event.end >= start_date):
                filtered_events.append(event)
        
        _LOGGER.debug("Calendar %s: Returning %d events between %s and %s", 
                     self.query_id, len(filtered_events), start_date, end_date)
        return filtered_events

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        if not self.coordinator.data or "calendars" not in self.coordinator.data:
            return {}
            
        calendar_data = self.coordinator.data["calendars"].get(self.query_id, [])
        
        attributes = {
            ATTR_QUERY_ID: self.query_id,
            ATTR_QUERY_NAME: self.query.get("name", ""),
            ATTR_QUERY_DESCRIPTION: self.query.get("description", ""),
            ATTR_QUERY_TYPE: self.query.get("query_type", ""),
            ATTR_LAST_UPDATED: self.coordinator.last_update_success,
            "data_source": "query",
            "event_count": len(calendar_data) if isinstance(calendar_data, list) else 0,
        }
        
        # Add query-specific attributes
        if self.query.get("ha_entity_id"):
            attributes["entity_id"] = self.query["ha_entity_id"]
        
        # Add calendar data context if available
        if calendar_data and isinstance(calendar_data, list):
            # Add sample event data (first few events)
            if len(calendar_data) > 0:
                sample_events = []
                for event in calendar_data[:3]:  # First 3 events
                    sample_event = {
                        "summary": self._get_event_summary(event),
                        "start": str(event.get("start", event.get("dtstart", ""))),
                        "end": str(event.get("end", event.get("dtend", ""))),
                    }
                    sample_events.append(sample_event)
                attributes["sample_events"] = sample_events
            
            # Add event statistics
            if len(calendar_data) > 0:
                try:
                    # Calculate date range of events
                    dates = []
                    for event in calendar_data:
                        start_date = self._parse_date(event.get("start") or event.get("dtstart"))
                        if start_date:
                            dates.append(start_date)
                    
                    if dates:
                        min_date = min(dates)
                        max_date = max(dates)
                        attributes.update({
                            "earliest_event": min_date.isoformat(),
                            "latest_event": max_date.isoformat(),
                            "date_range_days": (max_date - min_date).days,
                        })
                except Exception as e:
                    _LOGGER.debug("Calendar %s: Could not calculate event statistics: %s", self.query_id, e)
        
        return attributes

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        ) 