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
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    # Create basic financial sensors
    sensors = []
    
    # Add essential dashboard sensors that provide core financial metrics
    dashboard_sensors = [
        DashboardSensor(coordinator, "Net Worth", "net_worth", "Net Worth"),
        DashboardSensor(coordinator, "Total Assets", "total_assets", "Total Assets"),
        DashboardSensor(coordinator, "Total Liabilities", "total_liabilities", "Total Liabilities"),
    ]
    
    sensors.extend(dashboard_sensors)
    
    # Add enhanced analytics sensors
    from .sensors.enhanced_sensors import (
        CashFlowForecastSensor, FinancialHealthSensor, UpcomingExpensesSensor,
        RecurringObligationsSensor, AccountBalanceSensor, MonthlyBudgetSensor,
        SavingsRateSensor, RiskAssessmentSensor, TransactionStatusSensor,
        SpendingTrendsSensor, ObligationRatioSensor, FinancialInsightsSensor,
        CashFlowTrendSensor, ExpenseTrendSensor, SavingsTrendSensor, HighRiskItemsSensor,
        OverallFinancialScoreSensor, BalanceScoreSensor, CashFlowScoreSensor,
        ExpenseScoreSensor, RecurringScoreSensor, RiskLevelSensor,
        MonthlyObligationsSensor, EssentialObligationsSensor, DiscretionaryObligationsSensor,
        TotalAccountBalanceSensor, ActiveAccountCountSensor, AccountBalanceByTypeSensor,
        TotalIncomeSensor, TotalExpensesSensor, NetCashFlowSensor
    )
    
    # Create enhanced sensor instances
    enhanced_sensors = [
        CashFlowForecastSensor(coordinator),
        FinancialHealthSensor(coordinator),
        UpcomingExpensesSensor(coordinator),
        RecurringObligationsSensor(coordinator),
        AccountBalanceSensor(coordinator),
        MonthlyBudgetSensor(coordinator),
        SavingsRateSensor(coordinator),
        RiskAssessmentSensor(coordinator),
        TransactionStatusSensor(coordinator),
        SpendingTrendsSensor(coordinator),
        ObligationRatioSensor(coordinator),
        FinancialInsightsSensor(coordinator),
        CashFlowTrendSensor(coordinator),
        ExpenseTrendSensor(coordinator),
        SavingsTrendSensor(coordinator),
        HighRiskItemsSensor(coordinator),
        OverallFinancialScoreSensor(coordinator),
        BalanceScoreSensor(coordinator),
        CashFlowScoreSensor(coordinator),
        ExpenseScoreSensor(coordinator),
        RecurringScoreSensor(coordinator),
        RiskLevelSensor(coordinator),
        MonthlyObligationsSensor(coordinator),
        EssentialObligationsSensor(coordinator),
        DiscretionaryObligationsSensor(coordinator),
        TotalAccountBalanceSensor(coordinator),
        ActiveAccountCountSensor(coordinator),
        AccountBalanceByTypeSensor(coordinator),
        TotalIncomeSensor(coordinator),
        TotalExpensesSensor(coordinator),
        NetCashFlowSensor(coordinator),
    ]
    
    # Add all sensors
    all_sensors = dashboard_sensors + enhanced_sensors
    async_add_entities(all_sensors)


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
        """Extract numeric value from various data types."""
        if value is None:
            return None
        
        try:
            if isinstance(value, (int, float)):
                return float(value)
            elif isinstance(value, str):
                # Remove currency symbols and commas, then convert
                cleaned = value.replace('$', '').replace(',', '').replace('(', '').replace(')', '')
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
        """Return the unit of measurement of the sensor."""
        return "USD"
    
    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        if not self.coordinator.data or "dashboard" not in self.coordinator.data:
            return {}
            
        dashboard_data = self.coordinator.data["dashboard"]
        
        # Get additional context based on sensor type
        attributes = {
            "last_updated": self.coordinator.last_update_success,
            "data_source": "dashboard",
        }
        
        if self.key == "net_worth":
            # Add breakdown of net worth components
            accounts_summary = dashboard_data.get("accounts_summary", {})
            credit_cards_summary = dashboard_data.get("credit_cards_summary", {})
            assets_summary = dashboard_data.get("assets_summary", {})
            liabilities_summary = dashboard_data.get("liabilities_summary", {})
            
            attributes.update({
                "accounts_count": accounts_summary.get("count", 0),
                "accounts_total": accounts_summary.get("total_balance", 0),
                "credit_cards_count": credit_cards_summary.get("count", 0),
                "credit_cards_total": credit_cards_summary.get("total_balance", 0),
                "assets_count": assets_summary.get("count", 0),
                "assets_total": assets_summary.get("total_value", 0),
                "liabilities_count": liabilities_summary.get("count", 0),
                "liabilities_total": liabilities_summary.get("total_balance", 0),
            })
        
        return attributes


