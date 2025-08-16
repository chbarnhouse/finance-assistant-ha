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
    ATTR_LAST_UPDATED,
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
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    # Create basic financial calendar
    calendars = []
    
    # Create a single calendar for financial events
    calendar = FinanceAssistantCalendar(coordinator)
    calendars.append(calendar)

    async_add_entities(calendars)


class FinanceAssistantCalendar(CalendarEntity):
    """Representation of a Finance Assistant calendar."""

    def __init__(self, coordinator) -> None:
        """Initialize the calendar."""
        self.coordinator = coordinator
        self._attr_unique_id = f"{DOMAIN}_financial_calendar"
        self._attr_name = "Finance Assistant Calendar"
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
        _LOGGER.debug("Finance Assistant Calendar: Checking for events")
        _LOGGER.debug("Finance Assistant Calendar: Coordinator data keys: %s", list(self.coordinator.data.keys()) if self.coordinator.data else "None")
        
        # For now, return empty events list since we don't have calendar data
        # This will be populated when we implement actual calendar functionality
        _LOGGER.debug("Finance Assistant Calendar: No calendar data available yet")
        
        return []

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        """Return calendar events within a datetime range."""
        events = self.events
        
        # Filter events within the specified range
        filtered_events = []
        for event in events:
            # Check if event overlaps with the specified range
            # Convert datetime objects to date objects for comparison if needed
            event_start = event.start
            event_end = event.end
            
            # Convert request dates to date objects for comparison
            request_start = start_date.date() if hasattr(start_date, 'date') else start_date
            request_end = end_date.date() if hasattr(end_date, 'date') else end_date
            
            # Check if event overlaps with the specified range
            if (event_start <= request_end and event_end >= request_start):
                filtered_events.append(event)
        
        _LOGGER.debug("Finance Assistant Calendar: Returning %d events between %s and %s", 
                     len(filtered_events), start_date, end_date)
        return filtered_events

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        attributes = {
            ATTR_LAST_UPDATED: self.coordinator.last_update_success,
            "data_source": "finance_assistant",
            "event_count": 0,  # No events yet
        }
        
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