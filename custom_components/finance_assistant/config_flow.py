"""Enhanced configuration flow for Finance Assistant integration."""
from __future__ import annotations
import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_NAME

from .api_client import FinanceAssistantAPIClient
from .const import (
    CONF_API_KEY,
    CONF_SSL,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_NAME,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

class FinanceAssistantConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Finance Assistant."""
    
    VERSION = 1
    
    def __init__(self) -> None:
        """Initialize the config flow."""
        pass
    
    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}
        
        if user_input is not None:
            try:
                # Validate the connection
                await self._validate_connection(user_input)
                
                # Create the config entry directly (simplified)
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data=user_input,
                )
                
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
        
        # Show the form
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
                    vol.Required(CONF_HOST): str,
                    vol.Required(CONF_PORT, default=8080): int,
                    vol.Required(CONF_API_KEY): str,
                    vol.Optional(CONF_SSL, default=False): bool,
                    vol.Optional(
                        CONF_SCAN_INTERVAL, 
                        default=DEFAULT_SCAN_INTERVAL
                    ): int,
                }
            ),
            errors=errors,
        )
    

    
    async def async_step_import(self, import_info: dict[str, Any]) -> FlowResult:
        """Handle import from configuration.yaml."""
        return await self.async_step_user(import_info)
    
    async def _validate_connection(self, config: dict[str, Any]) -> None:
        """Validate the connection to Finance Assistant."""
        try:
            # Create API client
            api_client = FinanceAssistantAPIClient(
                host=config[CONF_HOST],
                port=config[CONF_PORT],
                api_key=config[CONF_API_KEY],
                ssl=config.get(CONF_SSL, False),
                timeout=30,
            )
            
            # Test connection with health check
            is_healthy = await api_client.health_check()
            if not is_healthy:
                raise CannotConnect()
            
            # Test enhanced endpoints
            try:
                await api_client.get_enhanced_categories()
                _LOGGER.info("Enhanced categories endpoint accessible")
            except Exception as e:
                _LOGGER.warning("Enhanced categories endpoint not accessible: %s", e)
            
            try:
                await api_client.get_enhanced_transactions()
                _LOGGER.info("Enhanced transactions endpoint accessible")
            except Exception as e:
                _LOGGER.warning("Enhanced transactions endpoint not accessible: %s", e)
            
            try:
                await api_client.get_recurring_transactions()
                _LOGGER.info("Recurring transactions endpoint accessible")
            except Exception as e:
                _LOGGER.warning("Recurring transactions endpoint not accessible: %s", e)
            
            _LOGGER.info("Successfully validated connection to Finance Assistant")
            
        except Exception as e:
            _LOGGER.error("Failed to validate connection: %s", e)
            if "Invalid API key" in str(e):
                raise InvalidAuth()
            elif "Server error" in str(e) or "HTTP error" in str(e):
                raise CannotConnect()
            else:
                raise CannotConnect()


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""


 