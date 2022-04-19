"""The Wallbox integration."""
from __future__ import annotations

from datetime import timedelta
from http import HTTPStatus
import logging
from typing import Any

import requests
import operator

#from wallbox import Wallbox
from eCB1 import eCB1 as Wallbox

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, HomeAssistantError
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from homeassistant.helpers.entity import DeviceInfo
from .const import *
# (
#     CONF_BASEURL,
#     CONF_CURRENT_VERSION_KEY,
#     CONF_DATA_KEY,
#     CONF_LOCKED_UNLOCKED_KEY,
#     CONF_MAX_CHARGING_CURRENT_KEY,
#     CONF_NAME_KEY,
#     CONF_PART_NUMBER_KEY,
#     CONF_SERIAL_NUMBER_KEY,
#     CONF_SOFTWARE_KEY,
#     CONF_STATION,
#     CONF_STATUS_DESCRIPTION_KEY,
#     CONF_STATUS_ID_KEY,
#     DOMAIN,
# )

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR, Platform.LOCK, Platform.SELECT, Platform.BINARY_SENSOR, Platform.SWITCH, Platform.NUMBER]
#Platform.NUMBER,
#UPDATE_INTERVAL = 30

# Translation of StatusId based on Wallbox portal code:
# https://my.wallbox.com/src/utilities/charger/chargerStatuses.js
CHARGER_STATUS: dict[int, str] = {
    0: "Disconnected",
    14: "Error",
    15: "Error",
    161: "Ready",
    162: "Ready",
    163: "Disconnected",
    164: "Waiting",
    165: "Locked",
    166: "Updating",
    177: "Scheduled",
    178: "Paused",
    179: "Scheduled",
    180: "Waiting for car demand",
    181: "Waiting for car demand",
    182: "Paused",
    183: "Waiting in queue by Power Sharing",
    184: "Waiting in queue by Power Sharing",
    185: "Waiting in queue by Power Boost",
    186: "Waiting in queue by Power Boost",
    187: "Waiting MID failed",
    188: "Waiting MID safety margin exceeded",
    189: "Waiting in queue by Eco-Smart",
    193: "Charging",
    194: "Charging",
    195: "Charging",
    196: "Discharging",
    209: "Locked",
    210: "Locked",
}
CHARGING_MODES: dict[str, str] = {}

class WallboxCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Wallbox Coordinator class."""

    def __init__(self, station: str, wallbox: Wallbox, hass: HomeAssistant) -> None:
        """Initialize."""
        self._station = 1 #station
        self._wallbox = wallbox

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )

    def _authenticate(self) -> None:
        """Authenticate using Wallbox API."""
        try:
            self._wallbox.authenticate()
        except requests.exceptions.HTTPError as wallbox_connection_error:
            if wallbox_connection_error.response.status_code == HTTPStatus.FORBIDDEN:
                raise ConfigEntryAuthFailed from wallbox_connection_error
            raise ConnectionError from wallbox_connection_error

    def _validate(self) -> None:
        """Authenticate using Wallbox API."""
        try:
            self._wallbox.authenticate()
        except requests.exceptions.HTTPError as wallbox_connection_error:
            if wallbox_connection_error.response.status_code == 403:
                raise InvalidAuth from wallbox_connection_error
            raise ConnectionError from wallbox_connection_error

    async def async_validate_input(self) -> None:
        """Get new sensor data for Wallbox component."""
        await self.hass.async_add_executor_job(self._validate)

    def _get_data(self) -> dict[str, Any]:
        """Get new sensor data for Wallbox component."""
        try:
            self._authenticate()
            data: dict[str, Any] = self._wallbox.getChargerStatus(self._station)
            data[CONF_MAX_AVAILABLE_POWER_KEY] = data[CONF_DATA_KEY][CONF_MAX_AVAILABLE_POWER_KEY]

            system_info: dict[str, Any] = self._wallbox.getSystemInformation()

            #ata[CONF_NAME_KEY] = system_info['company']
            data[CONF_SYS_INFO_KEY] = system_info

            data[CONF_DATA_KEY][CONF_SERIAL_NUMBER_KEY] = system_info[CONF_SERIAL_NUMBER_KEY]
            data[CONF_LOCKED_UNLOCKED_KEY] = data[CONF_DATA_KEY][CONF_LOCKED_UNLOCKED_KEY]

            CHARGING_MODES = self._wallbox.getChargingModes()
            T = []
            for i in CHARGING_MODES:
                T.append(CHARGING_MODES[i])
            data[CONF_CHARGING_MODES_KEY] = T

            data[CONF_AI_MODE_KEY] = self._wallbox.getAutoStartStopMode(self._station)[CONF_AI_MODE_KEY]
            data[CONF_DATA_KEY] = data[CONF_DATA_KEY] | self._wallbox.getMetersData(self._station)[CONF_METERS_KEY]['data']

        #    data[CONF_STATUS_DESCRIPTION_KEY] = CHARGER_STATUS.get(
        #        data[CONF_STATUS_ID_KEY], "Unknown"
        #    )

            _LOGGER.log(20, data)
            return data

        except requests.exceptions.HTTPError as wallbox_connection_error:
            raise ConnectionError from wallbox_connection_error

    async def _async_update_data(self) -> dict[str, Any]:
        """Get new sensor data for Wallbox component."""
        return await self.hass.async_add_executor_job(self._get_data)

    def _set_charging_current(self, charging_current: float) -> None:
        """Set maximum charging current for Wallbox."""
        try:
            self._authenticate()
            self._wallbox.setMaxChargingCurrent(self._station, charging_current)
            self._get_data()
        except requests.exceptions.HTTPError as wallbox_connection_error:
            if wallbox_connection_error.response.status_code == 403:
                raise InvalidAuth from wallbox_connection_error
            raise ConnectionError from wallbox_connection_error

    async def async_set_charging_current(self, charging_current: float) -> None:
        """Set maximum charging current for Wallbox."""
        await self.hass.async_add_executor_job(
            self._set_charging_current, charging_current
        )
        await self.async_request_refresh()

    def _set_lock_unlock(self, lock: bool) -> None:
        """Set wallbox to locked or unlocked."""
        try:
            self._authenticate()
            if lock:
                self._wallbox.lockCharger(self._station)
            else:
                self._wallbox.unlockCharger(self._station)
            self._get_data()
        except requests.exceptions.HTTPError as wallbox_connection_error:
            if wallbox_connection_error.response.status_code == 403:
                raise InvalidAuth from wallbox_connection_error
            raise ConnectionError from wallbox_connection_error

    def _set_charging_mode(self, mode: str) -> None:
        """Set wallbox charging mode."""
        #_LOGGER.log(20, "updation mode to: '"+mode+"'")
        try:
            self._authenticate()
            self._wallbox.setChargingMode(self._station, mode)
            self._get_data()
        except requests.exceptions.HTTPError as wallbox_connection_error:
            if wallbox_connection_error.response.status_code == 403:
                raise InvalidAuth from wallbox_connection_error
            raise ConnectionError from wallbox_connection_error

    async def async_set_lock_unlock(self, lock: bool) -> None:
        """Set wallbox to locked or unlocked."""
        await self.hass.async_add_executor_job(self._set_lock_unlock, lock)
        await self.async_request_refresh()

    async def async_set_charging_mode(self, mode: str) -> None:
        """Set wallbox charging mode"""
        await self.hass.async_add_executor_job(self._set_charging_mode, mode)
        await self.async_request_refresh()

    def _set_start_stop_mode(self, onOrOff: bool) -> None:
        """Set wallbox AI Mode (Auto Start Stop -> PV Excess Charging)"""
        try:
            self._authenticate()
            self._wallbox.setAutoStartStopMode(self._station, onOrOff)
            self._get_data()
        except requests.exceptions.HTTPError as wallbox_connection_error:
            if wallbox_connection_error.response.status_code == 403:
                raise InvalidAuth from wallbox_connection_error
            raise ConnectionError from wallbox_connection_error

    async def aysnc_set_start_stop_mode(self, onOrOff: bool) -> None:
        """Set wallbox AI Mode (Auto Start Stop -> PV Excess Charging)"""
        await self.hass.async_add_executor_job(self._set_start_stop_mode, onOrOff)
        await self.async_request_refresh()


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Wallbox from a config entry."""
    wallbox = Wallbox(entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD], entry.data[CONF_BASEURL])
    wallbox_coordinator = WallboxCoordinator(
        entry.data[CONF_STATION],
        wallbox,
        hass,
    )

    try:
        await wallbox_coordinator.async_validate_input()

    except InvalidAuth as ex:
        raise ConfigEntryAuthFailed from ex

    await wallbox_coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = wallbox_coordinator

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""


class WallboxEntity(CoordinatorEntity[WallboxCoordinator]):
    """Defines a base Wallbox entity."""

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this Wallbox device."""
        return DeviceInfo(
            identifiers={
                (DOMAIN, self.coordinator.data[CONF_DATA_KEY][CONF_SERIAL_NUMBER_KEY])
            },
            name=f"Wallbox Smart Controller",
            manufacturer=f"{self.coordinator.data[CONF_SYS_INFO_KEY]['company']}",
            model=self.coordinator.data[CONF_DATA_KEY][CONF_PART_NUMBER_KEY],
            # sw_version=self.coordinator.data[CONF_DATA_KEY][CONF_SOFTWARE_KEY][
            #     CONF_CURRENT_VERSION_KEY
            # ],
            sw_version=self.coordinator.data[CONF_SYS_INFO_KEY]['os_version'],
        )
