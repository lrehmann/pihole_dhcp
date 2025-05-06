# custom_components/pihole_dhcp/sensor.py

from __future__ import annotations
from typing import Any, Dict, List

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

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

# Map internal keys → (friendly name, unit, diagnostic flag)
_SENSOR_DEFS: Dict[str, tuple[str, str | None, bool]] = {
    ATTR_INTERFACE:   ("Interface",         None, False),
    ATTR_FIRST_SEEN:  ("First Seen",        "timestamp", False),
    ATTR_LAST_QUERY:  ("Last Query",        "timestamp", False),
    ATTR_NUM_QUERIES: ("Query Count",       "queries",   False),
    ATTR_IPS:         ("IP Addresses",      None,        False),
    ATTR_DHCP_EXPIRES:("DHCP Lease Expires","timestamp",False),
    ATTR_MAC_VENDOR:  ("MAC Vendor",        None,        True),
    ATTR_NAME:        ("Device Name",       None,        True),
}

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Create one sensor per (mac, attribute)."""
    coord = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    sensors: List[SensorEntity] = []

    for mac in coord.data:
        for attr, (label, unit, is_diag) in _SENSOR_DEFS.items():
            sensors.append(
                PiholeAttributeSensor(coord, mac, attr, label, unit, is_diag)
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
    ) -> None:
        super().__init__(coordinator)
        self._mac = mac
        self._attr = attr
        self._attr = attr
        key = attr.replace("_", "")
        self._attr_unique_id = f"{DOMAIN}_{mac.replace(':','')}_{key}"
        self._attr_name = f"{mac} {label}"
        self._attr_native_unit_of_measurement = unit
        if diagnostic:
            self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self) -> Any:
        """Return the value of this attribute from coordinator data."""
        return self.coordinator.data[self._mac].get(self._attr)

    @property
    def device_info(self) -> DeviceInfo:
        """Group under one device per MAC."""
        data = self.coordinator.data[self._mac]
        return DeviceInfo(
            identifiers={(DOMAIN, self._mac)},
            name=data.get(ATTR_NAME) or self._mac,
            manufacturer=data.get(ATTR_MAC_VENDOR),
            model=data.get(ATTR_INTERFACE),
        )
