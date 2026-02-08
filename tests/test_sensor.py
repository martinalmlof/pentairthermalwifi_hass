"""Test the Pentair Thermal WiFi sensor platform."""
from unittest.mock import patch

from homeassistant.core import HomeAssistant

from custom_components.pentairthermalwifi.const import DOMAIN


async def test_sensor_entities(
    hass: HomeAssistant, mock_config_entry, mock_pentair_client
) -> None:
    """Test sensor entities are created with correct values."""
    mock_config_entry.add_to_hass(hass)

    with patch(
        "custom_components.pentairthermalwifi.AsyncPentairThermalWifi",
        return_value=mock_pentair_client,
    ):
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    # Test target temperature sensor
    target_temp_state = hass.states.get("sensor.living_room_target_temperature")
    assert target_temp_state
    assert target_temp_state.state == "21.0"
    assert target_temp_state.attributes["unit_of_measurement"] == "°C"
    assert target_temp_state.attributes["device_class"] == "temperature"

    # Test comfort temperature sensor
    comfort_temp_state = hass.states.get("sensor.living_room_comfort_temperature")
    assert comfort_temp_state
    assert comfort_temp_state.state == "22.0"
    assert comfort_temp_state.attributes["unit_of_measurement"] == "°C"
    assert comfort_temp_state.attributes["device_class"] == "temperature"


async def test_sensor_unavailable_when_offline(
    hass: HomeAssistant, mock_config_entry, mock_pentair_client, mock_thermostat_offline
) -> None:
    """Test sensors are unavailable when thermostat is offline."""
    # Update mock to return offline thermostat
    mock_pentair_client.get_thermostat.return_value = mock_thermostat_offline

    mock_config_entry.add_to_hass(hass)

    with patch(
        "custom_components.pentairthermalwifi.AsyncPentairThermalWifi",
        return_value=mock_pentair_client,
    ):
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    # Test target temperature sensor is unavailable
    target_temp_state = hass.states.get("sensor.living_room_target_temperature")
    assert target_temp_state
    assert target_temp_state.state == "unavailable"

    # Test comfort temperature sensor is unavailable
    comfort_temp_state = hass.states.get("sensor.living_room_comfort_temperature")
    assert comfort_temp_state
    assert comfort_temp_state.state == "unavailable"
