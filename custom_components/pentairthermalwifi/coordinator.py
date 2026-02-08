"""DataUpdateCoordinator for Pentair Thermal WiFi integration."""
from __future__ import annotations

from datetime import timedelta
import logging

from pypentairthermalwifi import (
    AsyncPentairThermalWifi,
    PentairThermalWifiError,
    ThermostatsResponse,
)

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class PentairThermalWiFiCoordinator(DataUpdateCoordinator[ThermostatsResponse]):
    """Class to manage fetching Pentair Thermal WiFi data."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: AsyncPentairThermalWifi,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.client = client

    async def _async_update_data(self) -> ThermostatsResponse:
        """Fetch data from API."""
        try:
            return await self.client.get_thermostats()
        except PentairThermalWifiError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
