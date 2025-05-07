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
PLATFORMS: list[str] = ["sensor", "device_tracker"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Pi‑hole DHCP Presence from a UI config entry."""
    host = entry.data.get(CONF_HOST, DEFAULT_HOST)
    scan_interval = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    away_time = entry.data.get(CONF_AWAY_TIME, DEFAULT_AWAY_TIME)

    coordinator = PiholeUpdateCoordinator(hass, host, scan_interval)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "coordinator": coordinator,
        "away_time": away_time,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
