"""Climate platform for Pentair Thermal WiFi integration."""
from __future__ import annotations

import logging
from typing import Any

from pypentairthermalwifi import RegulationMode, Thermostat

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
    PRESET_BOOST,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import COORDINATOR, DOMAIN
from .coordinator import PentairThermalWiFiCoordinator

_LOGGER = logging.getLogger(__name__)

# Map pypentairthermalwifi RegulationMode to HA HVAC modes
MODE_TO_HVAC = {
    RegulationMode.OFF: HVACMode.OFF,
    RegulationMode.MANUAL: HVACMode.HEAT,
    RegulationMode.BOOST: HVACMode.HEAT,
    RegulationMode.SCHEDULE: HVACMode.AUTO,
}

HVAC_TO_MODE = {
    HVACMode.OFF: RegulationMode.OFF,
    HVACMode.HEAT: RegulationMode.MANUAL,
    HVACMode.AUTO: RegulationMode.SCHEDULE,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Pentair Thermal WiFi climate platform."""
    coordinator: PentairThermalWiFiCoordinator = hass.data[DOMAIN][entry.entry_id][
        COORDINATOR
    ]

    # Create a climate entity for each thermostat
    entities = []
    for thermostat in coordinator.data.get_all_thermostats():
        entities.append(PentairThermalWiFiClimate(coordinator, thermostat))

    async_add_entities(entities)


class PentairThermalWiFiClimate(CoordinatorEntity, ClimateEntity):
    """Representation of a Pentair Thermal WiFi thermostat."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.TURN_OFF
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.PRESET_MODE
    )
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT, HVACMode.AUTO]
    _attr_preset_modes = [PRESET_BOOST]

    def __init__(
        self,
        coordinator: PentairThermalWiFiCoordinator,
        thermostat: Thermostat,
    ) -> None:
        """Initialize the climate entity."""
        super().__init__(coordinator)
        self._serial_number = thermostat.serial_number
        self._attr_unique_id = f"{thermostat.serial_number}_climate"
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

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        if thermostat := self._thermostat:
            return thermostat.temperature_celsius
        return None

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        if thermostat := self._thermostat:
            return thermostat.manual_temperature_celsius
        return None

    @property
    def min_temp(self) -> float:
        """Return the minimum temperature."""
        if thermostat := self._thermostat:
            return thermostat.min_temp_celsius
        return 5.0

    @property
    def max_temp(self) -> float:
        """Return the maximum temperature."""
        if thermostat := self._thermostat:
            return thermostat.max_temp_celsius
        return 35.0

    @property
    def hvac_mode(self) -> HVACMode:
        """Return current hvac mode."""
        if thermostat := self._thermostat:
            return MODE_TO_HVAC.get(
                RegulationMode(thermostat.regulation_mode), HVACMode.OFF
            )
        return HVACMode.OFF

    @property
    def hvac_action(self) -> str | None:
        """Return current hvac action."""
        if thermostat := self._thermostat:
            if thermostat.regulation_mode == RegulationMode.OFF:
                return "off"
            if thermostat.heating:
                return "heating"
            return "idle"
        return None

    @property
    def preset_mode(self) -> str | None:
        """Return the current preset mode."""
        if thermostat := self._thermostat:
            if thermostat.regulation_mode == RegulationMode.BOOST:
                return PRESET_BOOST
        return None

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is None:
            return

        _LOGGER.debug("Setting temperature to %s for %s", temperature, self._serial_number)
        await self.coordinator.client.set_manual_temperature(
            self._serial_number, temperature
        )
        await self.coordinator.async_request_refresh()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target hvac mode."""
        _LOGGER.debug("Setting HVAC mode to %s for %s", hvac_mode, self._serial_number)

        thermostat = self._thermostat
        if not thermostat:
            return

        if hvac_mode == HVACMode.OFF:
            await self.coordinator.client.turn_off(self._serial_number)
        else:
            # Update regulation mode
            regulation_mode = HVAC_TO_MODE.get(hvac_mode, RegulationMode.MANUAL)
            thermostat.regulation_mode = regulation_mode
            await self.coordinator.client.update_thermostat(
                self._serial_number, thermostat
            )

        await self.coordinator.async_request_refresh()

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode."""
        _LOGGER.debug("Setting preset mode to %s for %s", preset_mode, self._serial_number)

        thermostat = self._thermostat
        if not thermostat:
            return

        if preset_mode == PRESET_BOOST:
            await self.coordinator.client.start_boost(self._serial_number)
            await self.coordinator.async_request_refresh()
