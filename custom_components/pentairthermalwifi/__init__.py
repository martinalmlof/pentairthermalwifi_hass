"""The Pentair Thermal WiFi integration."""
from __future__ import annotations

import logging

from pypentairthermalwifi import AsyncPentairThermalWifi

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed

from .const import COORDINATOR, DOMAIN, PLATFORMS
from .coordinator import PentairThermalWiFiCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Pentair Thermal WiFi from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Create API client
    client = AsyncPentairThermalWifi(
        email=entry.data[CONF_EMAIL],
        password=entry.data[CONF_PASSWORD],
    )

    # Authenticate and verify credentials
    try:
        await client.authenticate()
    except Exception as err:
        await client.close()
        raise ConfigEntryAuthFailed(f"Authentication failed: {err}") from err

    # Create and setup coordinator
    coordinator = PentairThermalWiFiCoordinator(hass, client)

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    # Start monitoring for push notifications
    await coordinator.async_start_monitoring()

    # Store coordinator in hass.data
    hass.data[DOMAIN][entry.entry_id] = {
        COORDINATOR: coordinator,
    }

    # Forward entry setup to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        # Stop monitoring and close the client
        coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]
        await coordinator.async_stop_monitoring()
        await coordinator.client.close()

        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
