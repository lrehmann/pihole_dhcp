# custom_components/pihole_dhcp/__init__.py

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_SCAN_INTERVAL,
    CONF_AWAY_TIME,
    DEFAULT_HOST,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_AWAY_TIME,
)
from .coordinator import PiholeUpdateCoordinator

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["sensor", "binary_sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Pi‑hole DHCP Presence from a UI config entry."""
    # Read config data
    host = entry.data.get(CONF_HOST, DEFAULT_HOST)
    scan_interval = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    away_time = entry.data.get(CONF_AWAY_TIME, DEFAULT_AWAY_TIME)

    # Instantiate coordinator and fetch initial data
    coordinator = PiholeUpdateCoordinator(hass, host, scan_interval)
    await coordinator.async_config_entry_first_refresh()

    # Store coordinator and options for unload/setup
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "coordinator": coordinator,
        "away_time": away_time,
    }

    # Forward setup to each platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload an existing Pi‑hole DHCP Presence config entry."""
    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        # Remove stored data
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
