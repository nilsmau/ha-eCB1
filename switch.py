from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import cast

from homeassistant.components.switch import (
    SwitchDeviceClass,
    SwitchEntity,
    SwitchEntityDescription
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from . import WallboxCoordinator, WallboxEntity
from .const import *

#UPDATE_INTERVAL = 30

_LOGGER = logging.getLogger(__name__)

@dataclass
class WallboxSwitchEntityDescription(SwitchEntityDescription):
    device_class: SwitchDeviceClass | str | None = None

SWITCH_TYPES: dict[str, WallboxSwitchEntityDescription] = {
    CONF_AI_MODE_KEY: WallboxSwitchEntityDescription(
        key=CONF_AI_MODE_KEY,
        name="AI Mode",
        device_class=SwitchDeviceClass.SWITCH,
        icon="mdi:refresh-auto"
    )
}

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Create wallbox switch entities in HASS."""
    coordinator: WallboxCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            WallboxSwitch(coordinator, entry, description)
            for ent in coordinator.data
            if (description := SWITCH_TYPES.get(ent))
        ]
    )

class WallboxSwitch(WallboxEntity, SwitchEntity):
    """Representation of a Wallbox Switch"""

    def __init__(
        self,
        coordinator: WallboxCoordinator,
        entry: ConfigEntry,
        description: SwitchEntityDescription,
    ) -> None:
        """Initialize a Wallbox switch."""

        super().__init__(coordinator)
        self.entity_description = description
        self._attr_name = f"{entry.title} {description.name}"
        self._attr_is_on = coordinator.data[self.entity_description.key]
        self._attr_unique_id = f"{description.key}-{coordinator.data[CONF_DATA_KEY][CONF_SERIAL_NUMBER_KEY]}"

    @property
    def is_on(self) -> bool:
        """Return the state of the switch."""
        return self.coordinator.data[self.entity_description.key]

    def turn_on(self) -> None:
        if self.entity_description.key == "autostartstop":
            self.coordinator.data[self.entity_description.key] = True
            self.coordinator.aysnc_set_start_stop_mode(bool(1))

    async def async_turn_on(self) -> None:
        if self.entity_description.key == "autostartstop":
            self.coordinator.data[self.entity_description.key] = True
            await self.coordinator.aysnc_set_start_stop_mode(bool(1))

    def turn_off(self) -> None:
        if self.entity_description.key == "autostartstop":
            self.coordinator.data[self.entity_description.key] = False
            self.coordinator.aysnc_set_start_stop_mode(bool(0))

    async def async_turn_off(self) -> None:
        if self.entity_description.key == "autostartstop":
            self.coordinator.data[self.entity_description.key] = False
            await self.coordinator.aysnc_set_start_stop_mode(bool(0))

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_is_on = self.coordinator.data[self.entity_description.key]
        self.async_write_ha_state()
    # def update(self) -> str | None:
    #     _LOGGER.log(20, "update called")
    #     self.is_on = self.coordinator.data[description.key]
    #
    # async def async_update(self) -> str | None:
    #     _LOGGER.log(20, "async update called")
    #     self.is_on = self.coordinator.data[description.key]
