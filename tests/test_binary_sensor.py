"""Test the Pentair Thermal WiFi binary sensor platform."""
from unittest.mock import patch

from homeassistant.core import HomeAssistant

from custom_components.pentairthermalwifi.const import DOMAIN


async def test_binary_sensor_entities(
    hass: HomeAssistant, mock_config_entry, mock_pentair_client
) -> None:
    """Test binary sensor entities are created with correct values."""
    mock_config_entry.add_to_hass(hass)

    with patch(
        "custom_components.pentairthermalwifi.AsyncPentairThermalWifi",
        return_value=mock_pentair_client,
    ):
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    # Test heating binary sensor
    heating_state = hass.states.get("binary_sensor.living_room_heating")
    assert heating_state
    assert heating_state.state == "on"  # heating=True in mock
    assert heating_state.attributes["device_class"] == "heat"

    # Test connectivity binary sensor
    connectivity_state = hass.states.get("binary_sensor.living_room_connectivity")
    assert connectivity_state
    assert connectivity_state.state == "on"  # online=True in mock
    assert connectivity_state.attributes["device_class"] == "connectivity"


async def test_heating_sensor_off_when_not_heating(
    hass: HomeAssistant, mock_config_entry, mock_pentair_client, mock_thermostat
) -> None:
    """Test heating sensor is off when not heating."""
    # Modify mock to show not heating
    mock_thermostat.heating = False
    mock_pentair_client.get_thermostat.return_value = mock_thermostat

    mock_config_entry.add_to_hass(hass)

    with patch(
        "custom_components.pentairthermalwifi.AsyncPentairThermalWifi",
        return_value=mock_pentair_client,
    ):
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    heating_state = hass.states.get("binary_sensor.living_room_heating")
    assert heating_state
    assert heating_state.state == "off"


async def test_connectivity_sensor_off_when_offline(
    hass: HomeAssistant, mock_config_entry, mock_pentair_client, mock_thermostat_offline
) -> None:
    """Test connectivity sensor is off when thermostat is offline."""
    mock_pentair_client.get_thermostat.return_value = mock_thermostat_offline

    mock_config_entry.add_to_hass(hass)

    with patch(
        "custom_components.pentairthermalwifi.AsyncPentairThermalWifi",
        return_value=mock_pentair_client,
    ):
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    connectivity_state = hass.states.get("binary_sensor.living_room_connectivity")
    assert connectivity_state
    assert connectivity_state.state == "off"


async def test_heating_sensor_unavailable_when_offline(
    hass: HomeAssistant, mock_config_entry, mock_pentair_client, mock_thermostat_offline
) -> None:
    """Test heating sensor is unavailable when thermostat is offline."""
    mock_pentair_client.get_thermostat.return_value = mock_thermostat_offline

    mock_config_entry.add_to_hass(hass)

    with patch(
        "custom_components.pentairthermalwifi.AsyncPentairThermalWifi",
        return_value=mock_pentair_client,
    ):
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    heating_state = hass.states.get("binary_sensor.living_room_heating")
    assert heating_state
    assert heating_state.state == "unavailable"
