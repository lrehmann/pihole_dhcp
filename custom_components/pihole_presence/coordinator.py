from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any, Dict

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import LEASES_ENDPOINT, DEVICES_ENDPOINT

_LOGGER = logging.getLogger(__name__)

class PiholeUpdateCoordinator(DataUpdateCoordinator[Dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, host: str, scan_interval: int):
        self._host = host.rstrip("/")
        self._session = async_get_clientsession(hass)
        super().__init__(
            hass, _LOGGER, name="Pi‑hole DHCP", update_interval=timedelta(seconds=scan_interval)
        )

    async def _async_update_data(self) -> Dict[str, Any]:
        leases_url = f"{self._host}{LEASES_ENDPOINT}"
        devices_url = f"{self._host}{DEVICES_ENDPOINT}"
        try:
            async with self._session.get(leases_url, timeout=10) as resp:
                leases_json = await resp.json(content_type=None)
            async with self._session.get(devices_url, timeout=10) as resp:
                devices_json = await resp.json(content_type=None)
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            raise UpdateFailed(err) from err

        leases = leases_json.get("leases", [])
        devices = devices_json.get("devices", [])
        merged: Dict[str, Dict[str, Any]] = {}

        for lease in leases:
            mac = lease.get("hwaddr", "").lower()
            if not mac:
                continue
            entry = merged.setdefault(mac, {"ips": set()})
            entry["ips"].add(lease.get("ip"))
            if lease.get("name") and lease["name"] != "*":
                entry["name"] = lease["name"]
            entry["dhcp_expires"] = lease.get("expires")

        for dev in devices:
            mac = dev.get("hwaddr", "").lower()
            if not mac:
                continue
            entry = merged.setdefault(mac, {"ips": set()})
            entry.update({
                "interface": dev.get("interface"),
                "first_seen": dev.get("firstSeen"),
                "last_query": dev.get("lastQuery"),
                "num_queries": dev.get("numQueries"),
                "mac_vendor": dev.get("macVendor"),
            })
            for ip_entry in dev.get("ips", []):
                if ip := ip_entry.get("ip"):
                    entry["ips"].add(ip)
                if not entry.get("name") and (n := ip_entry.get("name")) and n != "*":
                    entry["name"] = n

        for info in merged.values():
            info["ips"] = ", ".join(sorted(info.get("ips", [])))

        return merged