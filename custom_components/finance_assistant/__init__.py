"""Enhanced Finance Assistant integration for Home Assistant."""
from __future__ import annotations
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_API_KEY, CONF_SSL, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .api_client import FinanceAssistantAPIClient
from .coordinator import FinanceAssistantCoordinator
from .const import (
    DOMAIN,
    DEFAULT_SCAN_INTERVAL,
    PLATFORMS,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Finance Assistant from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    # Get configuration
    config = entry.data
    host = config[CONF_HOST]
    port = config[CONF_PORT]
    api_key = config[CONF_API_KEY]
    ssl = config.get(CONF_SSL, False)
    scan_interval = config.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    
    # Get enhanced options
    options = entry.options
    enable_enhanced_sensors = options.get("enable_enhanced_sensors", True)
    enable_enhanced_calendars = options.get("enable_enhanced_calendars", True)
    update_interval_financial = options.get("update_interval_financial", 15)
    update_interval_calendar = options.get("update_interval_calendar", 30)
    
    _LOGGER.info("Setting up Finance Assistant integration for %s:%s", host, port)
    
    try:
        # Create API client
        api_client = FinanceAssistantAPIClient(
            host=host,
            port=port,
            api_key=api_key,
            ssl=ssl,
            timeout=30,
        )
        
        # Test connection
        is_healthy = await api_client.health_check()
        if not is_healthy:
            raise ConfigEntryNotReady("Finance Assistant API is not healthy")
        
        # Create coordinator with enhanced update intervals
        coordinator = FinanceAssistantCoordinator(
            hass=hass,
            api_client=api_client,
            update_interval=timedelta(minutes=update_interval_financial),
        )
        
        # Store coordinator in hass data
        hass.data[DOMAIN][entry.entry_id] = {
            "coordinator": coordinator,
            "api_client": api_client,
            "config": config,
            "options": options,
        }
        
        # Start coordinator
        await coordinator.async_config_entry_first_refresh()
        
        # Set up platforms based on configuration
        platforms_to_setup = []
        
        if enable_enhanced_sensors:
            platforms_to_setup.append("sensor")
        
        if enable_enhanced_calendars:
            platforms_to_setup.append("calendar")
        
        # Always set up the main integration
        platforms_to_setup.append("calendar")  # Keep original calendar for backward compatibility
        
        # Set up platforms
        for platform in platforms_to_setup:
            hass.async_create_task(
                hass.config_entries.async_forward_entry_setup(entry, platform)
            )
        
        _LOGGER.info("Finance Assistant integration setup completed successfully")
        return True
        
    except Exception as e:
        _LOGGER.error("Failed to set up Finance Assistant integration: %s", e)
        raise ConfigEntryNotReady(f"Failed to set up Finance Assistant: {e}") from e


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        # Clean up coordinator and API client
        if entry.entry_id in hass.data[DOMAIN]:
            coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
            await coordinator.async_shutdown()
            del hass.data[DOMAIN][entry.entry_id]
        
        # Remove domain if no more entries
        if not hass.data[DOMAIN]:
            del hass.data[DOMAIN]
    
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry) 