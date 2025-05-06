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

from .const import DOMAIN, ATTR_LAST_QUERY, ATTR_NAME, ATTR_MAC_VENDOR, ATTR_INTERFACE, CONF_AWAY_TIME

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    coord = data['coordinator']
    away = data['away_time']

    async_add_entities(
        PiholeTracker(coord, mac, away) for mac in coord.data
    )

class PiholeTracker(CoordinatorEntity, TrackerEntity):
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator, mac: str, away_time: int) -> None:
        super().__init__(coordinator)
        self._mac = mac
        self._away = away_time
        self._attr_unique_id = f"{DOMAIN}_{mac.replace(':','')}_pihole"
        self._attr_name = "Presence via Pi‑hole"

    @property
    def is_connected(self) -> bool | None:
        last = self.coordinator.data[self._mac].get(ATTR_LAST_QUERY)
        if last is None:
            return None
        return (datetime.now(timezone.utc).timestamp() - last) <= self._away

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        last = self.coordinator.data[self._mac].get(ATTR_LAST_QUERY)
        return {
            'last_query': datetime.fromtimestamp(last, timezone.utc).isoformat() if last else None,
        }

    @property
    def device_info(self) -> DeviceInfo:
        info = self.coordinator.data[self._mac]
        return DeviceInfo(
            connections={(CONNECTION_NETWORK_MAC, self._mac)},
            name=info.get(ATTR_NAME) or self._mac,
            manufacturer=info.get(ATTR_MAC_VENDOR),
            model=info.get(ATTR_INTERFACE),
        )
