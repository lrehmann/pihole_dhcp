from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Dict, List

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC
from homeassistant.const import STATE_CLASS_TOTAL_INCREASING, STATE_CLASS_MEASUREMENT

from .const import (
    DOMAIN,
    ATTR_FIRST_SEEN,
    ATTR_LAST_QUERY,
    ATTR_NUM_QUERIES,
    ATTR_IPS,
    ATTR_DHCP_EXPIRES,
    ATTR_MAC_VENDOR,
    ATTR_NAME,
)

# Define which attributes to expose as sensors
# (key, label)
_SENSOR_DEFS: List[tuple[str, str]] = [
    (ATTR_FIRST_SEEN,   "First Seen"),
    (ATTR_LAST_QUERY,   "Last Query (s ago)"),
    (ATTR_NUM_QUERIES,  "Query Count"),
    (ATTR_IPS,          "IP Addresses"),
    (ATTR_DHCP_EXPIRES, "Lease Expires (h)"),
    (ATTR_MAC_VENDOR,   "MAC Vendor"),
    (ATTR_NAME,         "Device Name"),
]

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Pi-hole sensors from a config entry."""
    coord = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    sensors: List[SensorEntity] = []

    for mac in coord.data:
        for attr, label in _SENSOR_DEFS:
            sensors.append(
                PiholeAttrSensor(coord, mac, attr, label)
            )

    async_add_entities(sensors)

class PiholeAttrSensor(CoordinatorEntity, SensorEntity):
    """Generic diagnostic sensor for a Pi‑hole DHCP attribute."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self,
        coordinator,
        mac: str,
        attr: str,
        label: str,
    ) -> None:
        super().__init__(coordinator)
        self._mac = mac
        self._attr = attr
        key = attr.replace("_", "")
        self._attr_unique_id = f"{DOMAIN}_{mac.replace(':','')}_{key}"
        self._attr_name = label

        # Statistics for query count and last query
        if attr == ATTR_NUM_QUERIES:
            self._attr_state_class = STATE_CLASS_TOTAL_INCREASING
        elif attr == ATTR_LAST_QUERY:
            self._attr_state_class = STATE_CLASS_MEASUREMENT

    @property
    def native_value(self) -> Any:
        """Return formatted value for this attribute."""
        data = self.coordinator.data[self._mac]
        val = data.get(self._attr)
        now = datetime.now(timezone.utc).timestamp()

        if self._attr == ATTR_FIRST_SEEN and isinstance(val, (int, float)):
            return datetime.fromtimestamp(val, timezone.utc).isoformat()
        if self._attr == ATTR_LAST_QUERY and isinstance(val, (int, float)):
            return int(now - val)
        if self._attr == ATTR_DHCP_EXPIRES and isinstance(val, (int, float)):
            # hours remaining
            return round((val - now) / 3600, 1)
        return val

    @property
    def device_info(self) -> DeviceInfo:
        """Attach sensor to existing device by MAC."""
        info = self.coordinator.data[self._mac]
        return DeviceInfo(
            connections={(CONNECTION_NETWORK_MAC, self._mac)},
            name=info.get(ATTR_NAME) or None,
            manufacturer=info.get(ATTR_MAC_VENDOR),
            model=None,
        )
