"""Options flow for Finance Assistant integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, OptionsFlow
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


class FinanceAssistantOptionsFlow(OptionsFlow):
    """Handle options flow for Finance Assistant."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
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

                    # Update the config entry
                    self.hass.config_entries.async_update_entry(
                        self.config_entry, data=user_input
                    )

                    return self.async_create_entry(title="", data=user_input)
                except CannotConnect:
                    errors["base"] = "cannot_connect"
                except InvalidAuth:
                    errors["base"] = "invalid_auth"
                except Exception:  # pylint: disable=broad-except
                    _LOGGER.exception("Unexpected exception")
                    errors["base"] = "unknown"

        # Get current values
        current_data = self.config_entry.data

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST, default=current_data.get(CONF_HOST, "")): str,
                    vol.Optional(CONF_PORT, default=current_data.get(CONF_PORT, DEFAULT_PORT)): int,
                    vol.Required(CONF_API_KEY, default=current_data.get(CONF_API_KEY, "")): str,
                    vol.Optional(CONF_SSL, default=current_data.get(CONF_SSL, False)): bool,
                    vol.Optional(CONF_SCAN_INTERVAL, default=current_data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)): int,
                }
            ),
            errors=errors,
        )


 