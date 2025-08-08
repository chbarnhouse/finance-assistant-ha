"""Config flow for Finance Assistant integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_API_KEY, CONF_SSL
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import (
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_PORT,
    DOMAIN,
)
from .coordinator import FinanceAssistantDataUpdateCoordinator, CannotConnect, InvalidAuth

_LOGGER = logging.getLogger(__name__)


class FinanceAssistantConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Finance Assistant."""

    VERSION = 4

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle reconfiguration."""
        return await self.async_step_user(user_input)

    @staticmethod
    async def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        from .options import FinanceAssistantOptionsFlow
        return FinanceAssistantOptionsFlow(config_entry)



    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validate API key is provided
            if not user_input.get(CONF_API_KEY):
                errors[CONF_API_KEY] = "required"
            else:
                try:
                    # Test the connection
                    coordinator = FinanceAssistantDataUpdateCoordinator(
                        self.hass, user_input
                    )
                    await coordinator.async_validate_input()

                    return self.async_create_entry(
                        title=f"Finance Assistant ({user_input[CONF_HOST]}:{user_input[CONF_PORT]})",
                        data=user_input,
                    )
                except CannotConnect:
                    errors["base"] = "cannot_connect"
                except InvalidAuth:
                    errors["base"] = "invalid_auth"
                except Exception:  # pylint: disable=broad-except
                    _LOGGER.exception("Unexpected exception")
                    errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
                    vol.Required(CONF_API_KEY): str,
                    vol.Optional(CONF_SSL, default=False): bool,
                    vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): int,
                }
            ),
            errors=errors,
        )


 