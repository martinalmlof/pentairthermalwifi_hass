# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Home Assistant custom integration for Pentair Thermal WiFi thermostats (Senz WiFi floor thermostats). The integration uses the `pypentairthermalwifi` library (published on PyPI) for device communication.

## Architecture

### Directory Structure
- `custom_components/pentairthermalwifi/` - Main integration code
  - `__init__.py` - Integration setup and config entry management
  - `manifest.json` - Integration metadata and dependencies
  - `config_flow.py` - UI configuration flow
  - `const.py` - Constants and configuration keys
  - `climate.py` - Climate entity (thermostat)
  - `sensor.py` - Temperature and other sensors
  - `switch.py` - Control switches
  - `binary_sensor.py` - Status binary sensors
  - `strings.json` - UI strings for config flow
  - `translations/en.json` - English translations

### Integration Flow
1. User adds integration via UI config flow (`config_flow.py`)
2. Config entry is created with email/password credentials
3. `async_setup_entry()` in `__init__.py` initializes the pypentairthermalwifi client
4. Coordinator fetches initial data and starts push notification monitoring
5. Client is stored in `hass.data[DOMAIN][entry.entry_id]`
6. Platforms (climate, sensor, etc.) are loaded and create entities
7. Each entity reads from coordinator data
8. When thermostats change, push notifications update the coordinator automatically

### Entity Structure
- All entities use `entry.entry_id` as the unique device identifier
- Entities share common `device_info` for proper device grouping in HA
- Climate entity is the primary control interface
- Additional sensors, switches, and binary sensors expose device capabilities

## Development Commands

### Running Tests
```bash
# Install test dependencies
pip install -r requirements_test.txt

# Run all tests
pytest

# Run with coverage report
pytest --cov=custom_components.pentairthermalwifi --cov-report=html

# Run specific test file
pytest tests/test_climate.py

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_climate.py::test_set_temperature
```

### Testing in Home Assistant
1. Copy integration to HA config: `cp -r custom_components/pentairthermalwifi /path/to/homeassistant/config/custom_components/`
2. Restart Home Assistant
3. Add integration via UI: Settings → Devices & Services → Add Integration

### Manual Testing
- Check HA logs: `tail -f /path/to/homeassistant/home-assistant.log | grep pentairthermalwifi`
- Enable debug logging in `configuration.yaml`:
  ```yaml
  logger:
    default: info
    logs:
      custom_components.pentairthermalwifi: debug
  ```

## Test Coverage

### Test Files
- `test_config_flow.py` - Config flow UI testing (success, auth failure, duplicate)
- `test_init.py` - Integration setup and unload
- `test_climate.py` - Climate entity state and actions
- `test_sensor.py` - Sensor entities
- `test_binary_sensor.py` - Binary sensor entities
- `test_coordinator.py` - Data coordinator polling and error handling

### What's Tested
✅ Config flow with valid/invalid credentials
✅ Integration setup and teardown
✅ Climate entity state attributes
✅ Temperature setting and HVAC mode changes
✅ Preset mode (comfort)
✅ Sensor values and availability
✅ Binary sensor states (heating, connectivity)
✅ Offline thermostat handling
✅ Coordinator data updates
✅ Error handling and recovery

### CI/CD
GitHub Actions workflow automatically runs tests on push/PR:
- Tests against Python 3.11 and 3.12
- HACS validation
- Hassfest validation (Home Assistant quality checks)

## Key Implementation Notes

- **Authentication**: Uses email/password via `pypentairthermalwifi` library to access cloud API
- **Config Flow**: UI-based configuration with credential validation
- **Data Coordinator**: Uses push notifications instead of polling for real-time updates
- **Push Notifications**: Long-polling API keeps connection open until thermostat state changes
- **Monitoring**: Automatically started when integration loads, stopped on unload
- **Entities**: One climate entity + sensors per thermostat, all linked via device_info
- **HVAC Modes**: Maps pypentairthermalwifi RegulationMode to HA HVACMode
  - OFF → HVACMode.OFF
  - MANUAL → HVACMode.HEAT
  - SCHEDULE → HVACMode.AUTO
  - COMFORT → Preset mode
- **Modern Patterns**: All async, CoordinatorEntity base, proper device grouping
- **Integration Type**: "device" with "cloud_push" IoT class (push notifications)
