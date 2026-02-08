"""Test fixtures for Pentair Thermal WiFi integration."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pypentairthermalwifi import (
    AuthResponse,
    Group,
    RegulationMode,
    Thermostat,
    ThermostatsResponse,
    UpdateThermostatResponse,
)

from homeassistant.const import CONF_EMAIL, CONF_PASSWORD


@pytest.fixture
def mock_auth_response():
    """Create a mock successful auth response."""
    return AuthResponse(
        session_id="test_session_123",
        new_account=False,
        error_code=0,
        role_type=1,
        email="test@example.com",
        language="en",
    )


@pytest.fixture
def mock_thermostat():
    """Create a mock thermostat."""
    return Thermostat(
        serial_number="1234567",
        room="Living Room",
        icon_id=1,
        group_name="Home",
        group_id=1,
        temperature=2150,  # 21.5°C
        regulation_mode=RegulationMode.MANUAL,
        vacation_enabled=False,
        vacation_begin_day="",
        vacation_end_day="",
        vacation_temperature=1500,
        comfort_temperature=2200,
        comfort_end_time="",
        comfort_override=0,
        manual_temperature=2100,  # 21.0°C
        last_primary_mode_is_auto=False,
        frost_temperature=500,
        frost_protection_is_enabled=False,
        first_warming_daysleft=0,
        boost_duration=0,
        boost_floor_temp=2700,
        boost_room_temp=2200,
        sensor_application=1,
        no_sensor_pwm_index=0,
        online=True,
        heating=True,
        early_start_of_heating=False,
        max_temp=3500,  # 35.0°C
        min_temp=500,  # 5.0°C
        error_code=0,
        confirmed=True,
        email="test@example.com",
        utc_offset_sec=3600,
        assigned=True,
        sw_version="1.2.3",
        has_been_assigned=True,
        selected_schedule=0,
        schedules=[],
    )


@pytest.fixture
def mock_thermostat_offline(mock_thermostat):
    """Create a mock offline thermostat."""
    thermostat = mock_thermostat
    thermostat.online = False
    thermostat.heating = False
    return thermostat


@pytest.fixture
def mock_thermostats_response(mock_thermostat):
    """Create a mock thermostats response."""
    group = Group(
        group_name="Home",
        group_id=1,
        group_color="#FF0000",
        thermostats=[mock_thermostat],
    )
    return ThermostatsResponse(groups=[group])


@pytest.fixture
def mock_update_response():
    """Create a mock update response."""
    return UpdateThermostatResponse(success=True)


@pytest.fixture
def mock_pentair_client(
    mock_auth_response,
    mock_thermostats_response,
    mock_thermostat,
    mock_update_response,
):
    """Create a mock Pentair Thermal WiFi client."""
    client = AsyncMock()
    client.authenticate = AsyncMock(return_value=mock_auth_response)
    client.get_thermostats = AsyncMock(return_value=mock_thermostats_response)
    client.get_thermostat = AsyncMock(return_value=mock_thermostat)
    client.update_thermostat = AsyncMock(return_value=mock_update_response)
    client.set_manual_temperature = AsyncMock(return_value=mock_update_response)
    client.turn_off = AsyncMock(return_value=mock_update_response)
    client.close = AsyncMock()
    return client


@pytest.fixture
def mock_config_entry():
    """Create a mock config entry."""
    from homeassistant.config_entries import ConfigEntry, ConfigEntryDisabler

    return ConfigEntry(
        version=1,
        minor_version=0,
        domain="pentairthermalwifi",
        title="Pentair Thermal (test@example.com)",
        data={
            CONF_EMAIL: "test@example.com",
            CONF_PASSWORD: "test_password",
        },
        source="user",
        entry_id="test_entry_id",
        unique_id="test@example.com",
        discovery_keys={},
        options={},
        subentries_data={},
    )


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations for all tests."""
    yield
