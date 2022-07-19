"""Home Assistant component for accessing the Wallbox Portal API. The sensor component creates multiple sensors regarding wallbox performance."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, cast

# from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import InvalidAuth, WallboxCoordinator, WallboxEntity
from .const import *
import logging

_LOGGER = logging.getLogger(__name__)

@dataclass
class WallboxNumberEntityDescription(NumberEntityDescription):
    """Describes Wallbox sensor entity."""



NUMBER_TYPES: dict[str, WallboxNumberEntityDescription] = {
    CONF_MAN_CHARGING_CURRENT_KEY: WallboxNumberEntityDescription(
        key=CONF_MAN_CHARGING_CURRENT_KEY,
        name="Manual Charging Current",
        native_min_value=6
    ),
}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Create wallbox sensor entities in HASS."""
    coordinator: WallboxCoordinator = hass.data[DOMAIN][entry.entry_id]
    # Check if the user is authorized to change current, if so, add number component:
    try:
        await coordinator.async_set_charging_current(
            coordinator.data[CONF_DATA_KEY][CONF_MAN_CHARGING_CURRENT_KEY]
        )
    except InvalidAuth:
        return

    async_add_entities(
        [
            WallboxNumber(coordinator, entry, description)
            for ent in coordinator.data[CONF_DATA_KEY]
            if (description := NUMBER_TYPES.get(ent))
        ]
    )


class WallboxNumber(WallboxEntity, NumberEntity):
    """Representation of the Wallbox portal."""

    entity_description: WallboxNumberEntityDescription

    def __init__(
        self,
        coordinator: WallboxCoordinator,
        entry: ConfigEntry,
        description: WallboxNumberEntityDescription,
    ) -> None:
        """Initialize a Wallbox sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        #self._coordinator = coordinator
        self._attr_name = f"{entry.title} {description.name}"
        self._attr_unique_id = f"{description.key}-{coordinator.data[CONF_DATA_KEY][CONF_SERIAL_NUMBER_KEY]}"
        self._attr_mode = "slider"



    # @property
    # def max_value(self) -> float:
    #     """Return the maximum available current."""
    #     if self.entity_description.key == CONF_MAN_CHARGING_CURRENT_KEY:
    #         return cast(float, self.coordinator.data[CONF_DATA_KEY][CONF_MAX_AVAILABLE_POWER_KEY])

    @property
    def native_max_value(self) -> float:
        """Return the maximum available current."""
        if self.entity_description.key == CONF_MAN_CHARGING_CURRENT_KEY:
            return cast(float, self.coordinator.data[CONF_DATA_KEY][CONF_MAX_AVAILABLE_POWER_KEY])


    # @property
    # def value(self) -> float | None:
    #     """Return the state of the sensor."""
    #     return cast(
    #         Optional[float], self.coordinator.data[CONF_DATA_KEY][self.entity_description.key]
    #     )

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        return cast(
            Optional[float], self.coordinator.data[CONF_DATA_KEY][self.entity_description.key]
        )

    async def async_set_native_value(self, value: float) -> None:
        """Set the value of the entity."""
        if self.entity_description.key == CONF_MAN_CHARGING_CURRENT_KEY:
            await self.coordinator.async_set_charging_current(value)
