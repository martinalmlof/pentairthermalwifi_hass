"""Test the Pentair Thermal WiFi coordinator."""
from datetime import timedelta
from unittest.mock import AsyncMock

import pytest
from pypentairthermalwifi import APIError

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed
from homeassistant.util import dt as dt_util

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


async def test_coordinator_polling_interval(
    hass: HomeAssistant, mock_pentair_client
) -> None:
    """Test coordinator respects polling interval."""
    coordinator = PentairThermalWiFiCoordinator(hass, mock_pentair_client)

    # Verify update interval is set correctly
    assert coordinator.update_interval == timedelta(seconds=30)
