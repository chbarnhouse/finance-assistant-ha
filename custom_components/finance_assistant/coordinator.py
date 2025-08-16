"""Enhanced data coordinator for Finance Assistant integration."""
from __future__ import annotations
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.exceptions import ConfigEntryAuthFailed

from .api_client import FinanceAssistantAPIClient

_LOGGER = logging.getLogger(__name__)

class FinanceAssistantCoordinator(DataUpdateCoordinator):
    """Enhanced coordinator for Finance Assistant data."""
    
    def __init__(
        self,
        hass: HomeAssistant,
        api_client: FinanceAssistantAPIClient,
        update_interval: timedelta = timedelta(minutes=15),
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Finance Assistant",
            update_interval=update_interval,
        )
        self.api_client = api_client
    
    async def _async_update_data(self) -> Dict[str, Any]:
        """Update data from the Finance Assistant API."""
        try:
            _LOGGER.debug("Fetching enhanced financial data from Finance Assistant API")
            
            # Fetch all enhanced data in parallel
            data = {}
            
            # Basic financial data
            try:
                data["cash_flow_forecast"] = await self.api_client.get_cash_flow_forecast()
            except Exception as e:
                _LOGGER.warning("Failed to fetch cash flow forecast: %s", e)
                data["cash_flow_forecast"] = {}
            
            try:
                data["financial_summary"] = await self.api_client.get_financial_summary()
            except Exception as e:
                _LOGGER.warning("Failed to fetch financial summary: %s", e)
                data["financial_summary"] = {}
            
            try:
                data["critical_expenses"] = await self.api_client.get_critical_expenses()
            except Exception as e:
                _LOGGER.warning("Failed to fetch critical expenses: %s", e)
                data["critical_expenses"] = {}
            
            try:
                data["recurring_summary"] = await self.api_client.get_recurring_summary()
            except Exception as e:
                _LOGGER.warning("Failed to fetch recurring summary: %s", e)
                data["recurring_summary"] = {}
            
            try:
                data["account_summary"] = await self.api_client.get_account_summary()
            except Exception as e:
                _LOGGER.warning("Failed to fetch account summary: %s", e)
                data["account_summary"] = {}
            
            # Enhanced models data
            try:
                data["enhanced_categories"] = await self.api_client.get_enhanced_categories()
            except Exception as e:
                _LOGGER.warning("Failed to fetch enhanced categories: %s", e)
                data["enhanced_categories"] = []
            
            try:
                data["enhanced_payees"] = await self.api_client.get_enhanced_payees()
            except Exception as e:
                _LOGGER.warning("Failed to fetch enhanced payees: %s", e)
                data["enhanced_payees"] = []
            
            try:
                data["enhanced_accounts"] = await self.api_client.get_enhanced_accounts()
            except Exception as e:
                _LOGGER.warning("Failed to fetch enhanced accounts: %s", e)
                data["enhanced_accounts"] = []
            
            try:
                data["recurring_transactions"] = await self.api_client.get_recurring_transactions()
            except Exception as e:
                _LOGGER.warning("Failed to fetch recurring transactions: %s", e)
                data["recurring_transactions"] = []
            
            try:
                data["enhanced_transactions"] = await self.api_client.get_enhanced_transactions()
            except Exception as e:
                _LOGGER.warning("Failed to fetch enhanced transactions: %s", e)
                data["enhanced_transactions"] = []
            
            # Calculate derived financial health metrics
            data["financial_health"] = self._calculate_financial_health(data)
            
            # Calculate risk assessment
            data["risk_assessment"] = self._calculate_risk_assessment(data)
            
            # Add basic structure for backward compatibility
            try:
                # Add queries structure for old sensor/calendar compatibility
                data["queries"] = await self.api_client.get_queries()
            except Exception as e:
                _LOGGER.warning("Failed to fetch queries: %s", e)
                data["queries"] = []
            
            try:
                # Add dashboard structure for old sensor compatibility
                data["dashboard"] = await self.api_client.get_dashboard()
            except Exception as e:
                _LOGGER.warning("Failed to fetch dashboard: %s", e)
                data["dashboard"] = {}
            
            try:
                # Add calendars structure for old calendar compatibility
                data["calendars"] = await self.api_client.get_calendars()
            except Exception as e:
                _LOGGER.warning("Failed to fetch calendars: %s", e)
                data["calendars"] = {}
            
            # Add timestamp
            data["last_updated"] = datetime.now().isoformat()
            
            _LOGGER.debug("Successfully updated Finance Assistant data")
            return data
            
        except Exception as err:
            _LOGGER.error("Error updating Finance Assistant data: %s", err)
            raise UpdateFailed(f"Error updating Finance Assistant data: {err}") from err
    
    def _calculate_financial_health(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall financial health score and metrics."""
        try:
            # Extract key metrics
            cash_flow = data.get("cash_flow_forecast", {})
            financial_summary = data.get("financial_summary", {})
            recurring_summary = data.get("recurring_summary", {})
            account_summary = data.get("account_summary", {})
            
            # Calculate individual scores (0-100)
            balance_score = self._calculate_balance_score(account_summary)
            cash_flow_score = self._calculate_cash_flow_score(cash_flow)
            expense_score = self._calculate_expense_score(financial_summary)
            recurring_score = self._calculate_recurring_score(recurring_summary)
            
            # Calculate overall score (weighted average)
            overall_score = (
                balance_score * 0.25 +
                cash_flow_score * 0.30 +
                expense_score * 0.25 +
                recurring_score * 0.20
            )
            
            # Determine risk level
            risk_level = self._determine_risk_level(overall_score)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                balance_score, cash_flow_score, expense_score, recurring_score
            )
            
            # Generate alerts
            alerts = self._generate_alerts(data)
            
            # Calculate trends
            trends = self._calculate_trends(data)
            
            return {
                "overall_score": round(overall_score, 1),
                "balance_score": round(balance_score, 1),
                "cash_flow_score": round(cash_flow_score, 1),
                "expense_score": round(expense_score, 1),
                "recurring_score": round(recurring_score, 1),
                "risk_level": risk_level,
                "recommendations": recommendations,
                "alerts": alerts,
                "trends": trends,
                "generated_at": datetime.now().isoformat(),
            }
            
        except Exception as e:
            _LOGGER.error("Error calculating financial health: %s", e)
            return {
                "overall_score": 0,
                "balance_score": 0,
                "cash_flow_score": 0,
                "expense_score": 0,
                "recurring_score": 0,
                "risk_level": "unknown",
                "recommendations": ["Unable to calculate financial health"],
                "alerts": ["Financial health calculation failed"],
                "trends": {},
                "generated_at": datetime.now().isoformat(),
            }
    
    def _calculate_balance_score(self, account_summary: Dict[str, Any]) -> float:
        """Calculate balance health score."""
        try:
            total_balance = account_summary.get("total_balance", 0)
            
            if total_balance <= 0:
                return 0
            elif total_balance < 1000:
                return 25
            elif total_balance < 5000:
                return 50
            elif total_balance < 10000:
                return 75
            else:
                return 100
        except Exception:
            return 0
    
    def _calculate_cash_flow_score(self, cash_flow: Dict[str, Any]) -> float:
        """Calculate cash flow health score."""
        try:
            next_30_days = cash_flow.get("next_30_days", {})
            net_cash_flow = next_30_days.get("net", 0)
            
            if net_cash_flow >= 0:
                return 100
            elif net_cash_flow > -1000:
                return 75
            elif net_cash_flow > -2500:
                return 50
            elif net_cash_flow > -5000:
                return 25
            else:
                return 0
        except Exception:
            return 0
    
    def _calculate_expense_score(self, financial_summary: Dict[str, Any]) -> float:
        """Calculate expense management score."""
        try:
            current_month = financial_summary.get("current_month", {})
            savings_rate = current_month.get("savings_rate", 0)
            
            if savings_rate >= 20:
                return 100
            elif savings_rate >= 15:
                return 80
            elif savings_rate >= 10:
                return 60
            elif savings_rate >= 5:
                return 40
            elif savings_rate >= 0:
                return 20
            else:
                return 0
        except Exception:
            return 0
    
    def _calculate_recurring_score(self, recurring_summary: Dict[str, Any]) -> float:
        """Calculate recurring obligations score."""
        try:
            obligation_ratio = recurring_summary.get("obligation_ratio", 0)
            
            if obligation_ratio <= 30:
                return 100
            elif obligation_ratio <= 40:
                return 80
            elif obligation_ratio <= 50:
                return 60
            elif obligation_ratio <= 60:
                return 40
            elif obligation_ratio <= 70:
                return 20
            else:
                return 0
        except Exception:
            return 0
    
    def _determine_risk_level(self, score: float) -> str:
        """Determine risk level based on overall score."""
        if score >= 80:
            return "low"
        elif score >= 60:
            return "moderate"
        elif score >= 40:
            return "high"
        elif score >= 20:
            return "very_high"
        else:
            return "critical"
    
    def _generate_recommendations(
        self, balance_score: float, cash_flow_score: float, 
        expense_score: float, recurring_score: float
    ) -> list[str]:
        """Generate personalized financial recommendations."""
        recommendations = []
        
        if balance_score < 50:
            recommendations.append("Build emergency fund to cover 3-6 months of expenses")
        
        if cash_flow_score < 50:
            recommendations.append("Review upcoming expenses and adjust spending patterns")
        
        if expense_score < 50:
            recommendations.append("Focus on increasing savings rate through expense reduction")
        
        if recurring_score < 50:
            recommendations.append("Review recurring obligations and consider reducing non-essential expenses")
        
        if not recommendations:
            recommendations.append("Maintain current financial practices - you're doing great!")
        
        return recommendations
    
    def _generate_alerts(self, data: Dict[str, Any]) -> list[str]:
        """Generate financial alerts based on data."""
        alerts = []
        
        # Check for critical expenses
        critical_expenses = data.get("critical_expenses", {})
        if critical_expenses.get("total_critical_amount", 0) > 5000:
            alerts.append("High upcoming expenses detected - review budget")
        
        # Check for negative cash flow
        cash_flow = data.get("cash_flow_forecast", {})
        next_30_days = cash_flow.get("next_30_days", {})
        if next_30_days.get("net", 0) < -2000:
            alerts.append("Negative cash flow projected for next 30 days")
        
        # Check for low savings rate
        financial_summary = data.get("financial_summary", {})
        current_month = financial_summary.get("current_month", {})
        if current_month.get("savings_rate", 0) < 10:
            alerts.append("Low savings rate - consider increasing income or reducing expenses")
        
        return alerts
    
    def _calculate_trends(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate financial trends."""
        # This would typically compare current data with historical data
        # For now, return basic trend indicators
        return {
            "cash_flow_trend": "stable",
            "expense_trend": "stable",
            "savings_trend": "stable",
        }
    
    def _calculate_risk_assessment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive risk assessment."""
        try:
            # Extract risk factors
            cash_flow = data.get("cash_flow_forecast", {})
            financial_summary = data.get("financial_summary", {})
            recurring_summary = data.get("recurring_summary", {})
            critical_expenses = data.get("critical_expenses", {})
            
            risk_factors = []
            high_risk_items = []
            medium_risk_items = []
            
            # Assess cash flow risk
            next_30_days = cash_flow.get("next_30_days", {})
            if next_30_days.get("net", 0) < 0:
                risk_factors.append({
                    "category": "cash_flow",
                    "description": "Negative cash flow projected",
                    "severity": "high",
                    "impact": "Potential liquidity issues"
                })
                high_risk_items.append("Negative cash flow in next 30 days")
            
            # Assess expense risk
            current_month = financial_summary.get("current_month", {})
            if current_month.get("savings_rate", 0) < 10:
                risk_factors.append({
                    "category": "expenses",
                    "description": "Low savings rate",
                    "severity": "medium",
                    "impact": "Reduced financial resilience"
                })
                medium_risk_items.append("Savings rate below 10%")
            
            # Assess recurring obligations risk
            obligation_ratio = recurring_summary.get("obligation_ratio", 0)
            if obligation_ratio > 60:
                risk_factors.append({
                    "category": "recurring_obligations",
                    "description": "High recurring obligations",
                    "severity": "high",
                    "impact": "Limited financial flexibility"
                })
                high_risk_items.append("Recurring obligations exceed 60% of income")
            
            # Calculate overall risk score
            risk_score = min(100, len(high_risk_items) * 30 + len(medium_risk_items) * 15)
            
            # Generate mitigation strategies
            mitigation_strategies = []
            if high_risk_items:
                mitigation_strategies.append("Immediate action required - review budget and expenses")
            if medium_risk_items:
                mitigation_strategies.append("Monitor closely and implement improvement strategies")
            
            return {
                "overall_risk_score": risk_score,
                "risk_factors": risk_factors,
                "high_risk_items": high_risk_items,
                "medium_risk_items": medium_risk_items,
                "risk_trends": {"trend": "stable"},  # Would compare with historical data
                "mitigation_strategies": mitigation_strategies,
                "generated_at": datetime.now().isoformat(),
            }
            
        except Exception as e:
            _LOGGER.error("Error calculating risk assessment: %s", e)
            return {
                "overall_risk_score": 0,
                "risk_factors": [],
                "high_risk_items": [],
                "medium_risk_items": [],
                "risk_trends": {},
                "mitigation_strategies": ["Risk assessment calculation failed"],
                "generated_at": datetime.now().isoformat(),
            }
    
    # Remove custom data property - let DataUpdateCoordinator handle it
    # The base class provides a read-only data property 