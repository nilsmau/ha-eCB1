"""Config flow for Wallbox integration."""
from __future__ import annotations

from typing import Any

import logging
import voluptuous as vol
from eCB1 import eCB1 as Wallbox

from homeassistant import config_entries, core
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.data_entry_flow import FlowResult

from . import InvalidAuth, WallboxCoordinator
from .const import CONF_STATION, CONF_BASEURL, DOMAIN

_LOGGER = logging.getLogger(__name__)

COMPONENT_DOMAIN = DOMAIN

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_BASEURL, default="http://192.168.2.149/"): str,
        vol.Required(CONF_STATION, default=1): int,
        vol.Optional(CONF_USERNAME): str,
        vol.Optional(CONF_PASSWORD): str,

    }
)

STEP_SOCKETS_DATA_SCHEMA = vol.Schema({
    vol.Optional("Socket"): bool,
})


async def validate_input(
    hass: core.HomeAssistant, data: dict[str, Any]
) -> dict[str, str]:
    """Validate the user input allows to connect.
    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """

    return_value = {}

    try:
        data[CONF_USERNAME]
    except:
        data[CONF_USERNAME] = ""

    try:
        data[CONF_PASSWORD]
    except:
        data[CONF_PASSWORD] = ""

    if not data[CONF_BASEURL].endswith("/"):
        data[CONF_BASEURL] = data[CONF_BASEURL]+"/"
    wallbox = Wallbox(data["username"], data["password"], data[CONF_BASEURL])
    wallbox_coordinator = WallboxCoordinator(data[CONF_STATION], wallbox, hass)

    await wallbox_coordinator.async_validate_input()
    try:
        data['station_name'] = await hass.async_add_executor_job(wallbox.getMetersData, data['station'])
        data['station_name'] = data['station_name']['meter']['name']
    except:
        return_value.update({
            "error":"wrong socket",
            "title":""
        })
    else:
    # Return info that you want to store in the config entry.
        return_value.update({
            "title": "eCB1 "+data["station_name"],
            "error": ""
        })

    return return_value

class ConfigFlow(config_entries.ConfigFlow, domain=COMPONENT_DOMAIN):
    """Handle a config flow for Wallbox."""

    def __init__(self) -> None:
        """Start the Wallbox config flow."""
        self._reauth_entry: config_entries.ConfigEntry | None = None

    async def async_step_reauth(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Perform reauth upon an API authentication error."""
        self._reauth_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )

        return await self.async_step_user()

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None):
        errors: Dict[str, str] = {}

        """Original Configflow"""
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=STEP_USER_DATA_SCHEMA,
            )
        errors = {}

        try:
            await self.async_set_unique_id(user_input["url"]+str(user_input[CONF_STATION]))
            if not self._reauth_entry:
                self._abort_if_unique_id_configured()
                info = await validate_input(self.hass, user_input)
                if info['error'] is "":
                    return self.async_create_entry(title=info["title"], data=user_input)
                else:
                    return self.async_abort(reason="socket_not_found")
            if user_input[CONF_STATION] == self._reauth_entry.data[CONF_STATION]:
                self.hass.config_entries.async_update_entry(
                    self._reauth_entry, data=user_input, unique_id=user_input[CONF_BASEURL]
                )
                self.hass.async_create_task(
                    self.hass.config_entries.async_reload(self._reauth_entry.entry_id)
                )
                return self.async_abort(reason="reauth_successful")
            errors["base"] = "reauth_invalid"
        except ConnectionError:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
