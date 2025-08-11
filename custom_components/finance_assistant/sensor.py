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

    # Create sensors for each SENSOR query
    sensors = []
    if coordinator.data and "queries" in coordinator.data:
        for query in coordinator.data["queries"]:
            if query.get("output_type") == "SENSOR":
                sensor = FinanceAssistantSensor(coordinator, query)
                sensors.append(sensor)

    async_add_entities(sensors)


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
            _LOGGER.info("=== SENSOR DEBUG START ===")
            _LOGGER.info("Sensor %s (%s) raw data: %s", self.query_id, self.name, sensor_data)
            _LOGGER.info("Sensor %s data type: %s", self.query_id, type(sensor_data))
            
            # Handle different data formats with better error handling
            try:
                if isinstance(sensor_data, dict):
                    _LOGGER.info("Sensor %s: Processing as DICT", self.query_id)
                    _LOGGER.info("Sensor %s: Dict keys: %s", self.query_id, list(sensor_data.keys()))
                    
                    # Try multiple possible value fields
                    value = sensor_data.get("state") or sensor_data.get("value") or sensor_data.get("amount") or sensor_data.get("balance")
                    _LOGGER.info("Sensor %s: Direct value fields - state: %s, value: %s, amount: %s, balance: %s", 
                                self.query_id, sensor_data.get("state"), sensor_data.get("value"), 
                                sensor_data.get("amount"), sensor_data.get("balance"))
                    
                    if value is not None:
                        _LOGGER.info("Sensor %s: Found direct value: %s (type: %s)", self.query_id, value, type(value))
                        # Convert to numeric if possible
                        numeric_value = self._convert_to_numeric(value)
                        if numeric_value is not None:
                            _LOGGER.info("Sensor %s: Converted to numeric: %s", self.query_id, numeric_value)
                            _LOGGER.info("=== SENSOR DEBUG END ===")
                            return numeric_value
                        else:
                            _LOGGER.warning("Sensor %s: Failed to convert value to numeric: %s", self.query_id, value)
                    
                    # If no direct value, try to calculate from nested data
                    _LOGGER.info("Sensor %s: Trying to calculate from dict data", self.query_id)
                    calculated_value = self._calculate_from_dict(sensor_data)
                    if calculated_value is not None:
                        _LOGGER.info("Sensor %s: Calculated value: %s", self.query_id, calculated_value)
                        _LOGGER.info("=== SENSOR DEBUG END ===")
                        return calculated_value
                    
                    _LOGGER.warning("Sensor %s: Could not extract value from dict", self.query_id)
                    _LOGGER.info("=== SENSOR DEBUG END ===")
                    return 0
                    
                elif isinstance(sensor_data, (int, float)):
                    _LOGGER.info("Sensor %s: Processing as NUMERIC: %s", self.query_id, sensor_data)
                    _LOGGER.info("=== SENSOR DEBUG END ===")
                    return sensor_data
                    
                elif isinstance(sensor_data, list) and len(sensor_data) > 0:
                    _LOGGER.info("Sensor %s: Processing as LIST with %d items", self.query_id, len(sensor_data))
                    _LOGGER.info("Sensor %s: List items: %s", self.query_id, sensor_data)
                    # If it's a list, calculate the total value
                    total = self._calculate_list_total(sensor_data)
                    _LOGGER.info("Sensor %s: List total calculated: %s", self.query_id, total)
                    _LOGGER.info("=== SENSOR DEBUG END ===")
                    return total
                    
                elif isinstance(sensor_data, str):
                    _LOGGER.info("Sensor %s: Processing as STRING: %s", self.query_id, sensor_data)
                    # Try to parse string as numeric
                    numeric_value = self._convert_to_numeric(sensor_data)
                    if numeric_value is not None:
                        _LOGGER.info("Sensor %s: String converted to numeric: %s", self.query_id, numeric_value)
                        _LOGGER.info("=== SENSOR DEBUG END ===")
                        return numeric_value
                    _LOGGER.warning("Sensor %s: Could not parse string value: %s", self.query_id, sensor_data)
                    _LOGGER.info("=== SENSOR DEBUG END ===")
                    return 0
                    
                else:
                    _LOGGER.warning("Sensor %s: Unsupported data type: %s", self.query_id, type(sensor_data))
                    _LOGGER.info("=== SENSOR DEBUG END ===")
                    return 0
                    
            except Exception as e:
                _LOGGER.error("Sensor %s: Error processing data: %s", self.query_id, e)
                _LOGGER.info("=== SENSOR DEBUG END ===")
                return 0
        else:
            _LOGGER.warning("Sensor %s: No data available in coordinator", self.query_id)
            if self.coordinator.data:
                _LOGGER.info("Coordinator data keys: %s", list(self.coordinator.data.keys()))
                if "sensors" in self.coordinator.data:
                    _LOGGER.info("Available sensor IDs: %s", list(self.coordinator.data["sensors"].keys()))
            _LOGGER.info("=== SENSOR DEBUG END ===")
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
        
        # Fallback to defaults based on query type
        if self.query.get("query_type") == "TRANSACTIONS":
            return "USD"  # Default to USD for transaction amounts
        elif self.query.get("query_type") == "ACCOUNTS":
            return "USD"  # Default to USD for account balances
        return None

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

        # Add sensor-specific attributes from the data
        if (
            self.coordinator.data
            and "sensors" in self.coordinator.data
            and self.query_id in self.coordinator.data["sensors"]
        ):
            sensor_data = self.coordinator.data["sensors"][self.query_id]
            if "attributes" in sensor_data:
                attrs.update(sensor_data["attributes"])

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