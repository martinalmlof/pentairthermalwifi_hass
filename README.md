# Pentair Thermal WiFi for Home Assistant

A Home Assistant custom integration for Pentair Thermal WiFi thermostats (Senz WiFi floor thermostats).

## Features

- **Climate Control**: Full thermostat control with temperature setpoint
- **Sensors**: Temperature readings (floor temperature, etc.)
- **Switches**: Control heating modes and other device functions
- **Binary Sensors**: Status indicators (heating, connectivity, etc.)

## Installation

### Manual Installation

1. Copy the `custom_components/pentairthermalwifi` directory to your Home Assistant's `custom_components` directory
2. Restart Home Assistant
3. Add the integration through the UI: Settings → Devices & Services → Add Integration → Pentair Thermal WiFi

### HACS Installation

1. Add this repository as a custom repository in HACS
2. Install "Pentair Thermal WiFi" from HACS
3. Restart Home Assistant
4. Add the integration through the UI

## Configuration

The integration uses a config flow for easy setup through the Home Assistant UI. You'll need:

- **Email**: Your Pentair Thermal WiFi account email
- **Password**: Your Pentair Thermal WiFi account password

The integration connects to the Pentair Thermal cloud API to access your thermostats.

## Development

This integration uses the `pypentairthermalwifi` library to communicate with the devices.

### Requirements

- Home Assistant 2024.1.0 or newer
- `pypentairthermalwifi` Python package

## Support

For issues and feature requests, please use the [GitHub issue tracker](https://github.com/martinalmlof/pentairthermalwifi_hass/issues).
