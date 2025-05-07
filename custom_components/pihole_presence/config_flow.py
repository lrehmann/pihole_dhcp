from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from .const import (
    DOMAIN,
    CONF_SCAN_INTERVAL,
    CONF_AWAY_TIME,
    DEFAULT_HOST,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_AWAY_TIME,
)

STEP_USER_DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
    vol.Required(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(int, vol.Range(min=5)),
    vol.Required(CONF_AWAY_TIME, default=DEFAULT_AWAY_TIME): vol.All(int, vol.Range(min=30)),
})

class PiholeDhcpConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Pi‑hole DHCP Presence config flow."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(
                title="Pi‑hole DHCP Presence",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
        )