class FinanceAssistantSensor(SensorEntity):
    """Representation of a Finance Assistant query sensor."""

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
        if not self.coordinator.data or "sensors" not in self.coordinator.data:
            return None
            
        sensor_data = self.coordinator.data["sensors"].get(str(self.query_id))
        if not sensor_data:
            return None
        
        try:
            # The HomeAssistantSensorView returns {"value": value, "unit": "USD"}
            if isinstance(sensor_data, dict) and "value" in sensor_data:
                return self._convert_to_numeric(sensor_data["value"])
            
            # Fallback to old format if "data" field exists
            if isinstance(sensor_data, dict) and "data" in sensor_data:
                data = sensor_data["data"]
                if isinstance(data, list) and len(data) > 0:
                    # If it's a list, try to get the first item's value
                    first_item = data[0]
                    if isinstance(first_item, dict):
                        # Look for common value fields
                        value = first_item.get("value") or first_item.get("balance") or first_item.get("amount") or first_item.get("total")
                        if value is not None:
                            return self._convert_to_numeric(value)
                elif isinstance(data, dict):
                    # If it's a dict, look for value fields
                    value = data.get("value") or data.get("balance") or data.get("amount") or data.get("total")
                    if value is not None:
                        return self._convert_to_numeric(value)
                elif isinstance(data, (int, float)):
                    # If it's already a number
                    return self._convert_to_numeric(data)
                elif isinstance(data, str):
                    # If it's a string, try to parse it
                    return self._convert_to_numeric(data)
            elif isinstance(sensor_data, (int, float)):
                # Direct numeric value
                return self._convert_to_numeric(sensor_data)
            elif isinstance(sensor_data, str):
                # String value, try to parse
                return self._convert_to_numeric(sensor_data)
            elif isinstance(sensor_data, list):
                # List of data, try to calculate total
                return self._calculate_list_total(sensor_data)
            elif isinstance(sensor_data, dict):
                # Dict data, try to extract or calculate
                return self._calculate_from_dict(sensor_data)
            
            return None
        except Exception as e:
            _LOGGER.error("Error extracting sensor value for query %s: %s", self.query_id, e)
            return None

    def _convert_to_numeric(self, value) -> float | None:
        """Convert various value types to numeric."""
        if value is None:
            return None
        
        try:
            if isinstance(value, (int, float)):
                return float(value)
            elif isinstance(value, str):
                # Remove currency symbols, commas, and parentheses
                cleaned = value.replace('$', '').replace(',', '').replace('(', '').replace(')', '')
                # Handle negative values in parentheses
                if cleaned.startswith('-') or cleaned.startswith('−'):
                    cleaned = '-' + cleaned[1:]
                return float(cleaned)
            return None
        except (ValueError, TypeError):
            return None

    def _calculate_from_dict(self, data: dict) -> float | None:
        """Calculate total from dictionary data."""
        try:
            total = 0.0
            # Look for common numeric fields
            numeric_fields = ["value", "balance", "amount", "total", "sum", "count"]
            
            for field in numeric_fields:
                if field in data:
                    value = data[field]
                    if isinstance(value, (int, float)):
                        total += float(value)
                    elif isinstance(value, str):
                        parsed = self._convert_to_numeric(value)
                        if parsed is not None:
                            total += parsed
            
            return total if total != 0 else None
        except Exception as e:
            _LOGGER.error("Error calculating from dict: %s", e)
            return None

    def _calculate_list_total(self, data_list: list) -> float:
        """Calculate total from list of data."""
        try:
            total = 0.0
            for item in data_list:
                if isinstance(item, dict):
                    # Try to extract numeric value from dict item
                    value = self._calculate_from_dict(item)
                    if value is not None:
                        total += value
                elif isinstance(item, (int, float)):
                    total += float(item)
                elif isinstance(item, str):
                    parsed = self._convert_to_numeric(item)
                    if parsed is not None:
                        total += parsed
            
            return total
        except Exception as e:
            _LOGGER.error("Error calculating list total: %s", e)
            return 0.0

    @property
    def native_value(self) -> StateType:
        """Return the native value of the sensor."""
        return self.state

    @property
    def device_class(self) -> SensorDeviceClass | None:
        """Return the device class of the sensor."""
        # Determine device class based on query name or data
        query_name = self.query.get("name", "").lower()
        query_description = self.query.get("description", "").lower()
        
        # Check for specific financial indicators
        if any(term in query_name or term in query_description for term in ["balance", "amount", "total", "worth", "asset", "liability"]):
            return SensorDeviceClass.MONETARY
        elif any(term in query_name or term in query_description for term in ["percentage", "rate", "ratio"]):
            return SensorDeviceClass.PRESSURE  # Closest to percentage
        elif any(term in query_name or query_description for term in ["count", "number"]):
            return SensorDeviceClass.NONE  # No specific device class for counts
        
        # Default to monetary for financial queries
        return SensorDeviceClass.MONETARY

    @property
    def state_class(self) -> SensorStateClass | None:
        """Return the state class of the sensor."""
        # Determine state class based on query type and data
        query_name = self.query.get("name", "").lower()
        query_description = self.query.get("description", "").lower()
        
        # Check for specific indicators
        if any(term in query_name or term in query_description for term in ["balance", "amount", "total", "worth", "asset", "liability"]):
            return SensorStateClass.MEASUREMENT
        elif any(term in query_name or query_description for term in ["count", "number"]):
            return SensorStateClass.MEASUREMENT
        elif any(term in query_name or query_description for term in ["percentage", "rate", "ratio"]):
            return SensorStateClass.MEASUREMENT
        
        # Default to measurement for financial queries
        return SensorStateClass.MEASUREMENT

    @property
    def unit_of_measurement(self) -> str | None:
        """Return the unit of measurement of the sensor."""
        # Try to get unit from the sensor data first
        if (self.coordinator.data and "sensors" in self.coordinator.data and 
            str(self.query_id) in self.coordinator.data["sensors"]):
            sensor_data = self.coordinator.data["sensors"][str(self.query_id)]
            if isinstance(sensor_data, dict) and "unit" in sensor_data:
                return sensor_data["unit"]
        
        # Fallback to query configuration
        if self.query.get("ha_unit_of_measurement"):
            return self.query["ha_unit_of_measurement"]
        
        # Determine unit based on device class and query content
        device_class = self.device_class
        
        if device_class == SensorDeviceClass.MONETARY:
            return "USD"  # Default to USD for financial data
        elif device_class == SensorDeviceClass.PRESSURE:
            return "%"  # Percentage
        elif device_class == SensorDeviceClass.NONE:
            # Check if it's a count
            query_name = self.query.get("name", "").lower()
            if any(term in query_name for term in ["count", "number", "total"]):
                return None  # No unit for counts
        
        return "USD"  # Default to USD

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        if not self.coordinator.data or "sensors" not in self.coordinator.data:
            return {}
            
        sensor_data = self.coordinator.data["sensors"].get(str(self.query_id))
        
        attributes = {
            ATTR_QUERY_ID: self.query_id,
            ATTR_QUERY_NAME: self.query.get("name", ""),
            ATTR_QUERY_DESCRIPTION: self.query.get("description", ""),
            ATTR_QUERY_TYPE: self.query.get("query_type", ""),
            ATTR_LAST_UPDATED: self.coordinator.last_update_success,
            "data_source": "query",
        }
        
        # Add query-specific attributes
        if self.query.get("ha_entity_id"):
            attributes["entity_id"] = self.query["ha_entity_id"]
        if self.query.get("ha_unit_of_measurement"):
            attributes["custom_unit"] = self.query["ha_unit_of_measurement"]
        if self.query.get("ha_device_class"):
            attributes["custom_device_class"] = self.query["ha_device_class"]
        
        # Add data context if available
        if sensor_data:
            if isinstance(sensor_data, dict) and "data" in sensor_data:
                data = sensor_data["data"]
                if isinstance(data, list):
                    attributes["data_count"] = len(data)
                    # Add sample data (first few items)
                    if len(data) > 0:
                        attributes["sample_data"] = data[:3]
                elif isinstance(data, dict):
                    attributes["data_keys"] = list(data.keys())
                    attributes["sample_data"] = data
            elif isinstance(sensor_data, (int, float)):
                attributes["raw_value"] = sensor_data
            elif isinstance(sensor_data, str):
                attributes["raw_value"] = sensor_data
        
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