"""Home Assistant component for accessing the Wallbox Portal API. The sensor component creates multiple sensors regarding wallbox performance."""
from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import cast

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from . import WallboxCoordinator, WallboxEntity
from .const import *

_LOGGER = logging.getLogger(__name__)

SELECT_TYPES: dict[str, SelectEntityDescription] = {
    CONF_CHARGING_MODES_KEY: SelectEntityDescription(
        key=CONF_CHARGING_MODES_KEY,
        name="Charge Mode"
    ),
}

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    """Create wallbox lock entities in HASS."""
    coordinator: WallboxCoordinator = hass.data[DOMAIN][entry.entry_id]
    # Check if the user is authorized to lock, if so, add lock component

    async_add_entities(
        [
            WallboxModeSelector(coordinator, entry, description)
            for ent in coordinator.data
            if (description := SELECT_TYPES.get(ent))
        ]
    )

class WallboxModeSelector(WallboxEntity, SelectEntity):
    """Representation of a wallbox Mode Selector."""
    entity_description: SelectEntityDescription

    def __init__(
        self,
        coordinator: WallboxCoordinator,
        entry: ConfigEntry,
        description: SelectEntityDescription,
    ) -> None:

        """Initialize a Wallbox Mode Selector."""
        super().__init__(coordinator)

        self.entity_description = description
        self._attr_name = f"{entry.title} {description.name}"
        self._attr_unique_id = f"{description.key}-{coordinator.data[CONF_DATA_KEY][CONF_SERIAL_NUMBER_KEY]}"
        self._attr_current_option = coordinator.data[CONF_DATA_KEY][CONF_CURRENT_MODE_KEY]
        self._attr_options = coordinator.data[CONF_CHARGING_MODES_KEY]
        self._attr_available = True

    @property
    def current_option(self) -> str | None:
        """return the current preset"""
        return self.coordinator.data[CONF_DATA_KEY][CONF_CURRENT_MODE_KEY]


    async def async_select_option(self, option: str) -> None:
        """if user choses a different option send it to wallbox"""
        self._attr_current_option = option
        await self.coordinator.async_set_charging_mode(option)
