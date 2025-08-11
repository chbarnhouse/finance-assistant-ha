"""Sensor platform for Finance Assistant integration."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

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
    """Set up Finance Assistant sensor based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # Define dashboard sensor names to avoid conflicts
    dashboard_sensor_names = {
        "Net Worth",
        "Total Assets", 
        "Total Liabilities",
        "Total Account Balance"
    }
    
    # Create sensors for each SENSOR query (skip conflicting names)
    sensors = []
    if coordinator.data and "queries" in coordinator.data:
        for query in coordinator.data["queries"]:
            if query.get("output_type") == "SENSOR":
                # Skip queries that have the same name as dashboard sensors
                query_name = query.get("ha_friendly_name") or query.get("name", "")
                if query_name not in dashboard_sensor_names:
                    sensor = FinanceAssistantSensor(coordinator, query)
                    sensors.append(sensor)
                else:
                    _LOGGER.debug("Skipping query sensor '%s' - conflicts with dashboard sensor", query_name)
    
    # Add dashboard sensors for real-time financial data
    dashboard_sensors = [
        DashboardSensor(coordinator, "Net Worth", "net_worth", "Net Worth"),
        DashboardSensor(coordinator, "Total Assets", "total_assets", "Total Assets"),
        DashboardSensor(coordinator, "Total Liabilities", "total_liabilities", "Total Liabilities"),
        DashboardSensor(coordinator, "Total Account Balance", "total_account_balance", "Total Account Balance"),
    ]
    
    sensors.extend(dashboard_sensors)
    async_add_entities(sensors)


