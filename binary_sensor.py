"""Home Assistant component for accessing the eCharge Hardy Barth eCB1 Wallbox API. The sensor component creates multiple sensors regarding wallbox performance."""
from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import cast

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from . import WallboxCoordinator, WallboxEntity
from .const import *

#UPDATE_INTERVAL = 30

_LOGGER = logging.getLogger(__name__)

@dataclass
class WallboxBinarySensorEntityDescription(BinarySensorEntityDescription):
    device_class: BinarySensorDeviceClass | str | None = None

BINARYSENSOR_TYPES: dict[str, WallboxBinarySensorEntityDescription] = {
    CONF_CONNECTED_KEY: WallboxBinarySensorEntityDescription(
        key=CONF_CONNECTED_KEY,
        name="Connected",
        device_class=BinarySensorDeviceClass.PLUG,
        icon="mdi:ev-plug-type2"
    )
}

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Create wallbox binary sensor entities in HASS."""
    coordinator: WallboxCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            WallboxBinarySensor(coordinator, entry, description)
            for ent in coordinator.data[CONF_DATA_KEY]
            if (description := BINARYSENSOR_TYPES.get(ent))
        ]
    )

class WallboxBinarySensor(WallboxEntity, BinarySensorEntity):
    """Representation of the Wallbox portal."""

    entity_description: WallboxBinarySensorEntityDescription


    def __init__(
        self,
        coordinator: WallboxCoordinator,
        entry: ConfigEntry,
        description: WallboxSensorEntityDescription,
    ) -> None:
        """Initialize a Wallbox sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_is_on = coordinator.data[CONF_DATA_KEY][CONF_CONNECTED_KEY]
        self._attr_name = f"{entry.title} {description.name}"
        self._attr_unique_id = f"{description.key}-{coordinator.data[CONF_DATA_KEY][CONF_SERIAL_NUMBER_KEY]}"

    def update(self) -> bool:
        self.is_on = coordinator.data[CONF_DATA_KEY][CONF_CONNECTED_KEY]
