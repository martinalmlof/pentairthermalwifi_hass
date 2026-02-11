"""Test the Pentair Thermal WiFi climate platform."""
from unittest.mock import AsyncMock, patch

import pytest
from pypentairthermalwifi import RegulationMode

from homeassistant.components.climate import (
    ATTR_HVAC_MODE,
    ATTR_PRESET_MODE,
    ATTR_TEMPERATURE,
    DOMAIN as CLIMATE_DOMAIN,
    SERVICE_SET_HVAC_MODE,
    SERVICE_SET_PRESET_MODE,
    SERVICE_SET_TEMPERATURE,
    HVACMode,
    PRESET_BOOST,
)
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant

from custom_components.pentairthermalwifi.const import DOMAIN


async def test_climate_entity_state(
    hass: HomeAssistant, mock_config_entry, mock_pentair_client
) -> None:
    """Test climate entity state."""
    mock_config_entry.add_to_hass(hass)

    with patch(
        "custom_components.pentairthermalwifi.AsyncPentairThermalWifi",
        return_value=mock_pentair_client,
    ):
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    # Get the climate entity
    entity_id = "climate.living_room"
    state = hass.states.get(entity_id)

    assert state
    assert state.state == HVACMode.HEAT
    assert state.attributes["current_temperature"] == 21.5
    assert state.attributes["temperature"] == 21.0
    assert state.attributes["min_temp"] == 5.0
    assert state.attributes["max_temp"] == 35.0
    assert state.attributes["hvac_action"] == "heating"


async def test_climate_entity_offline(
    hass: HomeAssistant, mock_config_entry, mock_pentair_client, mock_thermostat_offline
) -> None:
    """Test climate entity when thermostat is offline."""
    # Update mock to return offline thermostat
    mock_pentair_client.get_thermostat.return_value = mock_thermostat_offline

    mock_config_entry.add_to_hass(hass)

    with patch(
        "custom_components.pentairthermalwifi.AsyncPentairThermalWifi",
        return_value=mock_pentair_client,
    ):
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    # Get the climate entity
    entity_id = "climate.living_room"
    state = hass.states.get(entity_id)

    assert state
    assert state.state == "unavailable"


async def test_climate_boost_target_temperature(
    hass: HomeAssistant, mock_config_entry, mock_pentair_client, mock_thermostat_boost
) -> None:
    """Test that boost_room_temp is used as target temperature in boost mode."""
    mock_config_entry.add_to_hass(hass)

    with patch(
        "custom_components.pentairthermalwifi.AsyncPentairThermalWifi",
        return_value=mock_pentair_client,
    ):
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    state = hass.states.get("climate.living_room")
    assert state
    assert state.attributes["temperature"] == 25.0  # boost_room_temp=2500 → 25.0°C
    assert state.attributes["preset_mode"] == "boost"


async def test_set_temperature(
    hass: HomeAssistant, mock_config_entry, mock_pentair_client
) -> None:
    """Test setting temperature."""
    mock_config_entry.add_to_hass(hass)

    with patch(
        "custom_components.pentairthermalwifi.AsyncPentairThermalWifi",
        return_value=mock_pentair_client,
    ):
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    entity_id = "climate.living_room"

    # Call set temperature service
    await hass.services.async_call(
        CLIMATE_DOMAIN,
        SERVICE_SET_TEMPERATURE,
        {
            ATTR_ENTITY_ID: entity_id,
            ATTR_TEMPERATURE: 22.5,
        },
        blocking=True,
    )

    # Verify the API was called
    mock_pentair_client.set_manual_temperature.assert_called_once_with(
        "1234567", 22.5
    )


async def test_set_hvac_mode_off(
    hass: HomeAssistant, mock_config_entry, mock_pentair_client
) -> None:
    """Test setting HVAC mode to off."""
    mock_config_entry.add_to_hass(hass)

    with patch(
        "custom_components.pentairthermalwifi.AsyncPentairThermalWifi",
        return_value=mock_pentair_client,
    ):
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    entity_id = "climate.living_room"

    # Call set HVAC mode service
    await hass.services.async_call(
        CLIMATE_DOMAIN,
        SERVICE_SET_HVAC_MODE,
        {
            ATTR_ENTITY_ID: entity_id,
            ATTR_HVAC_MODE: HVACMode.OFF,
        },
        blocking=True,
    )

    # Verify the API was called
    mock_pentair_client.turn_off.assert_called_once_with("1234567")


async def test_set_hvac_mode_auto(
    hass: HomeAssistant, mock_config_entry, mock_pentair_client, mock_thermostat
) -> None:
    """Test setting HVAC mode to auto (schedule)."""
    mock_config_entry.add_to_hass(hass)

    with patch(
        "custom_components.pentairthermalwifi.AsyncPentairThermalWifi",
        return_value=mock_pentair_client,
    ):
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    entity_id = "climate.living_room"

    # Call set HVAC mode service
    await hass.services.async_call(
        CLIMATE_DOMAIN,
        SERVICE_SET_HVAC_MODE,
        {
            ATTR_ENTITY_ID: entity_id,
            ATTR_HVAC_MODE: HVACMode.AUTO,
        },
        blocking=True,
    )

    # Verify update_thermostat was called with SCHEDULE mode
    mock_pentair_client.update_thermostat.assert_called_once()
    call_args = mock_pentair_client.update_thermostat.call_args
    assert call_args[0][0] == "1234567"
    assert call_args[0][1].regulation_mode == RegulationMode.SCHEDULE


async def test_set_preset_mode_boost(
    hass: HomeAssistant, mock_config_entry, mock_pentair_client, mock_thermostat
) -> None:
    """Test setting preset mode to boost."""
    mock_config_entry.add_to_hass(hass)

    with patch(
        "custom_components.pentairthermalwifi.AsyncPentairThermalWifi",
        return_value=mock_pentair_client,
    ):
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    entity_id = "climate.living_room"

    # Call set preset mode service
    await hass.services.async_call(
        CLIMATE_DOMAIN,
        SERVICE_SET_PRESET_MODE,
        {
            ATTR_ENTITY_ID: entity_id,
            ATTR_PRESET_MODE: PRESET_BOOST,
        },
        blocking=True,
    )

    # Verify start_boost was called with the serial number and no end_time
    mock_pentair_client.start_boost.assert_called_once_with("1234567")
