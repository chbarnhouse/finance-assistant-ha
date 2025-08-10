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
            _LOGGER.debug("Sensor %s data: %s", self.query_id, sensor_data)
            
            # Handle different data formats
            if isinstance(sensor_data, dict):
                value = sensor_data.get("state", sensor_data.get("value", 0))
                _LOGGER.debug("Sensor %s dict value: %s", self.query_id, value)
                return value
            elif isinstance(sensor_data, (int, float)):
                _LOGGER.debug("Sensor %s numeric value: %s", self.query_id, sensor_data)
                return sensor_data
            elif isinstance(sensor_data, list) and len(sensor_data) > 0:
                # If it's a list, calculate the total value
                total = 0
                for item in sensor_data:
                    if isinstance(item, dict):
                        # Handle different field names for values
                        value = item.get("value", item.get("state", item.get("balance", 0)))
                        if isinstance(value, (int, float)):
                            total += value
                    elif isinstance(item, (int, float)):
                        total += item
                _LOGGER.debug("Sensor %s list total: %s", self.query_id, total)
                return total
        else:
            _LOGGER.debug("Sensor %s no data available", self.query_id)
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