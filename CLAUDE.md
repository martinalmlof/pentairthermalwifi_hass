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
2. Config entry is created with device host
3. `async_setup_entry()` in `__init__.py` initializes the pypentairthermalwifi client
4. Client is stored in `hass.data[DOMAIN][entry.entry_id]`
5. Platforms (climate, sensor, etc.) are loaded and create entities
6. Each entity uses the stored client to communicate with the device

### Entity Structure
- All entities use `entry.entry_id` as the unique device identifier
- Entities share common `device_info` for proper device grouping in HA
- Climate entity is the primary control interface
- Additional sensors, switches, and binary sensors expose device capabilities

## Development Commands

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

## Key Implementation Notes

- **Authentication**: Uses email/password via `pypentairthermalwifi` library to access cloud API
- **Config Flow**: UI-based configuration with credential validation
- **Data Coordinator**: Uses `DataUpdateCoordinator` for efficient polling (30s interval)
- **Entities**: One climate entity + sensors per thermostat, all linked via device_info
- **HVAC Modes**: Maps pypentairthermalwifi RegulationMode to HA HVACMode
  - OFF → HVACMode.OFF
  - MANUAL → HVACMode.HEAT
  - SCHEDULE → HVACMode.AUTO
  - COMFORT → Preset mode
- **Modern Patterns**: All async, CoordinatorEntity base, proper device grouping
- **Integration Type**: "device" with "local_polling" IoT class (cloud-based API)
