"""Data coordinator for Finance Assistant integration."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.exceptions import HomeAssistantError

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
                    if response.status == 401:
                        _LOGGER.error("Invalid API key")
                        raise InvalidAuth()
                    elif response.status != 200:
                        _LOGGER.error("Connection failed with status: %s", response.status)
                        raise CannotConnect()
        except aiohttp.ClientError as err:
            _LOGGER.error("Error connecting to Finance Assistant: %s", err)
            raise CannotConnect() from err

    async def _async_update_data(self) -> Dict[str, Any]:
        """Update data via API with enhanced error handling and retry logic."""
        try:
            async with aiohttp.ClientSession() as session:
                # Prepare headers with required API key
                headers = {"X-API-Key": self.api_key}
                _LOGGER.debug("Using API key for authentication")
                
                # Get available queries
                queries_url = f"{self.base_url}{API_ENDPOINT_QUERIES}"
                queries = await self._fetch_with_retry(session, queries_url, headers, "queries")
                
                # Fetch dashboard data for real-time financial information
                dashboard_url = f"{self.base_url}/api/ha/dashboard/"
                dashboard_data = {}
                try:
                    dashboard_data = await self._fetch_with_retry(session, dashboard_url, headers, "dashboard")
                    _LOGGER.debug("Dashboard data fetched successfully")
                except Exception as e:
                    _LOGGER.warning("Failed to fetch dashboard data: %s", e)
                    # Continue without dashboard data - queries can still work
                
                # Initialize data structure
                data = {
                    "queries": queries,
                    "dashboard": dashboard_data,
                    "sensors": {},
                    "calendars": {},
                    "last_update": datetime.now().isoformat(),
                }
                
                # Fetch sensor data for each SENSOR query
                sensor_queries = [q for q in queries if q.get("output_type") == "SENSOR"]
                _LOGGER.debug("Found %d sensor queries to fetch", len(sensor_queries))
                
                for query in sensor_queries:
                    try:
                        sensor_data = await self.get_sensor_data(query["id"])
                        if sensor_data:
                            data["sensors"][str(query["id"])] = sensor_data
                    except Exception as e:
                        _LOGGER.warning("Failed to fetch sensor data for query %s: %s", query["id"], e)
                        # Continue with other queries
                
                # Fetch calendar data for each CALENDAR query
                calendar_queries = [q for q in queries if q.get("output_type") == "CALENDAR"]
                _LOGGER.debug("Found %d calendar queries to fetch", len(calendar_queries))
                
                for query in calendar_queries:
                    try:
                        calendar_data = await self.get_calendar_data(query["id"])
                        if calendar_data:
                            data["calendars"][str(query["id"])] = calendar_data
                    except Exception as e:
                        _LOGGER.warning("Failed to fetch calendar data for query %s: %s", query["id"], e)
                        # Continue with other queries
                
                _LOGGER.debug("Data update completed successfully")
                return data
                
        except Exception as e:
            _LOGGER.error("Error updating Finance Assistant data: %s", e)
            raise UpdateFailed(f"Failed to update Finance Assistant data: {e}")

    async def _fetch_with_retry(self, session: aiohttp.ClientSession, url: str, headers: Dict[str, str], data_type: str, max_retries: int = 3) -> Any:
        """Fetch data with retry logic and better error handling."""
        last_error = None
        
        for attempt in range(max_retries):
            try:
                timeout = aiohttp.ClientTimeout(total=30)  # 30 second timeout
                async with session.get(url, headers=headers, timeout=timeout) as response:
                    if response.status == 200:
                        data = await response.json()
                        _LOGGER.debug("Successfully fetched %s data on attempt %d", data_type, attempt + 1)
                        return data
                    elif response.status == 401:
                        _LOGGER.error("Authentication failed for %s: Invalid API key", data_type)
                        raise InvalidAuth()
                    elif response.status == 404:
                        _LOGGER.error("Endpoint not found for %s: %s", data_type, url)
                        raise CannotConnect()
                    elif response.status >= 500:
                        _LOGGER.warning("Server error for %s (attempt %d/%d): %s", data_type, attempt + 1, max_retries, response.status)
                        if attempt < max_retries - 1:
                            await asyncio.sleep(2 ** attempt)  # Exponential backoff
                            continue
                        else:
                            raise UpdateFailed(f"Server error after {max_retries} attempts: {response.status}")
                    else:
                        _LOGGER.error("HTTP error for %s: %s", data_type, response.status)
                        raise UpdateFailed(f"HTTP error {response.status} for {data_type}")
                        
            except aiohttp.ClientError as e:
                last_error = e
                _LOGGER.warning("Network error for %s (attempt %d/%d): %s", data_type, attempt + 1, max_retries, e)
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    raise CannotConnect() from e
            except asyncio.TimeoutError:
                last_error = "Request timeout"
                _LOGGER.warning("Timeout for %s (attempt %d/%d)", data_type, attempt + 1, max_retries)
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    raise UpdateFailed(f"Request timeout after {max_retries} attempts")
            except Exception as e:
                last_error = e
                _LOGGER.error("Unexpected error for %s (attempt %d/%d): %s", data_type, attempt + 1, max_retries, e)
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    raise UpdateFailed(f"Unexpected error after {max_retries} attempts: {e}")
        
        # If we get here, all retries failed
        raise UpdateFailed(f"Failed to fetch {data_type} after {max_retries} attempts. Last error: {last_error}")

    async def get_sensor_data(self, query_id: str) -> Dict[str, Any]:
        """Get sensor data for a specific query with enhanced error handling."""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}{API_ENDPOINT_SENSOR.format(query_id=query_id)}"
                headers = {"X-API-Key": self.api_key}
                
                timeout = aiohttp.ClientTimeout(total=15)  # 15 second timeout for individual queries
                async with session.get(url, headers=headers, timeout=timeout) as response:
                    if response.status == 200:
                        data = await response.json()
                        _LOGGER.debug("Sensor data for query %s: %s", query_id, data)
                        return data
                    elif response.status == 404:
                        _LOGGER.warning("Query %s not found", query_id)
                        return None
                    else:
                        _LOGGER.warning("Failed to fetch sensor data for query %s: HTTP %s", query_id, response.status)
                        return None
                        
        except aiohttp.ClientError as e:
            _LOGGER.error("Network error fetching sensor data for query %s: %s", query_id, e)
            return None
        except Exception as e:
            _LOGGER.error("Error fetching sensor data for query %s: %s", query_id, e)
            return None

    async def get_calendar_data(self, query_id: str) -> List[Dict[str, Any]]:
        """Get calendar data for a specific query with enhanced error handling."""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}{API_ENDPOINT_CALENDAR.format(query_id=query_id)}"
                headers = {"X-API-Key": self.api_key}
                
                timeout = aiohttp.ClientTimeout(total=15)  # 15 second timeout for individual queries
                async with session.get(url, headers=headers, timeout=timeout) as response:
                    if response.status == 200:
                        data = await response.json()
                        _LOGGER.debug("Calendar data for query %s: %s events", query_id, len(data) if isinstance(data, list) else 0)
                        return data if isinstance(data, list) else []
                    elif response.status == 404:
                        _LOGGER.warning("Query %s not found", query_id)
                        return []
                    else:
                        _LOGGER.warning("Failed to fetch calendar data for query %s: HTTP %s", query_id, response.status)
                        return []
                        
        except aiohttp.ClientError as e:
            _LOGGER.error("Network error fetching calendar data for query %s: %s", query_id, e)
            return []
        except Exception as e:
            _LOGGER.error("Error fetching calendar data for query %s: %s", query_id, e)
            return []


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth.""" 