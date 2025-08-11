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
        if (
            self.coordinator.data
            and "calendars" in self.coordinator.data
            and self.query_id in self.coordinator.data["calendars"]
        ):
            calendar_data = self.coordinator.data["calendars"][self.query_id]
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
                    
                    # Ensure end date is after start date
                    if end_date <= start_date:
                        end_date = start_date + timedelta(days=1)
                        _LOGGER.debug("Calendar %s: End date <= start date, adjusting to start + 1 day", self.query_id)
                    
                    # Create calendar event with required fields
                    event = CalendarEvent(
                        summary=event_data.get("summary", event_data.get("title", "Financial Event")),
                        description=event_data.get("description", ""),
                        location=event_data.get("location", ""),
                        start=start_date,
                        end=end_date,  # Always ensure end is present
                        uid=event_data.get("uid", f"{self.query_id}_{start_date.isoformat()}"),
                    )
                    events.append(event)
                    _LOGGER.debug("Calendar %s: Successfully parsed event: %s", self.query_id, event.summary)
                    
                except Exception as e:
                    _LOGGER.error("Calendar %s: Error parsing calendar event: %s", self.query_id, e)
                    _LOGGER.debug("Calendar %s: Problematic event data: %s", self.query_id, event_data)
                    continue
            
            _LOGGER.debug("Calendar %s: Successfully parsed %d events", self.query_id, len(events))
            return events
        
        return []

    def _parse_date(self, date_value) -> datetime | None:
        """Parse date value from various formats."""
        if not date_value:
            return None
        
        try:
            if isinstance(date_value, str):
                # Try to parse as ISO format first
                parsed = dt_util.parse_datetime(date_value)
                if parsed:
                    return parsed
                
                # Try other common formats
                for fmt in ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"]:
                    try:
                        return datetime.strptime(date_value, fmt)
                    except ValueError:
                        continue
                
                _LOGGER.warning("Calendar %s: Could not parse date string: %s", self.query_id, date_value)
                return None
                
            elif isinstance(date_value, dict):
                # Handle date dict format
                year = date_value.get("year")
                month = date_value.get("month", 1)
                day = date_value.get("day", 1)
                hour = date_value.get("hour", 0)
                minute = date_value.get("minute", 0)
                second = date_value.get("second", 0)
                
                if year and month and day:
                    return datetime(year, month, day, hour, minute, second)
                else:
                    _LOGGER.warning("Calendar %s: Incomplete date dict: %s", self.query_id, date_value)
                    return None
                    
            elif isinstance(date_value, (int, float)):
                # Handle timestamp
                return datetime.fromtimestamp(date_value)
                
            else:
                _LOGGER.warning("Calendar %s: Unsupported date format: %s (%s)", self.query_id, date_value, type(date_value))
                return None
                
        except Exception as e:
            _LOGGER.error("Calendar %s: Error parsing date %s: %s", self.query_id, date_value, e)
            return None

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        """Return calendar events within a datetime range."""
        events = self.events
        filtered_events = []
        
        for event in events:
            if event.start and event.end:
                # Check if event overlaps with the requested range
                if (
                    (event.start <= end_date and event.end >= start_date) or
                    (event.start >= start_date and event.start <= end_date) or
                    (event.end >= start_date and event.end <= end_date)
                ):
                    filtered_events.append(event)
        
        return filtered_events

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        attrs = {
            ATTR_QUERY_ID: self.query_id,
            ATTR_QUERY_NAME: self.query["name"],
            ATTR_QUERY_DESCRIPTION: self.query.get("description", ""),
            ATTR_QUERY_TYPE: self.query.get("query_type", ""),
        }

        # Add last updated timestamp
        if hasattr(self.coordinator, 'last_update_success_time') and self.coordinator.last_update_success_time:
            attrs[ATTR_LAST_UPDATED] = self.coordinator.last_update_success_time.isoformat()

        # Add calendar-specific attributes
        attrs["event_count"] = len(self.events)

        return attrs

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return (
            self.coordinator.last_update_success
            and self.coordinator.data is not None
        )

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        ) 