from __future__ import annotations
from datetime import datetime, timezone
from typing import Any

from homeassistant.components.device_tracker import TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC

from .const import DOMAIN, ATTR_LAST_QUERY, ATTR_NAME, ATTR_MAC_VENDOR, CONF_AWAY_TIME

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    away_time = data["away_time"]

    async_add_entities(
        PiholeTracker(coordinator, mac, away_time)
        for mac in coordinator.data
    )

class PiholeTracker(CoordinatorEntity, TrackerEntity):
    """Device tracker using Pi‑hole presence."""

    def __init__(self, coordinator, mac: str, away_time: int) -> None:
        super().__init__(coordinator)
        self._mac = mac
        self._away = away_time
        self._attr_unique_id = f"{DOMAIN}_{mac.replace(':','')}_pihole"
        self._attr_name = "Presence via Pi‑hole"

    @property
    def is_connected(self) -> bool:
        """True if device has queried Pi‑hole within away_time."""
        last = self.coordinator.data[self._mac].get(ATTR_LAST_QUERY)
        if last is None:
            return False
        return (datetime.now(timezone.utc).timestamp() - last) <= self._away

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        last = self.coordinator.data[self._mac].get(ATTR_LAST_QUERY)
        return {
            "last_query": datetime.fromtimestamp(last, timezone.utc).isoformat() if last else None,
        }

    @property
    def device_info(self) -> DeviceInfo:
        """Attach tracker to existing device by MAC."""
        info = self.coordinator.data[self._mac]
        return DeviceInfo(
            connections={(CONNECTION_NETWORK_MAC, self._mac)},
            name=info.get(ATTR_NAME) or None,
            manufacturer=info.get(ATTR_MAC_VENDOR),
            model=None,
        )
