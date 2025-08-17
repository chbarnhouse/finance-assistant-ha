"""Enhanced financial sensors for Home Assistant Finance Assistant integration."""
from __future__ import annotations
import logging
from datetime import datetime, timedelta
from typing import Any, Optional

import voluptuous as vol
from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
    SensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from ..coordinator import FinanceAssistantCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up enhanced financial sensors."""
    coordinator: FinanceAssistantCoordinator = hass.data["finance_assistant"][config_entry.entry_id]["coordinator"]
    
    # Create enhanced sensors
    sensors = [
        CashFlowForecastSensor(coordinator),
        FinancialHealthSensor(coordinator),
        UpcomingExpensesSensor(coordinator),
        RecurringObligationsSensor(coordinator),
        AccountBalanceSensor(coordinator),
        MonthlyBudgetSensor(coordinator),
        SavingsRateSensor(coordinator),
        RiskAssessmentSensor(coordinator),
        # Analytics Sensors
        TransactionStatusSensor(coordinator),
        SpendingTrendsSensor(coordinator),
        ObligationRatioSensor(coordinator),
        FinancialInsightsSensor(coordinator),
        CashFlowTrendSensor(coordinator),
        ExpenseTrendSensor(coordinator),
        SavingsTrendSensor(coordinator),
        HighRiskItemsSensor(coordinator),
        # Financial Summary Analytics
        OverallFinancialScoreSensor(coordinator),
        BalanceScoreSensor(coordinator),
        CashFlowScoreSensor(coordinator),
        ExpenseScoreSensor(coordinator),
        RecurringScoreSensor(coordinator),
        RiskLevelSensor(coordinator),
        # Recurring Transactions Analytics
        MonthlyObligationsSensor(coordinator),
        EssentialObligationsSensor(coordinator),
        DiscretionaryObligationsSensor(coordinator),
        ObligationRatioSensor(coordinator),
        # Account Analytics
        TotalAccountBalanceSensor(coordinator),
        ActiveAccountCountSensor(coordinator),
        AccountBalanceByTypeSensor(coordinator),
        # Cash Flow Analytics
        TotalIncomeSensor(coordinator),
        TotalExpensesSensor(coordinator),
        NetCashFlowSensor(coordinator),
    ]
    
    async_add_entities(sensors)


class CashFlowForecastSensor(CoordinatorEntity, SensorEntity):
    """Sensor for cash flow forecasting."""
    
    _attr_name = "Cash Flow Forecast"
    _attr_icon = "mdi:cash-multiple"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    
    def __init__(self, coordinator: FinanceAssistantCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_cash_flow_forecast"
    
    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data or "cash_flow_forecast" not in self.coordinator.data:
            return None
        
        forecast = self.coordinator.data["cash_flow_forecast"]
        return forecast.get("next_30_days", {}).get("net", 0)
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        if not self.coordinator.data or "cash_flow_forecast" not in self.coordinator.data:
            return {}
        
        forecast = self.coordinator.data["cash_flow_forecast"]
        return {
            "next_7_days": forecast.get("next_7_days", {}),
            "next_30_days": forecast.get("next_30_days", {}),
            "next_90_days": forecast.get("next_90_days", {}),
            "confidence_level": forecast.get("confidence_level", "unknown"),
            "assumptions": forecast.get("assumptions", []),
            "generated_at": forecast.get("generated_at"),
        }


class FinancialHealthSensor(CoordinatorEntity, SensorEntity):
    """Sensor for overall financial health score."""
    
    _attr_name = "Financial Health Score"
    _attr_icon = "mdi:heart-pulse"
    _attr_native_unit_of_measurement = "%"
    _attr_state_class = SensorStateClass.MEASUREMENT
    
    def __init__(self, coordinator: FinanceAssistantCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_financial_health"
    
    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data or "financial_health" not in self.coordinator.data:
            return None
        
        health = self.coordinator.data["financial_health"]
        return health.get("overall_score", 0)
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        if not self.coordinator.data or "financial_health" not in self.coordinator.data:
            return {}
        
        health = self.coordinator.data["financial_health"]
        return {
            "balance_score": health.get("balance_score", 0),
            "cash_flow_score": health.get("cash_flow_score", 0),
            "expense_score": health.get("expense_score", 0),
            "recurring_score": health.get("recurring_score", 0),
            "risk_level": health.get("risk_level", "unknown"),
            "recommendations": health.get("recommendations", []),
            "alerts": health.get("alerts", []),
            "trends": health.get("trends", {}),
            "generated_at": health.get("generated_at"),
        }


class UpcomingExpensesSensor(CoordinatorEntity, SensorEntity):
    """Sensor for upcoming critical expenses."""
    
    _attr_name = "Upcoming Critical Expenses"
    _attr_icon = "mdi:alert-circle"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    
    def __init__(self, coordinator: FinanceAssistantCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_upcoming_expenses"
    
    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data or "critical_expenses" not in self.coordinator.data:
            return None
        
        expenses = self.coordinator.data["critical_expenses"]
        return expenses.get("total_critical_amount", 0)
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        if not self.coordinator.data or "critical_expenses" not in self.coordinator.data:
            return {}
        
        expenses = self.coordinator.data["critical_expenses"]
        return {
            "count": expenses.get("count", 0),
            "expenses": expenses.get("critical_expenses", []),
            "next_due_date": self._get_next_due_date(expenses.get("critical_expenses", [])),
            "days_until_next": self._get_days_until_next(expenses.get("critical_expenses", [])),
        }
    
    def _get_next_due_date(self, expenses: list) -> Optional[str]:
        """Get the next due date from expenses."""
        if not expenses:
            return None
        
        # Sort by due date and return the earliest
        sorted_expenses = sorted(expenses, key=lambda x: x.get("due_date", ""))
        return sorted_expenses[0].get("due_date") if sorted_expenses else None
    
    def _get_days_until_next(self, expenses: list) -> Optional[int]:
        """Get days until next expense is due."""
        next_date = self._get_next_due_date(expenses)
        if not next_date:
            return None
        
        try:
            due_date = datetime.strptime(next_date, "%Y-%m-%d").date()
            today = datetime.now().date()
            return (due_date - today).days
        except (ValueError, TypeError):
            return None


class RecurringObligationsSensor(CoordinatorEntity, SensorEntity):
    """Sensor for recurring monthly obligations."""
    
    _attr_name = "Monthly Recurring Obligations"
    _attr_icon = "mdi:calendar-repeat"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    
    def __init__(self, coordinator: FinanceAssistantCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_recurring_obligations"
    
    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data or "recurring_summary" not in self.coordinator.data:
            return None
        
        summary = self.coordinator.data["recurring_summary"]
        return summary.get("total_monthly_obligations", 0)
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        if not self.coordinator.data or "recurring_summary" not in self.coordinator.data:
            return {}
        
        summary = self.coordinator.data["recurring_summary"]
        return {
            "essential_obligations": summary.get("essential_obligations", 0),
            "discretionary_obligations": summary.get("discretionary_obligations", 0),
            "obligation_ratio": summary.get("obligation_ratio", 0),
            "next_due_dates": summary.get("next_due_dates", []),
            "generated_at": summary.get("generated_at"),
        }


class AccountBalanceSensor(CoordinatorEntity, SensorEntity):
    """Sensor for total account balance."""
    
    _attr_name = "Total Account Balance"
    _attr_icon = "mdi:bank"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.TOTAL
    
    def __init__(self, coordinator: FinanceAssistantCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_total_balance"
    
    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data or "account_summary" not in self.coordinator.data:
            return None
        
        summary = self.coordinator.data["account_summary"]
        return summary.get("total_balance", 0)
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        if not self.coordinator.data or "account_summary" not in self.coordinator.data:
            return {}
        
        summary = self.coordinator.data["account_summary"]
        return {
            "account_count": summary.get("account_count", 0),
            "active_count": summary.get("active_count", 0),
            "balance_by_type": summary.get("balance_by_type", {}),
        }


class MonthlyBudgetSensor(CoordinatorEntity, SensorEntity):
    """Sensor for monthly budget status."""
    
    _attr_name = "Monthly Budget Status"
    _attr_icon = "mdi:chart-line"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    
    def __init__(self, coordinator: FinanceAssistantCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_monthly_budget"
    
    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data or "financial_summary" not in self.coordinator.data:
            return None
        
        summary = self.coordinator.data["financial_summary"]
        current_month = summary.get("current_month", {})
        return current_month.get("net", 0)
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        if not self.coordinator.data or "financial_summary" not in self.coordinator.data:
            return {}
        
        summary = self.coordinator.data["financial_summary"]
        current_month = summary.get("current_month", {})
        ytd = summary.get("year_to_date", {})
        
        return {
            "monthly_income": current_month.get("income", 0),
            "monthly_expenses": current_month.get("expenses", 0),
            "monthly_savings_rate": current_month.get("savings_rate", 0),
            "ytd_income": ytd.get("income", 0),
            "ytd_expenses": ytd.get("expenses", 0),
            "ytd_savings_rate": ytd.get("savings_rate", 0),
            "category_breakdown": summary.get("category_breakdown", []),
            "top_expenses": summary.get("top_expenses", []),
            "top_income": summary.get("top_income", []),
        }


class SavingsRateSensor(CoordinatorEntity, SensorEntity):
    """Sensor for savings rate percentage."""
    
    _attr_name = "Monthly Savings Rate"
    _attr_icon = "mdi:percent"
    _attr_native_unit_of_measurement = "%"
    _attr_state_class = SensorStateClass.MEASUREMENT
    
    def __init__(self, coordinator: FinanceAssistantCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_savings_rate"
    
    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data or "financial_summary" not in self.coordinator.data:
            return None
        
        summary = self.coordinator.data["financial_summary"]
        current_month = summary.get("current_month", {})
        return current_month.get("savings_rate", 0)
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        if not self.coordinator.data or "financial_summary" not in self.coordinator.data:
            return {}
        
        summary = self.coordinator.data["financial_summary"]
        current_month = summary.get("current_month", {})
        ytd = summary.get("year_to_date", {})
        
        return {
            "monthly_income": current_month.get("income", 0),
            "monthly_expenses": current_month.get("expenses", 0),
            "monthly_net": current_month.get("net", 0),
            "ytd_savings_rate": ytd.get("savings_rate", 0),
            "target_savings_rate": 20.0,  # Configurable target
            "savings_status": self._get_savings_status(current_month.get("savings_rate", 0)),
        }
    
    def _get_savings_status(self, rate: float) -> str:
        """Get human-readable savings status."""
        if rate >= 20:
            return "Excellent"
        elif rate >= 15:
            return "Good"
        elif rate >= 10:
            return "Fair"
        elif rate >= 5:
            return "Poor"
        else:
            return "Critical"


class RiskAssessmentSensor(CoordinatorEntity, SensorEntity):
    """Sensor for financial risk assessment."""
    
    _attr_name = "Financial Risk Assessment"
    _attr_icon = "mdi:shield-alert"
    _attr_native_unit_of_measurement = "%"
    _attr_state_class = SensorStateClass.MEASUREMENT
    
    def __init__(self, coordinator: FinanceAssistantCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_risk_assessment"
    
    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data or "risk_assessment" not in self.coordinator.data:
            return None
        
        assessment = self.coordinator.data["risk_assessment"]
        return assessment.get("overall_risk_score", 0)
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        if not self.coordinator.data or "risk_assessment" not in self.coordinator.data:
            return {}
        
        assessment = self.coordinator.data["risk_assessment"]
        return {
            "risk_factors": assessment.get("risk_factors", []),
            "high_risk_items": assessment.get("high_risk_items", []),
            "medium_risk_items": assessment.get("medium_risk_items", []),
            "risk_trends": assessment.get("risk_trends", {}),
            "mitigation_strategies": assessment.get("mitigation_strategies", []),
            "risk_level": self._get_risk_level(assessment.get("overall_risk_score", 0)),
            "generated_at": assessment.get("generated_at"),
        }
    
    def _get_risk_level(self, score: float) -> str:
        """Get human-readable risk level."""
        if score <= 20:
            return "Low"
        elif score <= 40:
            return "Moderate"
        elif score <= 60:
            return "High"
        elif score <= 80:
            return "Very High"
        else:
            return "Critical"


# New Analytics Sensors

class TransactionStatusSensor(CoordinatorEntity, SensorEntity):
    """Sensor for transaction status counts and analytics."""
    
    _attr_name = "Transaction Status Analytics"
    _attr_icon = "mdi:chart-line"
    _attr_state_class = SensorStateClass.MEASUREMENT
    
    def __init__(self, coordinator: FinanceAssistantCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_transaction_status"
    
    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data or "enhanced_transactions" not in self.coordinator.data:
            return None
        
        transactions = self.coordinator.data["enhanced_transactions"]
        if not transactions:
            return 0
        
        # Return total transaction count as main value
        return len(transactions)
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        if not self.coordinator.data or "enhanced_transactions" not in self.coordinator.data:
            return {}
        
        transactions = self.coordinator.data["enhanced_transactions"]
        if not transactions:
            return {}
        
        # Count transactions by status
        status_counts = {}
        for transaction in transactions:
            status = transaction.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "total_transactions": len(transactions),
            "real_transactions": status_counts.get("real", 0),
            "uncleared_transactions": status_counts.get("uncleared", 0),
            "unapproved_transactions": status_counts.get("unapproved", 0),
            "scheduled_transactions": status_counts.get("scheduled", 0),
            "cancelled_transactions": status_counts.get("cancelled", 0),
            "status_breakdown": status_counts,
            "last_updated": self.coordinator.data.get("last_updated"),
        }


class SpendingTrendsSensor(CoordinatorEntity, SensorEntity):
    """Sensor for spending trends and patterns."""
    
    _attr_name = "Spending Trends"
    _attr_icon = "mdi:trending-up"
    _attr_state_class = SensorStateClass.MEASUREMENT
    
    def __init__(self, coordinator: FinanceAssistantCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_spending_trends"
    
    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data or "financial_health" not in self.coordinator.data:
            return None
        
        health = self.coordinator.data["financial_health"]
        return health.get("overall_score", 0)
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        if not self.coordinator.data or "financial_health" not in self.coordinator.data:
            return {}
        
        health = self.coordinator.data["financial_health"]
        trends = health.get("trends", {})
        
        return {
            "cash_flow_trend": trends.get("cash_flow_trend", "Unknown"),
            "expense_trend": trends.get("expense_trend", "Unknown"),
            "savings_trend": trends.get("savings_trend", "Unknown"),
            "overall_score": health.get("overall_score", 0),
            "risk_level": health.get("risk_level", "Unknown"),
            "recommendations": health.get("recommendations", []),
            "alerts": health.get("alerts", []),
            "generated_at": health.get("generated_at"),
        }


class ObligationRatioSensor(CoordinatorEntity, SensorEntity):
    """Sensor for recurring obligations and ratio analysis."""
    
    _attr_name = "Obligation Ratio"
    _attr_icon = "mdi:percent"
    _attr_native_unit_of_measurement = "%"
    _attr_state_class = SensorStateClass.MEASUREMENT
    
    def __init__(self, coordinator: FinanceAssistantCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_obligation_ratio"
    
    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data or "recurring_summary" not in self.coordinator.data:
            return None
        
        summary = self.coordinator.data["recurring_summary"]
        return summary.get("obligation_ratio", 0)
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        if not self.coordinator.data or "recurring_summary" not in self.coordinator.data:
            return {}
        
        summary = self.coordinator.data["recurring_summary"]
        
        return {
            "total_monthly_obligations": summary.get("total_monthly_obligations", 0),
            "essential_obligations": summary.get("essential_obligations", 0),
            "discretionary_obligations": summary.get("discretionary_obligations", 0),
            "obligation_ratio": summary.get("obligation_ratio", 0),
            "next_due_dates": summary.get("next_due_dates", []),
            "obligation_status": self._get_obligation_status(summary.get("obligation_ratio", 0)),
            "generated_at": summary.get("generated_at"),
        }
    
    def _get_obligation_status(self, ratio: float) -> str:
        """Get human-readable obligation status."""
        if ratio <= 30:
            return "Excellent"
        elif ratio <= 50:
            return "Good"
        elif ratio <= 70:
            return "Fair"
        elif ratio <= 90:
            return "Poor"
        else:
            return "Critical"


class FinancialInsightsSensor(CoordinatorEntity, SensorEntity):
    """Sensor for financial insights and recommendations."""
    
    _attr_name = "Financial Insights"
    _attr_icon = "mdi:lightbulb-on"
    _attr_state_class = SensorStateClass.MEASUREMENT
    
    def __init__(self, coordinator: FinanceAssistantCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_financial_insights"
    
    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data or "financial_health" not in self.coordinator.data:
            return None
        
        health = self.coordinator.data["financial_health"]
        return len(health.get("recommendations", []))
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        if not self.coordinator.data or "financial_health" not in self.coordinator.data:
            return {}
        
        health = self.coordinator.data["financial_health"]
        
        return {
            "total_recommendations": len(health.get("recommendations", [])),
            "total_alerts": len(health.get("alerts", [])),
            "recommendations": health.get("recommendations", []),
            "alerts": health.get("alerts", []),
            "overall_score": health.get("overall_score", 0),
            "risk_level": health.get("risk_level", "Unknown"),
            "insight_status": self._get_insight_status(health.get("overall_score", 0)),
            "generated_at": health.get("generated_at"),
        }
    
    def _get_insight_status(self, score: float) -> str:
        """Get human-readable insight status."""
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Fair"
        elif score >= 20:
            return "Poor"
        else:
            return "Critical"


class CashFlowTrendSensor(CoordinatorEntity, SensorEntity):
    """Sensor for cash flow trend analysis."""
    
    _attr_name = "Cash Flow Trend"
    _attr_icon = "mdi:cash-flow"
    _attr_state_class = SensorStateClass.MEASUREMENT
    
    def __init__(self, coordinator: FinanceAssistantCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_cash_flow_trend"
    
    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data or "financial_health" not in self.coordinator.data:
            return None
        
        health = self.coordinator.data["financial_health"]
        trends = health.get("trends", {})
        trend = trends.get("cash_flow_trend", "Unknown")
        
        # Convert trend to numeric value for automation
        if trend == "Improving":
            return 1
        elif trend == "Stable":
            return 0
        elif trend == "Declining":
            return -1
        else:
            return 0
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        if not self.coordinator.data or "financial_health" not in self.coordinator.data:
            return {}
        
        health = self.coordinator.data["financial_health"]
        trends = health.get("trends", {})
        
        return {
            "cash_flow_trend": trends.get("cash_flow_trend", "Unknown"),
            "trend_numeric": self.native_value,
            "cash_flow_score": health.get("cash_flow_score", 0),
            "overall_score": health.get("overall_score", 0),
            "trend_description": self._get_trend_description(trends.get("cash_flow_trend", "Unknown")),
            "generated_at": health.get("generated_at"),
        }
    
    def _get_trend_description(self, trend: str) -> str:
        """Get human-readable trend description."""
        if trend == "Improving":
            return "Cash flow is improving month over month"
        elif trend == "Stable":
            return "Cash flow is stable and consistent"
        elif trend == "Declining":
            return "Cash flow is declining and needs attention"
        else:
            return "Cash flow trend is unknown"


class ExpenseTrendSensor(CoordinatorEntity, SensorEntity):
    """Sensor for expense trend analysis."""
    
    _attr_name = "Expense Trend"
    _attr_icon = "mdi:chart-line-variant"
    _attr_state_class = SensorStateClass.MEASUREMENT
    
    def __init__(self, coordinator: FinanceAssistantCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_expense_trend"
    
    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data or "financial_health" not in self.coordinator.data:
            return None
        
        health = self.coordinator.data["financial_health"]
        trends = health.get("trends", {})
        trend = trends.get("expense_trend", "Unknown")
        
        # Convert trend to numeric value for automation
        if trend == "Decreasing":
            return 1
        elif trend == "Stable":
            return 0
        elif trend == "Increasing":
            return -1
        else:
            return 0
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        if not self.coordinator.data or "financial_health" not in self.coordinator.data:
            return {}
        
        health = self.coordinator.data["financial_health"]
        trends = health.get("trends", {})
        
        return {
            "expense_trend": trends.get("expense_trend", "Unknown"),
            "trend_numeric": self.native_value,
            "expense_score": health.get("expense_score", 0),
            "overall_score": health.get("overall_score", 0),
            "trend_description": self._get_trend_description(trends.get("expense_trend", "Unknown")),
            "generated_at": health.get("generated_at"),
        }
    
    def _get_trend_description(self, trend: str) -> str:
        """Get human-readable trend description."""
        if trend == "Decreasing":
            return "Expenses are decreasing month over month"
        elif trend == "Stable":
            return "Expenses are stable and under control"
        elif trend == "Increasing":
            return "Expenses are increasing and need attention"
        else:
            return "Expense trend is unknown"


class SavingsTrendSensor(CoordinatorEntity, SensorEntity):
    """Sensor for savings trend analysis."""
    
    _attr_name = "Savings Trend"
    _attr_icon = "mdi:piggy-bank"
    _attr_state_class = SensorStateClass.MEASUREMENT
    
    def __init__(self, coordinator: FinanceAssistantCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_savings_trend"
    
    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data or "financial_health" not in self.coordinator.data:
            return None
        
        health = self.coordinator.data["financial_health"]
        trends = health.get("trends", {})
        trend = trends.get("savings_trend", "Unknown")
        
        # Convert trend to numeric value for automation
        if trend == "Improving":
            return 1
        elif trend == "Stable":
            return 0
        elif trend == "Declining":
            return -1
        else:
            return 0
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        if not self.coordinator.data or "financial_health" not in self.coordinator.data:
            return {}
        
        health = self.coordinator.data["financial_health"]
        trends = health.get("trends", {})
        
        return {
            "savings_trend": trends.get("savings_trend", "Unknown"),
            "trend_numeric": self.native_value,
            "overall_score": health.get("overall_score", 0),
            "trend_description": self._get_trend_description(trends.get("savings_trend", "Unknown")),
            "generated_at": health.get("generated_at"),
        }
    
    def _get_trend_description(self, trend: str) -> str:
        """Get human-readable trend description."""
        if trend == "Improving":
            return "Savings are improving month over month"
        elif trend == "Stable":
            return "Savings are stable and consistent"
        elif trend == "Declining":
            return "Savings are declining and need attention"
        else:
            return "Savings trend is unknown"


class HighRiskItemsSensor(CoordinatorEntity, SensorEntity):
    """Sensor for high-risk financial items."""
    
    _attr_name = "High Risk Items"
    _attr_icon = "mdi:alert-circle"
    _attr_state_class = SensorStateClass.MEASUREMENT
    
    def __init__(self, coordinator: FinanceAssistantCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_high_risk_items"
    
    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data or "risk_assessment" not in self.coordinator.data:
            return None
        
        assessment = self.coordinator.data["risk_assessment"]
        return len(assessment.get("high_risk_items", []))
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        if not self.coordinator.data or "risk_assessment" not in self.coordinator.data:
            return {}
        
        assessment = self.coordinator.data["risk_assessment"]
        
        return {
            "high_risk_count": len(assessment.get("high_risk_items", [])),
            "medium_risk_count": len(assessment.get("medium_risk_items", [])),
            "low_risk_count": len(assessment.get("low_risk_items", [])),
            "high_risk_items": assessment.get("high_risk_items", []),
            "medium_risk_items": assessment.get("medium_risk_items", []),
            "low_risk_items": assessment.get("low_risk_items", []),
            "overall_risk_score": assessment.get("overall_risk_score", 0),
            "risk_level": self._get_risk_level(assessment.get("overall_risk_score", 0)),
            "generated_at": assessment.get("generated_at"),
        }
    
    def _get_risk_level(self, score: float) -> str:
        """Get human-readable risk level."""
        if score <= 20:
            return "Low"
        elif score <= 40:
            return "Moderate"
        elif score <= 60:
            return "High"
        elif score <= 80:
            return "Very High"
        else:
            return "Critical"


# ============================================================================
# FINANCIAL SUMMARY ANALYTICS SENSORS
# ============================================================================

class OverallFinancialScoreSensor(CoordinatorEntity, SensorEntity):
    """Sensor for overall financial health score."""
    
    _attr_name = "Overall Financial Score"
    _attr_icon = "mdi:chart-line"
    _attr_native_unit_of_measurement = "%"
    _attr_state_class = SensorStateClass.MEASUREMENT
    
    def __init__(self, coordinator: FinanceAssistantCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_overall_financial_score"
    
    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data or "financial_summary" not in self.coordinator.data:
            return None
        
        summary = self.coordinator.data["financial_summary"]
        return summary.get("overall_score", 0)
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        if not self.coordinator.data or "financial_summary" not in self.coordinator.data:
            return {}
        
        summary = self.coordinator.data["financial_summary"]
        return {
            "balance_score": summary.get("balance_score", 0),
            "cash_flow_score": summary.get("cash_flow_score", 0),
            "expense_score": summary.get("expense_score", 0),
            "recurring_score": summary.get("recurring_score", 0),
            "risk_level": summary.get("risk_level", "unknown"),
            "recommendations": summary.get("recommendations", []),
            "alerts": summary.get("alerts", []),
            "trends": summary.get("trends", {}),
            "generated_at": summary.get("generated_at"),
        }


class BalanceScoreSensor(CoordinatorEntity, SensorEntity):
    """Sensor for balance health score."""
    
    _attr_name = "Balance Score"
    _attr_icon = "mdi:scale-balance"
    _attr_native_unit_of_measurement = "%"
    _attr_state_class = SensorStateClass.MEASUREMENT
    
    def __init__(self, coordinator: FinanceAssistantCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_balance_score"
    
    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data or "financial_summary" not in self.coordinator.data:
            return None
        
        summary = self.coordinator.data["financial_summary"]
        return summary.get("balance_score", 0)
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        if not self.coordinator.data or "financial_summary" not in self.coordinator.data:
            return {}
        
        summary = self.coordinator.data["financial_summary"]
        return {
            "overall_score": summary.get("overall_score", 0),
            "risk_level": summary.get("risk_level", "unknown"),
            "generated_at": summary.get("generated_at"),
        }


class CashFlowScoreSensor(CoordinatorEntity, SensorEntity):
    """Sensor for cash flow health score."""
    
    _attr_name = "Cash Flow Score"
    _attr_icon = "mdi:cash-flow"
    _attr_native_unit_of_measurement = "%"
    _attr_state_class = SensorStateClass.MEASUREMENT
    
    def __init__(self, coordinator: FinanceAssistantCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_cash_flow_score"
    
    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data or "financial_summary" not in self.coordinator.data:
            return None
        
        summary = self.coordinator.data["financial_summary"]
        return summary.get("cash_flow_score", 0)
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        if not self.coordinator.data or "financial_summary" not in self.coordinator.data:
            return {}
        
        summary = self.coordinator.data["financial_summary"]
        return {
            "overall_score": summary.get("overall_score", 0),
            "risk_level": summary.get("risk_level", "unknown"),
            "generated_at": summary.get("generated_at"),
        }


class ExpenseScoreSensor(CoordinatorEntity, SensorEntity):
    """Sensor for expense management score."""
    
    _attr_name = "Expense Score"
    _attr_icon = "mdi:credit-card-outline"
    _attr_native_unit_of_measurement = "%"
    _attr_state_class = SensorStateClass.MEASUREMENT
    
    def __init__(self, coordinator: FinanceAssistantCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_expense_score"
    
    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data or "financial_summary" not in self.coordinator.data:
            return None
        
        summary = self.coordinator.data["financial_summary"]
        return summary.get("expense_score", 0)
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        if not self.coordinator.data or "financial_summary" not in self.coordinator.data:
            return {}
        
        summary = self.coordinator.data["financial_summary"]
        return {
            "overall_score": summary.get("overall_score", 0),
            "risk_level": summary.get("risk_level", "unknown"),
            "generated_at": summary.get("generated_at"),
        }


class RecurringScoreSensor(CoordinatorEntity, SensorEntity):
    """Sensor for recurring expenses score."""
    
    _attr_name = "Recurring Score"
    _attr_icon = "mdi:repeat"
    _attr_native_unit_of_measurement = "%"
    _attr_state_class = SensorStateClass.MEASUREMENT
    
    def __init__(self, coordinator: FinanceAssistantCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_recurring_score"
    
    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data or "financial_summary" not in self.coordinator.data:
            return None
        
        summary = self.coordinator.data["financial_summary"]
        return summary.get("recurring_score", 0)
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        if not self.coordinator.data or "financial_summary" not in self.coordinator.data:
            return {}
        
        summary = self.coordinator.data["financial_summary"]
        return {
            "overall_score": summary.get("overall_score", 0),
            "risk_level": summary.get("risk_level", "unknown"),
            "generated_at": summary.get("generated_at"),
        }


class RiskLevelSensor(CoordinatorEntity, SensorEntity):
    """Sensor for financial risk level."""
    
    _attr_name = "Financial Risk Level"
    _attr_icon = "mdi:alert-triangle"
    _attr_state_class = SensorStateClass.MEASUREMENT
    
    def __init__(self, coordinator: FinanceAssistantCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_risk_level"
    
    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data or "financial_summary" not in self.coordinator.data:
            return None
        
        summary = self.coordinator.data["financial_summary"]
        risk_level = summary.get("risk_level", "unknown")
        
        # Convert risk level to numeric for automation
        risk_map = {"low": 1, "moderate": 2, "high": 3, "very_high": 4}
        return risk_map.get(risk_level, 0)
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        if not self.coordinator.data or "financial_summary" not in self.coordinator.data:
            return {}
        
        summary = self.coordinator.data["financial_summary"]
        risk_level = summary.get("risk_level", "unknown")
        
        return {
            "risk_level_text": risk_level,
            "risk_level_numeric": self.native_value,
            "overall_score": summary.get("overall_score", 0),
            "recommendations": summary.get("recommendations", []),
            "alerts": summary.get("alerts", []),
            "generated_at": summary.get("generated_at"),
        }


# ============================================================================
# RECURRING TRANSACTIONS ANALYTICS SENSORS
# ============================================================================

class MonthlyObligationsSensor(CoordinatorEntity, SensorEntity):
    """Sensor for total monthly obligations."""
    
    _attr_name = "Monthly Obligations"
    _attr_icon = "mdi:calendar-month"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    
    def __init__(self, coordinator: FinanceAssistantCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_monthly_obligations"
    
    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data or "recurring_summary" not in self.coordinator.data:
            return None
        
        summary = self.coordinator.data["recurring_summary"]
        return summary.get("total_monthly_obligations", 0)
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        if not self.coordinator.data or "recurring_summary" not in self.coordinator.data:
            return {}
        
        summary = self.coordinator.data["recurring_summary"]
        return {
            "essential_obligations": summary.get("essential_obligations", 0),
            "discretionary_obligations": summary.get("discretionary_obligations", 0),
            "obligation_ratio": summary.get("obligation_ratio", 0),
            "next_due_dates": summary.get("next_due_dates", []),
            "generated_at": summary.get("generated_at"),
        }


class EssentialObligationsSensor(CoordinatorEntity, SensorEntity):
    """Sensor for essential monthly obligations."""
    
    _attr_name = "Essential Obligations"
    _attr_icon = "mdi:home"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    
    def __init__(self, coordinator: FinanceAssistantCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_essential_obligations"
    
    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data or "recurring_summary" not in self.coordinator.data:
            return None
        
        summary = self.coordinator.data["recurring_summary"]
        return summary.get("essential_obligations", 0)
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        if not self.coordinator.data or "recurring_summary" not in self.coordinator.data:
            return {}
        
        summary = self.coordinator.data["recurring_summary"]
        return {
            "total_monthly_obligations": summary.get("total_monthly_obligations", 0),
            "discretionary_obligations": summary.get("discretionary_obligations", 0),
            "obligation_ratio": summary.get("obligation_ratio", 0),
            "generated_at": summary.get("generated_at"),
        }


class DiscretionaryObligationsSensor(CoordinatorEntity, SensorEntity):
    """Sensor for discretionary monthly obligations."""
    
    _attr_name = "Discretionary Obligations"
    _attr_icon = "mdi:shopping"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    
    def __init__(self, coordinator: FinanceAssistantCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_discretionary_obligations"
    
    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data or "recurring_summary" not in self.coordinator.data:
            return None
        
        summary = self.coordinator.data["recurring_summary"]
        return summary.get("discretionary_obligations", 0)
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        if not self.coordinator.data or "recurring_summary" not in self.coordinator.data:
            return {}
        
        summary = self.coordinator.data["recurring_summary"]
        return {
            "total_monthly_obligations": summary.get("total_monthly_obligations", 0),
            "essential_obligations": summary.get("essential_obligations", 0),
            "obligation_ratio": summary.get("obligation_ratio", 0),
                    "generated_at": summary.get("generated_at"),
    }


class ObligationRatioSensor(CoordinatorEntity, SensorEntity):
    """Sensor for obligation ratio (monthly obligations vs income)."""
    
    _attr_name = "Obligation Ratio"
    _attr_icon = "mdi:percent"
    _attr_native_unit_of_measurement = "%"
    _attr_state_class = SensorStateClass.MEASUREMENT
    
    def __init__(self, coordinator: FinanceAssistantCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_obligation_ratio"
    
    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data or "recurring_summary" not in self.coordinator.data:
            return None
        
        summary = self.coordinator.data["recurring_summary"]
        return summary.get("obligation_ratio", 0)
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        if not self.coordinator.data or "recurring_summary" not in self.coordinator.data:
            return {}
        
        summary = self.coordinator.data["recurring_summary"]
        return {
            "total_monthly_obligations": summary.get("total_monthly_obligations", 0),
            "essential_obligations": summary.get("essential_obligations", 0),
            "discretionary_obligations": summary.get("discretionary_obligations", 0),
            "generated_at": summary.get("generated_at"),
        }


# ============================================================================
# ACCOUNT ANALYTICS SENSORS
# ============================================================================

class TotalAccountBalanceSensor(CoordinatorEntity, SensorEntity):
    """Sensor for total account balance."""
    
    _attr_name = "Total Account Balance"
    _attr_icon = "mdi:bank"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    
    def __init__(self, coordinator: FinanceAssistantCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_total_account_balance"
    
    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data or "account_summary" not in self.coordinator.data:
            return None
        
        summary = self.coordinator.data["account_summary"]
        return summary.get("total_balance", 0)
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        if not self.coordinator.data or "account_summary" not in self.coordinator.data:
            return {}
        
        summary = self.coordinator.data["account_summary"]
        return {
            "account_count": summary.get("account_count", 0),
            "active_count": summary.get("active_count", 0),
            "balance_by_type": summary.get("balance_by_type", {}),
            "generated_at": summary.get("generated_at"),
        }


class ActiveAccountCountSensor(CoordinatorEntity, SensorEntity):
    """Sensor for active account count."""
    
    _attr_name = "Active Account Count"
    _attr_icon = "mdi:account-multiple"
    _attr_state_class = SensorStateClass.MEASUREMENT
    
    def __init__(self, coordinator: FinanceAssistantCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_active_account_count"
    
    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data or "account_summary" not in self.coordinator.data:
            return None
        
        summary = self.coordinator.data["account_summary"]
        return summary.get("active_count", 0)
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        if not self.coordinator.data or "account_summary" not in self.coordinator.data:
            return {}
        
        summary = self.coordinator.data["account_summary"]
        return {
            "total_account_count": summary.get("account_count", 0),
            "total_balance": summary.get("total_balance", 0),
            "balance_by_type": summary.get("balance_by_type", {}),
            "generated_at": summary.get("generated_at"),
        }


class AccountBalanceByTypeSensor(CoordinatorEntity, SensorEntity):
    """Sensor for account balance by type."""
    
    _attr_name = "Account Balance by Type"
    _attr_icon = "mdi:chart-pie"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    
    def __init__(self, coordinator: FinanceAssistantCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_account_balance_by_type"
    
    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data or "account_summary" not in self.coordinator.data:
            return None
        
        summary = self.coordinator.data["account_summary"]
        balance_by_type = summary.get("balance_by_type", {})
        
        # Return the highest balance type
        if balance_by_type:
            return max(balance_by_type.values())
        return 0
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        if not self.coordinator.data or "account_summary" not in self.coordinator.data:
            return {}
        
        summary = self.coordinator.data["account_summary"]
        balance_by_type = summary.get("balance_by_type", {})
        
        return {
            "total_balance": summary.get("total_balance", 0),
            "account_count": summary.get("account_count", 0),
            "active_count": summary.get("active_count", 0),
            "balance_by_type": balance_by_type,
            "generated_at": summary.get("generated_at"),
        }


# ============================================================================
# CASH FLOW ANALYTICS SENSORS
# ============================================================================

class TotalIncomeSensor(CoordinatorEntity, SensorEntity):
    """Sensor for total income."""
    
    _attr_name = "Total Income"
    _attr_icon = "mdi:cash-plus"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    
    def __init__(self, coordinator: FinanceAssistantCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_total_income"
    
    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data or "financial_summary" not in self.coordinator.data:
            return None
        
        # This would need to be calculated from transactions
        # For now, return a placeholder
        return 0
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        if not self.coordinator.data or "financial_summary" not in self.coordinator.data:
            return {}
        
        summary = self.coordinator.data["financial_summary"]
        return {
            "overall_score": summary.get("overall_score", 0),
            "cash_flow_score": summary.get("cash_flow_score", 0),
            "risk_level": summary.get("risk_level", "unknown"),
            "generated_at": summary.get("generated_at"),
        }


class TotalExpensesSensor(CoordinatorEntity, SensorEntity):
    """Sensor for total expenses."""
    
    _attr_name = "Total Expenses"
    _attr_icon = "mdi:cash-minus"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    
    def __init__(self, coordinator: FinanceAssistantCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_total_expenses"
    
    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data or "financial_summary" not in self.coordinator.data:
            return None
        
        summary = self.coordinator.data["financial_summary"]
        return summary.get("expense_score", 0)
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        if not self.coordinator.data or "financial_summary" not in self.coordinator.data:
            return {}
        
        summary = self.coordinator.data["financial_summary"]
        return {
            "overall_score": summary.get("overall_score", 0),
            "expense_score": summary.get("expense_score", 0),
            "risk_level": summary.get("risk_level", "unknown"),
            "generated_at": summary.get("generated_at"),
        }


class NetCashFlowSensor(CoordinatorEntity, SensorEntity):
    """Sensor for net cash flow."""
    
    _attr_name = "Net Cash Flow"
    _attr_icon = "mdi:cash-multiple"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    
    def __init__(self, coordinator: FinanceAssistantCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_net_cash_flow"
    
    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data or "financial_summary" not in self.coordinator.data:
            return None
        
        summary = self.coordinator.data["financial_summary"]
        # Calculate net cash flow from income and expenses
        # This would need to be implemented in the backend
        return 0
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        if not self.coordinator.data or "financial_summary" not in self.coordinator.data:
            return {}
        
        summary = self.coordinator.data["financial_summary"]
        return {
            "overall_score": summary.get("overall_score", 0),
            "cash_flow_score": summary.get("cash_flow_score", 0),
            "risk_level": summary.get("risk_level", "unknown"),
            "generated_at": summary.get("generated_at"),
        }
