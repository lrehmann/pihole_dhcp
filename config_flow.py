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

STEP_SCHEMA = vol.Schema({
    vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
    vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(int, vol.Range(min=5)),
    vol.Optional(CONF_AWAY_TIME, default=DEFAULT_AWAY_TIME): vol.All(int, vol.Range(min=30)),
})

class PiholeDhcpConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Create the entry via UI."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="Pi‑hole DHCP", data=user_input)
        return self.async_show_form(step_id="user", data_schema=STEP_SCHEMA)

    async def async_step_reauth(self, user_input=None):
        # simple re‑auth → same as user
        return await self.async_step_user(user_input)

class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        data = {**self.config_entry.data, **self.config_entry.options}
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST, default=data.get(CONF_HOST, DEFAULT_HOST)): str,
                vol.Required(CONF_SCAN_INTERVAL, default=data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)): vol.All(int, vol.Range(min=5)),
                vol.Required(CONF_AWAY_TIME, default=data.get(CONF_AWAY_TIME, DEFAULT_AWAY_TIME)): vol.All(int, vol.Range(min=30)),
            }),
        )