"""Data coordinator for Finance Assistant integration."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_HOST,
    CONF_PORT,
    CONF_API_KEY,
    CONF_SSL,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    API_ENDPOINT_QUERIES,
    API_ENDPOINT_SENSOR,
    API_ENDPOINT_CALENDAR,
)

_LOGGER = logging.getLogger(__name__)


class FinanceAssistantDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Finance Assistant data."""

    def __init__(self, hass: HomeAssistant, config: Dict[str, Any]) -> None:
        """Initialize."""
        self.config = config
        self.host = config[CONF_HOST]
        self.port = config[CONF_PORT]
        self.api_key = config[CONF_API_KEY]  # Required
        if not self.api_key:
            raise ValueError("API key is required")
        _LOGGER.debug("API key configured: %s", "***" if self.api_key else "NOT SET")
        self.ssl = config[CONF_SSL]
        self.scan_interval = config.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

        # Build base URL
        protocol = "https" if self.ssl else "http"
        self.base_url = f"{protocol}://{self.host}:{self.port}"

        super().__init__(
            hass,
            _LOGGER,
            name="Finance Assistant",
            update_interval=timedelta(seconds=self.scan_interval),
        )

    async def async_validate_input(self) -> None:
        """Validate the user input allows us to connect."""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}{API_ENDPOINT_QUERIES}"
                headers = {"X-API-Key": self.api_key}
                _LOGGER.debug("Validating connection with API key")
                
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        raise CannotConnect()
        except aiohttp.ClientError as err:
            _LOGGER.error("Error connecting to Finance Assistant: %s", err)
            raise CannotConnect() from err

    async def _async_update_data(self) -> Dict[str, Any]:
        """Update data via API."""
        try:
            async with aiohttp.ClientSession() as session:
                # Prepare headers with required API key
                headers = {"X-API-Key": self.api_key}
                _LOGGER.debug("Using API key for authentication")
                
                # Get available queries
                queries_url = f"{self.base_url}{API_ENDPOINT_QUERIES}"
                async with session.get(queries_url, headers=headers) as response:
                    if response.status != 200:
                        raise UpdateFailed(f"Error fetching queries: {response.status}")
                    queries = await response.json()

                # Fetch data for each query
                data = {"queries": queries, "sensors": {}, "calendars": {}}
                
                for query in queries:
                    query_id = query["id"]
                    
                    try:
                        # Fetch sensor data for SENSOR queries
                        if query.get("query_type") == "SENSOR":
                            sensor_url = f"{self.base_url}{API_ENDPOINT_SENSOR.format(query_id=query_id)}"
                            _LOGGER.debug("Fetching sensor data from: %s", sensor_url)
                            async with session.get(sensor_url, headers=headers) as response:
                                if response.status == 200:
                                    sensor_data = await response.json()
                                    data["sensors"][query_id] = sensor_data
                                    _LOGGER.debug("Sensor data for %s: %s", query_id, sensor_data)
                                else:
                                    _LOGGER.warning("Failed to fetch sensor data for %s: %s", query_id, response.status)
                        
                        # Fetch calendar data for CALENDAR queries
                        elif query.get("query_type") == "CALENDAR":
                            calendar_url = f"{self.base_url}{API_ENDPOINT_CALENDAR.format(query_id=query_id)}"
                            _LOGGER.debug("Fetching calendar data from: %s", calendar_url)
                            async with session.get(calendar_url, headers=headers) as response:
                                if response.status == 200:
                                    calendar_data = await response.json()
                                    data["calendars"][query_id] = calendar_data
                                    _LOGGER.debug("Calendar data for %s: %s", query_id, calendar_data)
                                else:
                                    _LOGGER.warning("Failed to fetch calendar data for %s: %s", query_id, response.status)
                    
                    except Exception as e:
                        _LOGGER.error("Error fetching data for query %s: %s", query_id, e)
                        continue

                _LOGGER.debug("Final coordinator data: %s", data)
                return data

        except aiohttp.ClientError as err:
            _LOGGER.error("Error updating Finance Assistant data: %s", err)
            raise UpdateFailed(f"Error communicating with Finance Assistant: {err}") from err
        except Exception as err:
            _LOGGER.error("Unexpected error updating Finance Assistant data: %s", err)
            raise UpdateFailed(f"Unexpected error: {err}") from err

    async def get_sensor_data(self, query_id: str) -> Dict[str, Any]:
        """Get sensor data for a specific query."""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}{API_ENDPOINT_SENSOR.format(query_id=query_id)}"
                headers = {"X-API-Key": self.api_key}
                
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        _LOGGER.error("Error fetching sensor data: %s", response.status)
                        return {}
        except aiohttp.ClientError as err:
            _LOGGER.error("Error fetching sensor data: %s", err)
            return {}

    async def get_calendar_data(self, query_id: str) -> List[Dict[str, Any]]:
        """Get calendar data for a specific query."""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}{API_ENDPOINT_CALENDAR.format(query_id=query_id)}"
                headers = {"X-API-Key": self.api_key}
                
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        _LOGGER.error("Error fetching calendar data: %s", response.status)
                        return []
        except aiohttp.ClientError as err:
            _LOGGER.error("Error fetching calendar data: %s", err)
            return []


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""


class InvalidAuth(Exception):
    """Error to indicate there is invalid auth.""" 