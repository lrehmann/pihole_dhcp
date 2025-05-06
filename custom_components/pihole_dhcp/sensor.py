# custom_components/pihole_dhcp/sensor.py

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

from .const import (
    DOMAIN,
    ATTR_INTERFACE,
    ATTR_FIRST_SEEN,
    ATTR_LAST_QUERY,
    ATTR_NUM_QUERIES,
    ATTR_IPS,
    ATTR_DHCP_EXPIRES,
    ATTR_MAC_VENDOR,
    ATTR_NAME,
)

# Map key → (Label, unit, diagnostic‐flag, is_timestamp)
_SENSOR_DEFS: Dict[str, tuple[str, str | None, bool, bool]] = {
    ATTR_INTERFACE:    ("Interface",          None,     False, False),
    ATTR_FIRST_SEEN:   ("First Seen",         None,     False, True),
    ATTR_LAST_QUERY:   ("Last Query",         None,     False, True),
    ATTR_NUM_QUERIES:  ("Query Count",        "queries",False, False),
    ATTR_IPS:          ("IP Addresses",       None,     False, False),
    ATTR_DHCP_EXPIRES: ("DHCP Lease Expires", None,     False, True),
    ATTR_MAC_VENDOR:   ("MAC Vendor",         None,     True,  False),
    ATTR_NAME:         ("Device Name",        None,     True,  False),
}

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Create one sensor per (mac, attribute)."""
    coord = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    sensors: List[SensorEntity] = []

    for mac in coord.data:
        for attr, (label, unit, diag, is_ts) in _SENSOR_DEFS.items():
            sensors.append(
                PiholeAttributeSensor(coord, mac, attr, label, unit, diag, is_ts)
            )

    async_add_entities(sensors)

class PiholeAttributeSensor(CoordinatorEntity, SensorEntity):
    """Generic sensor for one Pi‑hole DHCP field."""

    def __init__(
        self,
        coordinator,
        mac: str,
        attr: str,
        label: str,
        unit: str | None,
        diagnostic: bool,
        is_timestamp: bool,
    ) -> None:
        super().__init__(coordinator)
        self._mac = mac
        self._attr = attr
        key = attr.lower().replace("_", "")
        self._attr_unique_id = f"{DOMAIN}_{mac.replace(':','')}_{key}"
        self._attr_name = label
        self._attr_native_unit_of_measurement = unit
        if diagnostic:
            self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._is_ts = is_timestamp

    @property
    def native_value(self) -> Any:
        """Return the processed value for this attribute."""
        value = self.coordinator.data[self._mac].get(self._attr)
        if self._is_ts and isinstance(value, (int, float)):
            # convert UNIX timestamp -> ISO 8601 string
            return datetime.fromtimestamp(value, tz=timezone.utc).isoformat()
        return value

    @property
    def device_info(self) -> DeviceInfo:
        """Group under the existing device by MAC."""
        data = self.coordinator.data[self._mac]
        return DeviceInfo(
            connections={(CONNECTION_NETWORK_MAC, self._mac)},
            name=data.get(ATTR_NAME) or self._mac,
            manufacturer=data.get(ATTR_MAC_VENDOR),
            model=data.get(ATTR_INTERFACE),
        )
