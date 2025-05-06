from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant

from .const import (
    DOMAIN,
    CONF_SCAN_INTERVAL,
    CONF_AWAY_TIME,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_AWAY_TIME,
)
from .coordinator import PiholeUpdateCoordinator

_LOGGER = logging.getLogger(__name__)
PLATFORMS: list[str] = ["sensor", "binary_sensor"]