class DashboardSensor(SensorEntity):
    """Representation of a Finance Assistant dashboard sensor."""
    
    def __init__(self, coordinator, name: str, key: str, friendly_name: str) -> None:
        """Initialize the dashboard sensor."""
        self.coordinator = coordinator
        self._attr_unique_id = f"{DOMAIN}_dashboard_{key}"
        self._attr_name = friendly_name
        self._attr_device_info = DEVICE_INFO
        self.key = key
        
    @property
    def state(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data or "dashboard" not in self.coordinator.data:
            return None
            
        dashboard_data = self.coordinator.data["dashboard"]
        
        try:
            if self.key == "net_worth":
                return self._extract_numeric_value(dashboard_data.get("net_worth"))
            elif self.key == "total_assets":
                return self._extract_numeric_value(dashboard_data.get("total_assets"))
            elif self.key == "total_liabilities":
                return self._extract_numeric_value(dashboard_data.get("total_liabilities"))
            elif self.key == "total_account_balance":
                # Try to get from accounts summary
                accounts_summary = dashboard_data.get("accounts_summary", {})
                return self._extract_numeric_value(accounts_summary.get("total_balance"))
            return None
        except Exception as e:
            _LOGGER.error("Error extracting dashboard value for %s: %s", self.key, e)
            return None
    
    def _extract_numeric_value(self, value) -> float | None:
        """Extract numeric value from various formats."""
        if value is None:
            return None
            
        try:
            if isinstance(value, (int, float)):
                return float(value)
            elif isinstance(value, str):
                # Remove currency symbols and formatting
                cleaned = value.replace('$', '').replace(',', '').replace(' ', '').strip()
                if cleaned:
                    return float(cleaned)
            return None
        except (ValueError, TypeError):
            return None
    
    @property
    def device_class(self) -> SensorDeviceClass | None:
        """Return the device class of the sensor."""
        return SensorDeviceClass.MONETARY
    
    @property
    def state_class(self) -> SensorStateClass | None:
        """Return the state class of the sensor."""
        return SensorStateClass.MEASUREMENT
    
    @property
    def unit_of_measurement(self) -> str | None:
        """Return the unit of measurement."""
        return "USD"
    
    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success


class FinanceAssistantSensor(SensorEntity):
    """Representation of a Finance Assistant sensor."""

    def __init__(self, coordinator, query: dict[str, Any]) -> None:
        """Initialize the sensor."""
        self.coordinator = coordinator
        self.query = query
        self.query_id = query["id"]
        self._attr_unique_id = f"{DOMAIN}_{self.query_id}"
        self._attr_name = query.get("ha_friendly_name", query["name"])
        self._attr_device_info = DEVICE_INFO

    @property
    def state(self) -> StateType:
        """Return the state of the sensor."""
        if (
            self.coordinator.data
            and "sensors" in self.coordinator.data
            and self.query_id in self.coordinator.data["sensors"]
        ):
            sensor_data = self.coordinator.data["sensors"][self.query_id]
            _LOGGER.debug("Sensor %s data: %s", self.query_id, sensor_data)
            
            # Handle different data formats with better error handling
            try:
                if isinstance(sensor_data, dict):
                    # Try multiple possible value fields
                    value = sensor_data.get("state") or sensor_data.get("value") or sensor_data.get("amount") or sensor_data.get("balance")
                    if value is not None:
                        # Convert to numeric if possible
                        numeric_value = self._convert_to_numeric(value)
                        if numeric_value is not None:
                            _LOGGER.debug("Sensor %s dict value: %s", self.query_id, numeric_value)
                            return numeric_value
                    
                    # If no direct value, try to calculate from nested data
                    calculated_value = self._calculate_from_dict(sensor_data)
                    if calculated_value is not None:
                        _LOGGER.debug("Sensor %s calculated value: %s", self.query_id, calculated_value)
                        return calculated_value
                    
                    _LOGGER.warning("Sensor %s: Could not extract value from dict", self.query_id)
                    return 0
                    
                elif isinstance(sensor_data, (int, float)):
                    _LOGGER.debug("Sensor %s numeric value: %s", self.query_id, sensor_data)
                    return sensor_data
                    
                elif isinstance(sensor_data, list) and len(sensor_data) > 0:
                    # If it's a list, calculate the total value
                    total = self._calculate_list_total(sensor_data)
                    _LOGGER.debug("Sensor %s list total: %s", self.query_id, total)
                    return total
                    
                elif isinstance(sensor_data, str):
                    # Try to convert string to numeric
                    numeric_value = self._convert_to_numeric(sensor_data)
                    if numeric_value is not None:
                        _LOGGER.debug("Sensor %s string value: %s", self.query_id, numeric_value)
                        return numeric_value
                    
                    _LOGGER.warning("Sensor %s: Could not convert string to numeric: %s", self.query_id, sensor_data)
                    return 0
                else:
                    _LOGGER.warning("Sensor %s: Unsupported data type: %s", self.query_id, type(sensor_data))
                    return 0
                    
            except Exception as e:
                _LOGGER.error("Sensor %s: Error processing data: %s", self.query_id, e)
                return 0
        else:
            _LOGGER.debug("Sensor %s: No data available", self.query_id)
            return 0

    def _convert_to_numeric(self, value) -> float | None:
        """Convert value to numeric if possible."""
        if value is None:
            return None
            
        try:
            if isinstance(value, (int, float)):
                return float(value)
            elif isinstance(value, str):
                # Remove common currency symbols and whitespace
                cleaned = value.replace('$', '').replace(',', '').replace(' ', '').strip()
                if cleaned:
                    return float(cleaned)
            return None
        except (ValueError, TypeError):
            return None

    def _calculate_from_dict(self, data: dict) -> float | None:
        """Calculate value from dictionary data."""
        try:
            # Look for common financial fields
            financial_fields = ['amount', 'balance', 'total', 'sum', 'value', 'state']
            for field in financial_fields:
                if field in data:
                    value = self._convert_to_numeric(data[field])
                    if value is not None:
                        return value
            
            # If no direct financial fields, try to sum numeric values
            total = 0
            count = 0
            for key, value in data.items():
                if isinstance(value, (int, float)):
                    total += value
                    count += 1
                elif isinstance(value, str):
                    numeric_value = self._convert_to_numeric(value)
                    if numeric_value is not None:
                        total += numeric_value
                        count += 1
            
            return total if count > 0 else None
            
        except Exception as e:
            _LOGGER.debug("Sensor %s: Error calculating from dict: %s", self.query_id, e)
            return None

    def _calculate_list_total(self, data_list: list) -> float:
        """Calculate total from list of data items."""
        try:
            total = 0
            for item in data_list:
                if isinstance(item, dict):
                    # Handle different field names for values
                    value = item.get("value") or item.get("state") or item.get("balance") or item.get("amount")
                    if value is not None:
                        numeric_value = self._convert_to_numeric(value)
                        if numeric_value is not None:
                            total += numeric_value
                elif isinstance(item, (int, float)):
                    total += item
                elif isinstance(item, str):
                    numeric_value = self._convert_to_numeric(item)
                    if numeric_value is not None:
                        total += numeric_value
            
            return total
        except Exception as e:
            _LOGGER.error("Sensor %s: Error calculating list total: %s", self.query_id, e)
            return 0

    @property
    def native_value(self) -> StateType:
        """Return the native value of the sensor."""
        return self.state

    @property
    def device_class(self) -> SensorDeviceClass | None:
        """Return the device class of the sensor."""
        # Use monetary device class for financial sensors
        return SensorDeviceClass.MONETARY

    @property
    def state_class(self) -> SensorStateClass | None:
        """Return the state class of the sensor."""
        # Determine state class based on query type
        if self.query.get("query_type") == "TRANSACTIONS":
            return SensorStateClass.TOTAL
        elif self.query.get("query_type") == "ACCOUNTS":
            return SensorStateClass.MEASUREMENT
        return None

    @property
    def unit_of_measurement(self) -> str | None:
        """Return the unit of measurement."""
        # Use the unit from the query configuration, fallback to defaults
        unit = self.query.get("ha_unit_of_measurement")
        if unit:
            return unit
        
        # Default to USD for financial sensors
        return "USD"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        if not self.coordinator.data or "queries" not in self.coordinator.data:
            return {}
            
        # Find the query data
        queries = self.coordinator.data["queries"]
        query_data = None
        for query in queries:
            if query["id"] == self.query_id:
                query_data = query
                break
                
        if not query_data:
            return {}
            
        attributes = {
            ATTR_QUERY_ID: self.query_id,
            ATTR_QUERY_NAME: query_data.get("name", "Unknown"),
            ATTR_QUERY_DESCRIPTION: query_data.get("description", ""),
            ATTR_QUERY_TYPE: query_data.get("query_type", "Unknown"),
            ATTR_LAST_UPDATED: datetime.now().isoformat(),
        }
        
        # Add query-specific attributes
        if query_data.get("ha_friendly_name"):
            attributes["ha_friendly_name"] = query_data["ha_friendly_name"]
        if query_data.get("ha_unit_of_measurement"):
            attributes["ha_unit_of_measurement"] = query_data["ha_unit_of_measurement"]
            
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