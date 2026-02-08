"""Config flow for Pentair Thermal WiFi integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from pypentairthermalwifi import AsyncPentairThermalWifi, AuthenticationError

from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_EMAIL): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


class PentairThermalWiFiConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Pentair Thermal WiFi."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate credentials by attempting authentication
            try:
                async with AsyncPentairThermalWifi(
                    email=user_input[CONF_EMAIL],
                    password=user_input[CONF_PASSWORD],
                ) as client:
                    await client.authenticate()
                    # Use email as unique ID
                    await self.async_set_unique_id(user_input[CONF_EMAIL])
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=f"Pentair Thermal ({user_input[CONF_EMAIL]})",
                        data=user_input,
                    )
            except AuthenticationError:
                _LOGGER.error("Authentication failed with provided credentials")
                errors["base"] = "invalid_auth"
            except Exception as e:
                _LOGGER.exception("Unexpected error during authentication: %s", e)
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
