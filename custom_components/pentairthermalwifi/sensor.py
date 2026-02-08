"""Sensor platform for Pentair Thermal WiFi integration."""
from __future__ import annotations

import logging

from pypentairthermalwifi import Thermostat

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import COORDINATOR, DOMAIN
from .coordinator import PentairThermalWiFiCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Pentair Thermal WiFi sensor platform."""
    coordinator: PentairThermalWiFiCoordinator = hass.data[DOMAIN][entry.entry_id][
        COORDINATOR
    ]

    # Create sensors for each thermostat
    entities = []
    for thermostat in coordinator.data.get_all_thermostats():
        entities.extend([
            PentairThermalWiFiTargetTemperatureSensor(coordinator, thermostat),
            PentairThermalWiFiComfortTemperatureSensor(coordinator, thermostat),
        ])

    async_add_entities(entities)


class PentairThermalWiFiSensorBase(CoordinatorEntity, SensorEntity):
    """Base class for Pentair Thermal WiFi sensors."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: PentairThermalWiFiCoordinator,
        thermostat: Thermostat,
        sensor_type: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._serial_number = thermostat.serial_number
        self._sensor_type = sensor_type
        self._attr_unique_id = f"{thermostat.serial_number}_{sensor_type}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, thermostat.serial_number)},
            "name": thermostat.room,
            "manufacturer": "Pentair Thermal",
            "model": "Senz WiFi",
            "sw_version": thermostat.sw_version,
        }

    @property
    def _thermostat(self) -> Thermostat | None:
        """Get the current thermostat data from coordinator."""
        return self.coordinator.data.get_thermostat(self._serial_number)

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        if not super().available:
            return False
        thermostat = self._thermostat
        return thermostat is not None and thermostat.online


class PentairThermalWiFiTargetTemperatureSensor(PentairThermalWiFiSensorBase):
    """Sensor for target temperature."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_name = "Target temperature"

    def __init__(
        self,
        coordinator: PentairThermalWiFiCoordinator,
        thermostat: Thermostat,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, thermostat, "target_temperature")

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if thermostat := self._thermostat:
            return thermostat.manual_temperature_celsius
        return None


class PentairThermalWiFiComfortTemperatureSensor(PentairThermalWiFiSensorBase):
    """Sensor for comfort temperature."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_name = "Comfort temperature"

    def __init__(
        self,
        coordinator: PentairThermalWiFiCoordinator,
        thermostat: Thermostat,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, thermostat, "comfort_temperature")

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if thermostat := self._thermostat:
            return thermostat.comfort_temperature_celsius
        return None
