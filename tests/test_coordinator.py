"""Test the Pentair Thermal WiFi coordinator."""
from unittest.mock import AsyncMock

import pytest
from pypentairthermalwifi import APIError

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.pentairthermalwifi.coordinator import (
    PentairThermalWiFiCoordinator,
)


async def test_coordinator_update_success(
    hass: HomeAssistant, mock_pentair_client, mock_thermostats_response
) -> None:
    """Test successful coordinator update."""
    coordinator = PentairThermalWiFiCoordinator(hass, mock_pentair_client)

    await coordinator.async_refresh()

    assert coordinator.data == mock_thermostats_response
    assert coordinator.last_update_success is True
    mock_pentair_client.get_thermostats.assert_called_once()


async def test_coordinator_update_failure(
    hass: HomeAssistant, mock_pentair_client
) -> None:
    """Test coordinator update failure."""
    mock_pentair_client.get_thermostats.side_effect = APIError("API Error")

    coordinator = PentairThermalWiFiCoordinator(hass, mock_pentair_client)

    await coordinator.async_refresh()

    assert coordinator.last_update_success is False


async def test_coordinator_push_notifications(
    hass: HomeAssistant, mock_pentair_client
) -> None:
    """Test coordinator uses push notifications instead of polling."""
    coordinator = PentairThermalWiFiCoordinator(hass, mock_pentair_client)

    # Verify no polling interval is set (we use push notifications)
    assert coordinator.update_interval is None
