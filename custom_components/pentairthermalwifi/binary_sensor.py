"""Binary sensor platform for Pentair Thermal WiFi integration."""
from __future__ import annotations

import logging

from pypentairthermalwifi import Thermostat

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
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
    """Set up the Pentair Thermal WiFi binary sensor platform."""
    coordinator: PentairThermalWiFiCoordinator = hass.data[DOMAIN][entry.entry_id][
        COORDINATOR
    ]

    # Create binary sensors for each thermostat
    entities = []
    for thermostat in coordinator.data.get_all_thermostats():
        entities.extend([
            PentairThermalWiFiHeatingSensor(coordinator, thermostat),
            PentairThermalWiFiConnectivitySensor(coordinator, thermostat),
        ])

    async_add_entities(entities)


class PentairThermalWiFiBinarySensorBase(CoordinatorEntity, BinarySensorEntity):
    """Base class for Pentair Thermal WiFi binary sensors."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: PentairThermalWiFiCoordinator,
        thermostat: Thermostat,
        sensor_type: str,
        device_class: BinarySensorDeviceClass | None = None,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._serial_number = thermostat.serial_number
        self._sensor_type = sensor_type
        self._attr_unique_id = f"{thermostat.serial_number}_{sensor_type}"
        self._attr_device_class = device_class
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


class PentairThermalWiFiHeatingSensor(PentairThermalWiFiBinarySensorBase):
    """Binary sensor for heating status."""

    _attr_name = "Heating"
    _attr_device_class = BinarySensorDeviceClass.HEAT

    def __init__(
        self,
        coordinator: PentairThermalWiFiCoordinator,
        thermostat: Thermostat,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(
            coordinator, thermostat, "heating", BinarySensorDeviceClass.HEAT
        )

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        if not super().available:
            return False
        thermostat = self._thermostat
        return thermostat is not None and thermostat.online

    @property
    def is_on(self) -> bool | None:
        """Return true if heating is active."""
        if thermostat := self._thermostat:
            return thermostat.heating
        return None


class PentairThermalWiFiConnectivitySensor(PentairThermalWiFiBinarySensorBase):
    """Binary sensor for connectivity status."""

    _attr_name = "Connectivity"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(
        self,
        coordinator: PentairThermalWiFiCoordinator,
        thermostat: Thermostat,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(
            coordinator, thermostat, "connectivity", BinarySensorDeviceClass.CONNECTIVITY
        )

    @property
    def is_on(self) -> bool | None:
        """Return true if device is online."""
        if thermostat := self._thermostat:
            return thermostat.online
        return None
