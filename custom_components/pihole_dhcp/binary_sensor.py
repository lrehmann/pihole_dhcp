# custom_components/pihole_dhcp/binary_sensor.py

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_AWAY_TIME

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    away_time = data["away_time"]

    async_add_entities(
        PiholePresenceBinarySensor(coordinator, mac, away_time)
        for mac in coordinator.data
    )

class PiholePresenceBinarySensor(CoordinatorEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.PRESENCE

    def __init__(self, coordinator, mac: str, away_time: int) -> None:
        super().__init__(coordinator)
        self._mac = mac
        self._away_time = away_time
        self._attr_unique_id = f"{DOMAIN}_{mac.replace(':','')}_presence"
        self._attr_name = f"{mac} present"

    @property
    def is_on(self) -> bool | None:
        last_query = self.coordinator.data[self._mac].get("last_query")
        if last_query is None:
            return None
        now = datetime.now(timezone.utc).timestamp()
        return (now - last_query) <= self._away_time

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "away_timeout": self._away_time,
            "last_query": self.coordinator.data[self._mac].get("last_query"),
        }

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device this presence sensor belongs to."""
        data = self.coordinator.data[self._mac]
        return DeviceInfo(
            identifiers={(DOMAIN, self._mac)},
            name=data.get("name") or self._mac,
            manufacturer=data.get("mac_vendor"),
            model=data.get("interface"),
        )
