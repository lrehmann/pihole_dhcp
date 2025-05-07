from __future__ import annotations
from datetime import datetime, timezone
from typing import Any

from homeassistant.components.device_tracker import TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC

from .const import DOMAIN, CONF_AWAY_TIME, ATTR_LAST_QUERY, ATTR_NAME, ATTR_MAC_VENDOR

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Create a device_tracker per MAC."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    away = data["away_time"]

    trackers = [
        PiholeTracker(coordinator, mac, away) for mac in coordinator.data
    ]
    async_add_entities(trackers)

class PiholeTracker(CoordinatorEntity, TrackerEntity):
    """Presence via Pi-hole device tracker."""
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator, mac: str, away_time: int) -> None:
        super().__init__(coordinator)
        self._mac = mac
        self._away = away_time
        self._attr_unique_id = f"{DOMAIN}_{mac.replace(':','')}_pihole"
        self._attr_name = "Presence via Pi-hole"

    @property
    def is_connected(self) -> bool:
        last = self.coordinator.data[self._mac].get(ATTR_LAST_QUERY)
        if not isinstance(last, (int, float)):
            # treat missing timestamp as away
            return False
        return (datetime.now(timezone.utc).timestamp() - last) <= self._away

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        last = self.coordinator.data[self._mac].get(ATTR_LAST_QUERY)
        return {
            "last_query": datetime.fromtimestamp(last, timezone.utc).isoformat()
            if isinstance(last, (int, float)) else None
        }

    @property
    def device_info(self) -> DeviceInfo:
        data = self.coordinator.data[self._mac]
        name = data.get(ATTR_NAME)
        if not name or name == "*" or not name.strip():
            name = self._mac
        return DeviceInfo(
            connections={(CONNECTION_NETWORK_MAC, self._mac)},
            name=name,
            manufacturer=data.get(ATTR_MAC_VENDOR),
            model=None,
        )
