"""API client for Finance Assistant enhanced endpoints."""
from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional
import aiohttp
from aiohttp import ClientTimeout

_LOGGER = logging.getLogger(__name__)

class FinanceAssistantAPIClient:
    """Client for communicating with Finance Assistant enhanced API."""
    
    def __init__(
        self,
        host: str,
        port: int,
        api_key: str,
        ssl: bool = False,
        timeout: int = 30,
    ) -> None:
        """Initialize the API client."""
        self.host = host
        self.port = port
        self.api_key = api_key
        self.ssl = ssl
        self.timeout = timeout
        
        # Build base URL
        protocol = "https" if self.ssl else "http"
        self.base_url = f"{protocol}://{self.host}:{self.port}"
        
        # Default headers
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
        }
        
        # Timeout configuration
        self.client_timeout = ClientTimeout(total=self.timeout)
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Make a request to the Finance Assistant API."""
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with aiohttp.ClientSession(timeout=self.client_timeout) as session:
                if method.upper() == "GET":
                    async with session.get(url, headers=self.headers, params=params) as response:
                        return await self._handle_response(response)
                elif method.upper() == "POST":
                    async with session.post(url, headers=self.headers, json=data) as response:
                        return await self._handle_response(response)
                elif method.upper() == "PUT":
                    async with session.put(url, headers=self.headers, json=data) as response:
                        return await self._handle_response(response)
                elif method.upper() == "DELETE":
                    async with session.delete(url, headers=self.headers) as response:
                        return await self._handle_response(response)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                    
        except aiohttp.ClientError as e:
            _LOGGER.error("Network error in API request to %s: %s", url, e)
            raise
        except Exception as e:
            _LOGGER.error("Unexpected error in API request to %s: %s", url, e)
            raise
    
    async def _handle_response(self, response: aiohttp.ClientResponse) -> Any:
        """Handle the API response."""
        if response.status == 200:
            try:
                return await response.json()
            except Exception as e:
                _LOGGER.error("Failed to parse JSON response: %s", e)
                return {}
        elif response.status == 401:
            _LOGGER.error("Authentication failed: Invalid API key")
            raise ValueError("Invalid API key")
        elif response.status == 403:
            _LOGGER.error("Access forbidden: Insufficient permissions")
            raise ValueError("Insufficient permissions")
        elif response.status == 404:
            _LOGGER.error("Endpoint not found: %s", response.url)
            raise ValueError("Endpoint not found")
        elif response.status >= 500:
            _LOGGER.error("Server error: %s", response.status)
            raise RuntimeError(f"Server error: {response.status}")
        else:
            _LOGGER.error("HTTP error: %s", response.status)
            raise RuntimeError(f"HTTP error: {response.status}")
    
    # Enhanced Financial Data Endpoints
    
    async def get_cash_flow_forecast(self) -> Dict[str, Any]:
        """Get cash flow forecast data."""
        return await self._make_request("GET", "/api/enhanced/transactions/cash_flow_forecast/")
    
    async def get_financial_summary(self) -> Dict[str, Any]:
        """Get comprehensive financial summary."""
        return await self._make_request("GET", "/api/enhanced/transactions/financial_summary/")
    
    async def get_critical_expenses(self) -> Dict[str, Any]:
        """Get critical upcoming expenses."""
        return await self._make_request("GET", "/api/enhanced/transactions/critical_expenses/")
    
    async def get_recurring_summary(self) -> Dict[str, Any]:
        """Get recurring transactions summary."""
        return await self._make_request("GET", "/api/recurring-transactions/summary/")
    
    async def get_account_summary(self) -> Dict[str, Any]:
        """Get account summary and balances."""
        return await self._make_request("GET", "/api/enhanced/accounts/summary/")
    
    # Enhanced Models Endpoints
    
    async def get_enhanced_categories(self) -> List[Dict[str, Any]]:
        """Get enhanced categories."""
        response = await self._make_request("GET", "/api/enhanced/categories/")
        return response.get("results", []) if isinstance(response, dict) else response
    
    async def get_enhanced_payees(self) -> List[Dict[str, Any]]:
        """Get enhanced payees."""
        response = await self._make_request("GET", "/api/enhanced/payees/")
        return response.get("results", []) if isinstance(response, dict) else response
    
    async def get_enhanced_accounts(self) -> List[Dict[str, Any]]:
        """Get enhanced accounts."""
        response = await self._make_request("GET", "/api/enhanced/accounts/")
        return response.get("results", []) if isinstance(response, dict) else response
    
    async def get_recurring_transactions(self) -> List[Dict[str, Any]]:
        """Get recurring transactions."""
        response = await self._make_request("GET", "/api/recurring-transactions/")
        return response.get("results", []) if isinstance(response, dict) else response
    
    async def get_enhanced_transactions(self) -> List[Dict[str, Any]]:
        """Get enhanced transactions."""
        response = await self._make_request("GET", "/api/enhanced/transactions/")
        return response.get("results", []) if isinstance(response, dict) else response
    
    # Individual Entity Operations
    
    async def get_enhanced_category(self, category_id: str) -> Dict[str, Any]:
        """Get a specific enhanced category."""
        return await self._make_request("GET", f"/api/enhanced/categories/{category_id}/")
    
    async def get_enhanced_payee(self, payee_id: str) -> Dict[str, Any]:
        """Get a specific enhanced payee."""
        return await self._make_request("GET", f"/api/enhanced/payees/{payee_id}/")
    
    async def get_enhanced_account(self, account_id: str) -> Dict[str, Any]:
        """Get a specific enhanced account."""
        return await self._make_request("GET", f"/api/enhanced/accounts/{account_id}/")
    
    async def get_recurring_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """Get a specific recurring transaction."""
        return await self._make_request("GET", f"/api/recurring-transactions/{transaction_id}/")
    
    async def get_enhanced_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """Get a specific enhanced transaction."""
        return await self._make_request("GET", f"/api/enhanced/transactions/{transaction_id}/")
    
    # Create Operations
    
    async def create_enhanced_category(self, category_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new enhanced category."""
        return await self._make_request("POST", "/api/enhanced/categories/", data=category_data)
    
    async def create_enhanced_payee(self, payee_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new enhanced payee."""
        return await self._make_request("POST", "/api/enhanced/payees/", data=payee_data)
    
    async def create_enhanced_account(self, account_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new enhanced account."""
        return await self._make_request("POST", "/api/enhanced/accounts/", data=account_data)
    
    async def create_recurring_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new recurring transaction."""
        return await self._make_request("POST", "/api/recurring-transactions/", data=transaction_data)
    
    async def create_enhanced_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new enhanced transaction."""
        return await self._make_request("POST", "/api/enhanced/transactions/", data=transaction_data)
    
    # Update Operations
    
    async def update_enhanced_category(self, category_id: str, category_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an enhanced category."""
        return await self._make_request("PUT", f"/api/enhanced/categories/{category_id}/", data=category_data)
    
    async def update_enhanced_payee(self, payee_id: str, payee_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an enhanced payee."""
        return await self._make_request("PUT", f"/api/enhanced/payees/{payee_id}/", data=payee_data)
    
    async def update_enhanced_account(self, account_id: str, account_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an enhanced account."""
        return await self._make_request("PUT", f"/api/enhanced/accounts/{account_id}/", data=account_data)
    
    async def update_recurring_transaction(self, transaction_id: str, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a recurring transaction."""
        return await self._make_request("PUT", f"/api/recurring-transactions/{transaction_id}/", data=transaction_data)
    
    async def update_enhanced_transaction(self, transaction_id: str, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an enhanced transaction."""
        return await self._make_request("PUT", f"/api/enhanced/transactions/{transaction_id}/", data=transaction_data)
    
    # Delete Operations
    
    async def delete_enhanced_category(self, category_id: str) -> bool:
        """Delete an enhanced category."""
        try:
            await self._make_request("DELETE", f"/api/enhanced/categories/{category_id}/")
            return True
        except Exception:
            return False
    
    async def delete_enhanced_payee(self, payee_id: str) -> bool:
        """Delete an enhanced payee."""
        try:
            await self._make_request("DELETE", f"/api/enhanced/payees/{payee_id}/")
            return True
        except Exception:
            return False
    
    async def delete_enhanced_account(self, account_id: str) -> bool:
        """Delete an enhanced account."""
        try:
            await self._make_request("DELETE", f"/api/enhanced/accounts/{account_id}/")
            return True
        except Exception:
            return False
    
    async def delete_recurring_transaction(self, transaction_id: str) -> bool:
        """Delete a recurring transaction."""
        try:
            await self._make_request("DELETE", f"/api/recurring-transactions/{transaction_id}/")
            return True
        except Exception:
            return False
    
    async def delete_enhanced_transaction(self, transaction_id: str) -> bool:
        """Delete an enhanced transaction."""
        try:
            await self._make_request("DELETE", f"/api/enhanced/transactions/{transaction_id}/")
            return True
        except Exception:
            return False
    
    # Filtered Queries
    
    async def get_enhanced_transactions_filtered(
        self,
        status: Optional[str] = None,
        source_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        category_id: Optional[str] = None,
        account_id: Optional[str] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """Get filtered enhanced transactions."""
        params = {}
        
        if status:
            params["status"] = status
        if source_type:
            params["source_type"] = source_type
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if category_id:
            params["category_id"] = category_id
        if account_id:
            params["account_id"] = account_id
        if min_amount is not None:
            params["min_amount"] = min_amount
        if max_amount is not None:
            params["max_amount"] = max_amount
        
        response = await self._make_request("GET", "/api/enhanced/transactions/", params=params)
        return response.get("results", []) if isinstance(response, dict) else response
    
    async def get_recurring_transactions_filtered(
        self,
        frequency: Optional[str] = None,
        is_active: Optional[bool] = None,
        category_id: Optional[str] = None,
        account_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get filtered recurring transactions."""
        params = {}
        
        if frequency:
            params["frequency"] = frequency
        if is_active is not None:
            params["is_active"] = is_active
        if category_id:
            params["category_id"] = category_id
        if account_id:
            params["account_id"] = account_id
        
        response = await self._make_request("GET", "/api/recurring-transactions/", params=params)
        return response.get("results", []) if isinstance(response, dict) else response
    
    # Health Check
    
    async def health_check(self) -> bool:
        """Check if the API is healthy."""
        try:
            await self._make_request("GET", "/api/health/")
            return True
        except Exception:
            return False
    
    # Backward Compatibility Methods
    
    async def get_queries(self) -> List[Dict[str, Any]]:
        """Get queries for backward compatibility."""
        try:
            response = await self._make_request("GET", "/api/ha/queries/")
            return response if isinstance(response, list) else []
        except Exception as e:
            _LOGGER.warning("Failed to fetch queries: %s", e)
            return []
    
    async def get_dashboard(self) -> Dict[str, Any]:
        """Get dashboard data for backward compatibility."""
        try:
            response = await self._make_request("GET", "/api/ha/dashboard/")
            return response if isinstance(response, dict) else {}
        except Exception as e:
            _LOGGER.warning("Failed to fetch dashboard: %s", e)
            return {}
    
    async def get_calendars(self) -> Dict[str, Any]:
        """Get calendar data for backward compatibility."""
        try:
            # For now, return empty calendars to prevent errors
            # This can be enhanced later with actual calendar data
            return {}
        except Exception as e:
            _LOGGER.warning("Failed to fetch calendars: %s", e)
            return {}
