# custom_components/pihole_dhcp/sensor.py

from __future__ import annotations

from typing import Any, Dict

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    ATTR_INTERFACE,
    ATTR_FIRST_SEEN,
    ATTR_LAST_QUERY,
    ATTR_NUM_QUERIES,
    ATTR_MAC_VENDOR,
    ATTR_IPS,
    ATTR_NAME,
    ATTR_DHCP_EXPIRES,
)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]

    async_add_entities(
        PiholeDiagnosticSensor(coordinator, mac) for mac in coordinator.data
    )

class PiholeDiagnosticSensor(CoordinatorEntity, SensorEntity):
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator, mac: str) -> None:
        super().__init__(coordinator)
        self._mac = mac
        # main state is the num_cycles (or num_queries)
        self._attr_unique_id = f"{DOMAIN}_{mac.replace(':','')}_num_queries"
        self._attr_name = f"{mac} Pi‑hole Queries"

    @property
    def native_value(self) -> int | None:
        return self.coordinator.data[self._mac].get("num_queries")

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        d = self.coordinator.data[self._mac]
        return {
            ATTR_INTERFACE: d.get("interface"),
            ATTR_FIRST_SEEN: d.get("first_seen"),
            ATTR_LAST_QUERY: d.get("last_query"),
            ATTR_MAC_VENDOR: d.get("mac_vendor"),
            ATTR_IPS: d.get("ips"),
            ATTR_NAME: d.get("name"),
            ATTR_DHCP_EXPIRES: d.get("dhcp_expires"),
        }

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device that this sensor belongs to."""
        data = self.coordinator.data[self._mac]
        return DeviceInfo(
            identifiers={(DOMAIN, self._mac)},
            name=data.get("name") or self._mac,
            manufacturer=data.get("mac_vendor"),
            model=data.get("interface"),
        )
