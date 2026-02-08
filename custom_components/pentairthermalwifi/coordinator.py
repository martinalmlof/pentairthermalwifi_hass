"""DataUpdateCoordinator for Pentair Thermal WiFi integration."""
from __future__ import annotations

import logging

from pypentairthermalwifi import (
    AsyncPentairThermalWifi,
    Notification,
    PentairThermalWifiError,
    ThermostatsResponse,
)

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class PentairThermalWiFiCoordinator(DataUpdateCoordinator[ThermostatsResponse]):
    """Class to manage fetching Pentair Thermal WiFi data using push notifications."""

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
            # No update_interval - we use push notifications instead of polling
        )
        self.client = client
        self._monitoring_started = False

    async def _async_update_data(self) -> ThermostatsResponse:
        """Fetch data from API."""
        try:
            return await self.client.get_thermostats()
        except PentairThermalWifiError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

    async def async_start_monitoring(self) -> None:
        """Start monitoring for thermostat changes via push notifications."""
        if self._monitoring_started:
            _LOGGER.debug("Monitoring already started")
            return

        _LOGGER.info("Starting push notification monitoring")
        try:
            await self.client.start_monitoring(
                callback=self._handle_notification,
                error_callback=self._handle_error,
            )
            self._monitoring_started = True
        except Exception as err:
            _LOGGER.error("Failed to start monitoring: %s", err)
            raise

    async def async_stop_monitoring(self) -> None:
        """Stop monitoring for thermostat changes."""
        if not self._monitoring_started:
            return

        _LOGGER.info("Stopping push notification monitoring")
        try:
            await self.client.stop_monitoring()
        except Exception as err:
            _LOGGER.error("Error stopping monitoring: %s", err)
        finally:
            self._monitoring_started = False

    async def _handle_notification(self, notification: Notification) -> None:
        """Handle a notification from the API about a thermostat change.

        Args:
            notification: Notification with updated thermostat data
        """
        _LOGGER.info(
            "Received notification for thermostat %s (%s)",
            notification.thermostat.serial_number,
            notification.thermostat.room,
        )

        # Update the specific thermostat in our cached data
        if self.data:
            updated = False
            for group in self.data.groups:
                for i, thermostat in enumerate(group.thermostats):
                    if thermostat.serial_number == notification.thermostat.serial_number:
                        group.thermostats[i] = notification.thermostat
                        updated = True
                        break
                if updated:
                    break

            if updated:
                # Trigger coordinator update to notify all entities
                self.async_set_updated_data(self.data)
            else:
                _LOGGER.warning(
                    "Received notification for unknown thermostat: %s",
                    notification.thermostat.serial_number,
                )
        else:
            # No cached data yet, fetch all thermostats
            await self.async_refresh()

    async def _handle_error(self, error: Exception) -> None:
        """Handle an error from the monitoring loop.

        Args:
            error: The exception that occurred
        """
        _LOGGER.error("Error in monitoring loop: %s", error)
        self.last_update_success = False
        self.async_update_listeners()
