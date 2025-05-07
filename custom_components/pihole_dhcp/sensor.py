from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, List

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC

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
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    sensors = [
        PiholeAttrSensor(coordinator, mac, attr, label)
        for mac in coordinator.data
        for attr, label in _SENSOR_DEFS
    ]
    async_add_entities(sensors)

class PiholeAttrSensor(CoordinatorEntity, SensorEntity):
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

        if attr == ATTR_NUM_QUERIES:
            self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        elif attr == ATTR_LAST_QUERY:
            self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> Any:
        data = self.coordinator.data[self._mac]
        val = data.get(self._attr)
        now_ts = datetime.now(timezone.utc).timestamp()

        if self._attr == ATTR_FIRST_SEEN and isinstance(val, (int, float)):
            return datetime.fromtimestamp(val, timezone.utc).isoformat()
        if self._attr == ATTR_LAST_QUERY and isinstance(val, (int, float)):
            return int(now_ts - val)
        if self._attr == ATTR_DHCP_EXPIRES and isinstance(val, (int, float)):
            return round((val - now_ts) / 3600, 1)
        return val

    @property
    def device_info(self) -> DeviceInfo:
        info = self.coordinator.data[self._mac]
        name = info.get(ATTR_NAME)
        if not name or name == "*" or not name.strip():
            name = self._mac
        return DeviceInfo(
            connections={(CONNECTION_NETWORK_MAC, self._mac)},
            name=name,
            manufacturer=info.get(ATTR_MAC_VENDOR),
            model=None,
        )
