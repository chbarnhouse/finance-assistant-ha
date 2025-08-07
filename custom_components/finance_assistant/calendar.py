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
    ATTR_DATA_SOURCE,
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
            if query.get("query_type") == "CALENDAR":
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
    def events(self) -> list[CalendarEvent]:
        """Return all events in the calendar."""
        if (
            self.coordinator.data
            and "calendars" in self.coordinator.data
            and self.query_id in self.coordinator.data["calendars"]
        ):
            calendar_data = self.coordinator.data["calendars"][self.query_id]
            events = []
            
            for event_data in calendar_data:
                try:
                    # Parse event data
                    start_date = event_data.get("dtstart")
                    if start_date:
                        if isinstance(start_date, str):
                            start_date = dt_util.parse_datetime(start_date)
                        elif isinstance(start_date, dict):
                            # Handle date dict format
                            start_date = datetime(
                                start_date.get("year"),
                                start_date.get("month"),
                                start_date.get("day")
                            )
                    
                    end_date = event_data.get("dtend")
                    if end_date:
                        if isinstance(end_date, str):
                            end_date = dt_util.parse_datetime(end_date)
                        elif isinstance(end_date, dict):
                            end_date = datetime(
                                end_date.get("year"),
                                end_date.get("month"),
                                end_date.get("day")
                            )
                    
                    # If no end date, set to start date + 1 day
                    if start_date and not end_date:
                        end_date = start_date + timedelta(days=1)
                    
                    event = CalendarEvent(
                        summary=event_data.get("summary", ""),
                        description=event_data.get("description", ""),
                        location=event_data.get("location", ""),
                        start=start_date,
                        end=end_date,
                        uid=event_data.get("uid", f"{self.query_id}_{start_date}"),
                    )
                    events.append(event)
                    
                except Exception as e:
                    _LOGGER.error("Error parsing calendar event: %s", e)
                    continue
            
            return events
        
        return []

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
            ATTR_DATA_SOURCE: self.query.get("data_source", ""),
            ATTR_QUERY_TYPE: self.query.get("query_type", ""),
        }

        # Add last updated timestamp
        if self.coordinator.last_update_success:
            attrs[ATTR_LAST_UPDATED] = self.coordinator.last_update_success.isoformat()

        # Add calendar-specific attributes
        attrs["event_count"] = len(self.events)

        return attrs

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