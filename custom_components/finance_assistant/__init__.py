"""The Finance Assistant integration."""
from __future__ import annotations

import logging
from typing import Any

__version__ = "1.0.24"

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_API_KEY, CONF_SSL, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
import homeassistant.helpers.config_validation as cv

from .const import (
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)
from .coordinator import FinanceAssistantDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# No CONFIG_SCHEMA needed - this integration only uses config entries

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.CALENDAR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Finance Assistant from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Create coordinator
    coordinator = FinanceAssistantDataUpdateCoordinator(hass, entry.data)
    await coordinator.async_config_entry_first_refresh()

    # Store coordinator
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate old entry."""
    _LOGGER.info("Migrating from version %s", config_entry.version)

    if config_entry.version == 1:
        # Add new fields with defaults
        new = {**config_entry.data}
        new[CONF_SCAN_INTERVAL] = DEFAULT_SCAN_INTERVAL
        
        config_entry.version = 2
        hass.config_entries.async_update_entry(config_entry, data=new)

    if config_entry.version == 2:
        # Migrate to version 3
        config_entry.version = 3
        hass.config_entries.async_update_entry(config_entry)

    if config_entry.version == 3:
        # Migrate to version 4
        config_entry.version = 4
        hass.config_entries.async_update_entry(config_entry)

    _LOGGER.info("Migration to version %s successful", config_entry.version)
    return True 