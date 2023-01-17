"""Home Assistant component for accessing the eCharge Hardy Barth eCB1 Wallbox API. The sensor component creates multiple sensors regarding wallbox performance."""
from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import cast

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import *
# (
#     ELECTRIC_CURRENT_AMPERE,
#     ENERGY_KILO_WATT_HOUR,
#     LENGTH_KILOMETERS,
#     PERCENTAGE,
#     POWER_KILO_WATT,
# )
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from . import WallboxCoordinator, WallboxEntity
from .const import *

# (
#     CONF_ADDED_ENERGY_KEY,
#     CONF_ADDED_RANGE_KEY,
#     CONF_CHARGING_POWER_KEY,
#     CONF_CHARGING_SPEED_KEY,
#     CONF_COST_KEY,
#     CONF_CURRENT_MODE_KEY,
#     CONF_DATA_KEY,
#     CONF_DEPOT_PRICE_KEY,
#     CONF_MAX_AVAILABLE_POWER_KEY,
#     CONF_MAX_CHARGING_CURRENT_KEY,
#     CONF_SERIAL_NUMBER_KEY,
#     CONF_STATE_OF_CHARGE_KEY,
#     CONF_STATUS_DESCRIPTION_KEY,
#     DOMAIN,
# )

UPDATE_INTERVAL = 30

_LOGGER = logging.getLogger(__name__)


@dataclass
class WallboxSensorEntityDescription(SensorEntityDescription):
    """Describes Wallbox sensor entity."""
    precision: int | None = None

OBIS_SENSORS: dict[str, WallboxSensorEntityDescription] = {

    OBIS_ACTIVE_POWER_PLUS: WallboxSensorEntityDescription(
            key=OBIS_ACTIVE_POWER_PLUS,
            name='Active Power +',
            native_unit_of_measurement=POWER_WATT,
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_ACTIVE_POWER_PLUS_MIN: WallboxSensorEntityDescription(
            key=OBIS_ACTIVE_POWER_PLUS_MIN,
            name='Active Power + min ',
            native_unit_of_measurement=POWER_WATT,
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_ACTIVE_POWER_PLUS_MAX: WallboxSensorEntityDescription(
            key=OBIS_ACTIVE_POWER_PLUS_MAX,
            name='Active Power + max',
            native_unit_of_measurement=POWER_WATT,
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_ACTIVE_ENERGY_PLUS: WallboxSensorEntityDescription(
            key=OBIS_ACTIVE_ENERGY_PLUS,
            name='Active energy + ',
            native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
            device_class=SensorDeviceClass.ENERGY,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_ACTIVE_POWER_MINUS: WallboxSensorEntityDescription(
            key=OBIS_ACTIVE_POWER_MINUS,
            name='Active power -',
            native_unit_of_measurement=POWER_WATT,
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_ACTIVE_POWER_MINUS_MIN: WallboxSensorEntityDescription(
            key=OBIS_ACTIVE_POWER_MINUS_MIN,
            name='Active power - min ',
            native_unit_of_measurement=POWER_WATT,
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_ACTIVE_POWER_MINUS_MAX: WallboxSensorEntityDescription(
            key=OBIS_ACTIVE_POWER_MINUS_MAX,
            name='Active power - max ',
            native_unit_of_measurement=POWER_WATT,
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_ACTIVE_ENERGY_MINUS: WallboxSensorEntityDescription(
            key=OBIS_ACTIVE_ENERGY_MINUS,
            name='Active energy - ',
            native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
            device_class=SensorDeviceClass.ENERGY,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_REACTIVE_POWER_PLUS: WallboxSensorEntityDescription(
            key=OBIS_REACTIVE_POWER_PLUS,
            name='Reactive power +  ',
            native_unit_of_measurement=POWER_VOLT_AMPERE,
            device_class=SensorDeviceClass.REACTIVE_POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_REACTIVE_POWER_PLUS_MIN: WallboxSensorEntityDescription(
            key=OBIS_REACTIVE_POWER_PLUS_MIN,
            name='Reactive power +  min ',
            native_unit_of_measurement=POWER_VOLT_AMPERE,
            device_class=SensorDeviceClass.REACTIVE_POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_REACTIVE_POWER_PLUS_MAX: WallboxSensorEntityDescription(
            key=OBIS_REACTIVE_POWER_PLUS_MAX,
            name='Reactive power + max ',
            native_unit_of_measurement=POWER_VOLT_AMPERE,
            device_class=SensorDeviceClass.REACTIVE_POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_REACTIVE_POWER_MINUS: WallboxSensorEntityDescription(
            key=OBIS_REACTIVE_POWER_MINUS,
            name='Reactive power - ',
            native_unit_of_measurement=POWER_VOLT_AMPERE,
            device_class=SensorDeviceClass.REACTIVE_POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_REACTIVE_POWER_MINUS_MIN: WallboxSensorEntityDescription(
            key=OBIS_REACTIVE_POWER_MINUS_MIN,
            name='Reactive power - min ',
            native_unit_of_measurement=POWER_VOLT_AMPERE,
            device_class=SensorDeviceClass.REACTIVE_POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_REACTIVE_POWER_MINUS_MAX: WallboxSensorEntityDescription(
            key=OBIS_REACTIVE_POWER_MINUS_MAX,
            name='Reactive power - max ',
            native_unit_of_measurement=POWER_VOLT_AMPERE,
            device_class=SensorDeviceClass.REACTIVE_POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_APPARENT_POWER_PLUS: WallboxSensorEntityDescription(
            key=OBIS_APPARENT_POWER_PLUS,
            name='Apparent power + ',
            native_unit_of_measurement=POWER_VOLT_AMPERE,
            device_class=SensorDeviceClass.APPARENT_POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_APPARENT_POWER_PLUS_MIN: WallboxSensorEntityDescription(
            key=OBIS_APPARENT_POWER_PLUS_MIN,
            name='Apparent power + min ',
            native_unit_of_measurement=POWER_VOLT_AMPERE,
            device_class=SensorDeviceClass.APPARENT_POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_APPARENT_POWER_PLUS_MAX: WallboxSensorEntityDescription(
            key=OBIS_APPARENT_POWER_PLUS_MAX,
            name='Apparent power + max ',
            native_unit_of_measurement=POWER_VOLT_AMPERE,
            device_class=SensorDeviceClass.APPARENT_POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_APPARENT_POWER_MINUS: WallboxSensorEntityDescription(
            key=OBIS_APPARENT_POWER_MINUS,
            name='Apparent power - ',
            native_unit_of_measurement=POWER_VOLT_AMPERE,
            device_class=SensorDeviceClass.APPARENT_POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_APPARENT_POWER_MINUS_MIN: WallboxSensorEntityDescription(
            key=OBIS_APPARENT_POWER_MINUS_MIN,
            name='Apparent power - min ',
            native_unit_of_measurement=POWER_VOLT_AMPERE,
            device_class=SensorDeviceClass.APPARENT_POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_APPARENT_POWER_MINUS_MAX: WallboxSensorEntityDescription(
            key=OBIS_APPARENT_POWER_MINUS_MAX,
            name='Apparent power - max',
            native_unit_of_measurement=POWER_VOLT_AMPERE,
            device_class=SensorDeviceClass.APPARENT_POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_POWER_FACTOR: WallboxSensorEntityDescription(
            key=OBIS_POWER_FACTOR,
            name='Power factor',
            native_unit_of_measurement=PERCENTAGE,
            device_class=SensorDeviceClass.POWER_FACTOR,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_POWER_FACTOR_MIN: WallboxSensorEntityDescription(
            key=OBIS_POWER_FACTOR_MIN,
            name='Power factor min',
            native_unit_of_measurement=PERCENTAGE,
            device_class=SensorDeviceClass.POWER_FACTOR,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_POWER_FACTOR_MAX: WallboxSensorEntityDescription(
            key=OBIS_POWER_FACTOR_MAX,
            name='Power factor max',
            native_unit_of_measurement=PERCENTAGE,
            device_class=SensorDeviceClass.POWER_FACTOR,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_SUPPLY_FREQUENCY: WallboxSensorEntityDescription(
            key=OBIS_SUPPLY_FREQUENCY,
            name='Supply frequency',
            native_unit_of_measurement=FREQUENCY_HERTZ,
            device_class=SensorDeviceClass.FREQUENCY,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_SUPPLY_FREQUENCY_MIN: WallboxSensorEntityDescription(
            key=OBIS_SUPPLY_FREQUENCY_MIN,
            name='Supply frequency min',
            native_unit_of_measurement=FREQUENCY_HERTZ,
            device_class=SensorDeviceClass.FREQUENCY,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_SUPPLY_FREQUENCY_MAX: WallboxSensorEntityDescription(
            key=OBIS_SUPPLY_FREQUENCY_MAX,
            name='Supply frequency max',
            native_unit_of_measurement=FREQUENCY_HERTZ,
            device_class=SensorDeviceClass.FREQUENCY,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_ACTIVE_POWER_PLUS_L1: WallboxSensorEntityDescription(
            key=OBIS_ACTIVE_POWER_PLUS_L1,
            name='Active power + (L1)',
            native_unit_of_measurement=POWER_WATT,
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_ACTIVE_POWER_PLUS_L1_MIN: WallboxSensorEntityDescription(
            key=OBIS_ACTIVE_POWER_PLUS_L1_MIN,
            name='Active power + (L1) min',
            native_unit_of_measurement=POWER_WATT,
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_ACTIVE_POWER_PLUS_L1_MAX: WallboxSensorEntityDescription(
            key=OBIS_ACTIVE_POWER_PLUS_L1_MAX,
            name='Active power + (L1) max',
            native_unit_of_measurement=POWER_WATT,
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_ACTIVE_ENERGY_PLUS_L1: WallboxSensorEntityDescription(
            key=OBIS_ACTIVE_ENERGY_PLUS_L1,
            name='Active energy + (L1)',
            native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
            device_class=SensorDeviceClass.ENERGY,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_ACTIVE_POWER_MINUS_L1: WallboxSensorEntityDescription(
            key=OBIS_ACTIVE_POWER_MINUS_L1,
            name='Active power - (L1)',
            native_unit_of_measurement=POWER_WATT,
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_ACTIVE_POWER_MINUS_L1_MIN: WallboxSensorEntityDescription(
            key=OBIS_ACTIVE_POWER_MINUS_L1_MIN,
            name='Active power - (L1) min',
            native_unit_of_measurement=POWER_WATT,
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_ACTIVE_POWER_MINUS_L1_MAX: WallboxSensorEntityDescription(
            key=OBIS_ACTIVE_POWER_MINUS_L1_MAX,
            name='Active power - (L1) max',
            native_unit_of_measurement=POWER_WATT,
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_ACTIVE_ENERGY_MINUS_L1: WallboxSensorEntityDescription(
            key=OBIS_ACTIVE_ENERGY_MINUS_L1,
            name='Active energy - (L1)',
            native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
            device_class=SensorDeviceClass.ENERGY,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_REACTIVE_POWER_PLUS_L1: WallboxSensorEntityDescription(
            key=OBIS_REACTIVE_POWER_PLUS_L1,
            name='Reactive power + (L1)',
            native_unit_of_measurement=POWER_VOLT_AMPERE,
            device_class=SensorDeviceClass.REACTIVE_POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_REACTIVE_POWER_PLUS_L1_MIN: WallboxSensorEntityDescription(
            key=OBIS_REACTIVE_POWER_PLUS_L1_MIN,
            name='Reactive power + (L1) min',
            native_unit_of_measurement=POWER_VOLT_AMPERE,
            device_class=SensorDeviceClass.REACTIVE_POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_REACTIVE_POWER_PLUS_L1_MAX: WallboxSensorEntityDescription(
            key=OBIS_REACTIVE_POWER_PLUS_L1_MAX,
            name='Reactive power + (L1) max',
            native_unit_of_measurement=POWER_VOLT_AMPERE,
            device_class=SensorDeviceClass.REACTIVE_POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_REACTIVE_POWER_MINUS_L1: WallboxSensorEntityDescription(
            key=OBIS_REACTIVE_POWER_MINUS_L1,
            name='Reactive power - (L1)',
            native_unit_of_measurement=POWER_VOLT_AMPERE,
            device_class=SensorDeviceClass.REACTIVE_POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_REACTIVE_POWER_MINUS_L1_MIN: WallboxSensorEntityDescription(
            key=OBIS_REACTIVE_POWER_MINUS_L1_MIN,
            name='Reactive power - (L1) min',
            native_unit_of_measurement=POWER_VOLT_AMPERE,
            device_class=SensorDeviceClass.REACTIVE_POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_REACTIVE_POWER_MINUS_L1_MAX: WallboxSensorEntityDescription(
            key=OBIS_REACTIVE_POWER_MINUS_L1_MAX,
            name='Reactive power - (L1) max',
            native_unit_of_measurement=POWER_VOLT_AMPERE,
            device_class=SensorDeviceClass.REACTIVE_POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_APPARENT_POWER_PLUS_L1: WallboxSensorEntityDescription(
            key=OBIS_APPARENT_POWER_PLUS_L1,
            name='Apparent power + (L1)',
            native_unit_of_measurement=POWER_VOLT_AMPERE,
            device_class=SensorDeviceClass.APPARENT_POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_APPARENT_POWER_PLUS_L1_MIN: WallboxSensorEntityDescription(
            key=OBIS_APPARENT_POWER_PLUS_L1_MIN,
            name='Apparent power + (L1) min',
            native_unit_of_measurement=POWER_VOLT_AMPERE,
            device_class=SensorDeviceClass.APPARENT_POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_APPARENT_POWER_PLUS_L1_MAX: WallboxSensorEntityDescription(
            key=OBIS_APPARENT_POWER_PLUS_L1_MAX,
            name='Apparent power + (L1) max',
            native_unit_of_measurement=POWER_VOLT_AMPERE,
            device_class=SensorDeviceClass.APPARENT_POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_APPARENT_POWER_MINUS_L1: WallboxSensorEntityDescription(
            key=OBIS_APPARENT_POWER_MINUS_L1,
            name='Apparent power - (L1)',
            native_unit_of_measurement=POWER_VOLT_AMPERE,
            device_class=SensorDeviceClass.APPARENT_POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_APPARENT_POWER_MINUS_L1_MIN: WallboxSensorEntityDescription(
            key=OBIS_APPARENT_POWER_MINUS_L1_MIN,
            name='Apparent power - (L1) min',
            native_unit_of_measurement=POWER_VOLT_AMPERE,
            device_class=SensorDeviceClass.APPARENT_POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_APPARENT_POWER_MINUS_L1_MAX: WallboxSensorEntityDescription(
            key=OBIS_APPARENT_POWER_MINUS_L1_MAX,
            name='Apparent power - (L1) max ',
            native_unit_of_measurement=POWER_VOLT_AMPERE,
            device_class=SensorDeviceClass.APPARENT_POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_CURRENT_L1: WallboxSensorEntityDescription(
            key=OBIS_CURRENT_L1,
            name='Current (L1)',
            native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
            device_class=SensorDeviceClass.CURRENT,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_CURRENT_L1_MIN: WallboxSensorEntityDescription(
            key=OBIS_CURRENT_L1_MIN,
            name='Current (L1) min ',
            native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
            device_class=SensorDeviceClass.CURRENT,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_CURRENT_L1_MAX: WallboxSensorEntityDescription(
            key=OBIS_CURRENT_L1_MAX,
            name='Current (L1) max ',
            native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
            device_class=SensorDeviceClass.CURRENT,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_VOLTAGE_L1: WallboxSensorEntityDescription(
            key=OBIS_VOLTAGE_L1,
            name='Voltage (L1) ',
            native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
            device_class=SensorDeviceClass.VOLTAGE,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_VOLTAGE_L1_MIN: WallboxSensorEntityDescription(
            key=OBIS_VOLTAGE_L1_MIN,
            name='Voltage (L1) min',
            native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
            device_class=SensorDeviceClass.VOLTAGE,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_VOLTAGE_L1_MAX: WallboxSensorEntityDescription(
            key=OBIS_VOLTAGE_L1_MAX,
            name='Voltage (L1) max',
            native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
            device_class=SensorDeviceClass.VOLTAGE,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_POWER_FACTOR_L1: WallboxSensorEntityDescription(
            key=OBIS_POWER_FACTOR_L1,
            name='Power factor (L1)',
            native_unit_of_measurement=PERCENTAGE,
            device_class=SensorDeviceClass.POWER_FACTOR,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_POWER_FACTOR_L1_MIN: WallboxSensorEntityDescription(
            key=OBIS_POWER_FACTOR_L1_MIN,
            name='Power factor (L1) min ',
            native_unit_of_measurement=PERCENTAGE,
            device_class=SensorDeviceClass.POWER_FACTOR,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_POWER_FACTOR_L1_MAX: WallboxSensorEntityDescription(
            key=OBIS_POWER_FACTOR_L1_MAX,
            name='Power factor (L1) max ',
            native_unit_of_measurement=PERCENTAGE,
            device_class=SensorDeviceClass.POWER_FACTOR,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_ACTIVE_POWER_PLUS_L2: WallboxSensorEntityDescription(
            key=OBIS_ACTIVE_POWER_PLUS_L2,
            name='Active power + (L2)',
            native_unit_of_measurement=POWER_WATT,
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_ACTIVE_POWER_PLUS_L2_MIN: WallboxSensorEntityDescription(
            key=OBIS_ACTIVE_POWER_PLUS_L2_MIN,
            name='Active power + (L2) min ',
            native_unit_of_measurement=POWER_WATT,
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_ACTIVE_POWER_PLUS_L2_MAX: WallboxSensorEntityDescription(
            key=OBIS_ACTIVE_POWER_PLUS_L2_MAX,
            name='Active power + (L2) max ',
            native_unit_of_measurement=POWER_WATT,
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_ACTIVE_ENERGY_PLUS_L2: WallboxSensorEntityDescription(
            key=OBIS_ACTIVE_ENERGY_PLUS_L2,
            name='Active energy + (L2)',
            native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
            device_class=SensorDeviceClass.ENERGY,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_ACTIVE_POWER_MINUS_L2: WallboxSensorEntityDescription(
            key=OBIS_ACTIVE_POWER_MINUS_L2,
            name='Active power - (L2)',
            native_unit_of_measurement=POWER_WATT,
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_ACTIVE_POWER_MINUS_L2_MIN: WallboxSensorEntityDescription(
            key=OBIS_ACTIVE_POWER_MINUS_L2_MIN,
            name='Active power - (L2) min ',
            native_unit_of_measurement=POWER_WATT,
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_ACTIVE_POWER_MINUS_L2_MAX: WallboxSensorEntityDescription(
            key=OBIS_ACTIVE_POWER_MINUS_L2_MAX,
            name='Active power - (L2) max ',
            native_unit_of_measurement=POWER_WATT,
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_ACTIVE_ENERGY_MINUS_L2: WallboxSensorEntityDescription(
            key=OBIS_ACTIVE_ENERGY_MINUS_L2,
            name='Active energy - (L2) ',
            native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
            device_class=SensorDeviceClass.ENERGY,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_REACTIVE_POWER_PLUS_L2: WallboxSensorEntityDescription(
            key=OBIS_REACTIVE_POWER_PLUS_L2,
            name='Reactive power + (L2) ',
            native_unit_of_measurement=POWER_VOLT_AMPERE,
            device_class=SensorDeviceClass.REACTIVE_POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_REACTIVE_POWER_PLUS_L2_MIN: WallboxSensorEntityDescription(
            key=OBIS_REACTIVE_POWER_PLUS_L2_MIN,
            name='Reactive power + (L2) min ',
            native_unit_of_measurement=POWER_VOLT_AMPERE,
            device_class=SensorDeviceClass.REACTIVE_POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_REACTIVE_POWER_PLUS_L2_MAX: WallboxSensorEntityDescription(
            key=OBIS_REACTIVE_POWER_PLUS_L2_MAX,
            name='Reactive power + (L2) max ',
            native_unit_of_measurement=POWER_VOLT_AMPERE,
            device_class=SensorDeviceClass.REACTIVE_POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_REACTIVE_POWER_MINUS_L2: WallboxSensorEntityDescription(
            key=OBIS_REACTIVE_POWER_MINUS_L2,
            name='Reactive power - (L2) ',
            native_unit_of_measurement=POWER_VOLT_AMPERE,
            device_class=SensorDeviceClass.REACTIVE_POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_REACTIVE_POWER_MINUS_L2_MIN: WallboxSensorEntityDescription(
            key=OBIS_REACTIVE_POWER_MINUS_L2_MIN,
            name='Reactive power - (L2) min ',
            native_unit_of_measurement=POWER_VOLT_AMPERE,
            device_class=SensorDeviceClass.REACTIVE_POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_REACTIVE_POWER_MINUS_L2_MAX: WallboxSensorEntityDescription(
            key=OBIS_REACTIVE_POWER_MINUS_L2_MAX,
            name='Reactive power - (L2) max ',
            native_unit_of_measurement=POWER_VOLT_AMPERE,
            device_class=SensorDeviceClass.REACTIVE_POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_APPARENT_POWER_PLUS_L2: WallboxSensorEntityDescription(
            key=OBIS_APPARENT_POWER_PLUS_L2,
            name='Apparent power + (L2) ',
            native_unit_of_measurement=POWER_VOLT_AMPERE,
            device_class=SensorDeviceClass.APPARENT_POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_APPARENT_POWER_PLUS_L2_MIN: WallboxSensorEntityDescription(
            key=OBIS_APPARENT_POWER_PLUS_L2_MIN,
            name='Apparent power + (L2) min ',
            native_unit_of_measurement=POWER_VOLT_AMPERE,
            device_class=SensorDeviceClass.APPARENT_POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_APPARENT_POWER_PLUS_L2_MAX: WallboxSensorEntityDescription(
            key=OBIS_APPARENT_POWER_PLUS_L2_MAX,
            name='Apparent power + (L2) max ',
            native_unit_of_measurement=POWER_VOLT_AMPERE,
            device_class=SensorDeviceClass.APPARENT_POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_APPARENT_POWER_MINUS_L2: WallboxSensorEntityDescription(
            key=OBIS_APPARENT_POWER_MINUS_L2,
            name='Apparent power - (L2) ',
            native_unit_of_measurement=POWER_VOLT_AMPERE,
            device_class=SensorDeviceClass.APPARENT_POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_APPARENT_POWER_MINUS_L2_MIN: WallboxSensorEntityDescription(
            key=OBIS_APPARENT_POWER_MINUS_L2_MIN,
            name='Apparent power - (L2) min ',
            native_unit_of_measurement=POWER_VOLT_AMPERE,
            device_class=SensorDeviceClass.APPARENT_POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_APPARENT_POWER_MINUS_L2_MAX: WallboxSensorEntityDescription(
            key=OBIS_APPARENT_POWER_MINUS_L2_MAX,
            name='Apparent power - (L2) max ',
            native_unit_of_measurement=POWER_VOLT_AMPERE,
            device_class=SensorDeviceClass.APPARENT_POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_CURRENT_L2: WallboxSensorEntityDescription(
            key=OBIS_CURRENT_L2,
            name='Current (L2) ',
            native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
            device_class=SensorDeviceClass.CURRENT,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_CURRENT_L2_MIN: WallboxSensorEntityDescription(
            key=OBIS_CURRENT_L2_MIN,
            name='Current (L2) min',
            native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
            device_class=SensorDeviceClass.CURRENT,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_CURRENT_L2_MAX: WallboxSensorEntityDescription(
            key=OBIS_CURRENT_L2_MAX,
            name='Current (L2) max',
            native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
            device_class=SensorDeviceClass.CURRENT,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_VOLTAGE_L2: WallboxSensorEntityDescription(
            key=OBIS_VOLTAGE_L2,
            name='Voltage (L2)',
            native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
            device_class=SensorDeviceClass.VOLTAGE,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_VOLTAGE_L2_MIN: WallboxSensorEntityDescription(
            key=OBIS_VOLTAGE_L2_MIN,
            name='Voltage (L2) min',
            native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
            device_class=SensorDeviceClass.VOLTAGE,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_VOLTAGE_L2_MAX: WallboxSensorEntityDescription(
            key=OBIS_VOLTAGE_L2_MAX,
            name='Voltage (L2) max',
            native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
            device_class=SensorDeviceClass.VOLTAGE,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_POWER_FACTOR_L2: WallboxSensorEntityDescription(
            key=OBIS_POWER_FACTOR_L2,
            name='Power factor (L2)',
            native_unit_of_measurement=PERCENTAGE,
            device_class=SensorDeviceClass.POWER_FACTOR,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_POWER_FACTOR_L2_MIN: WallboxSensorEntityDescription(
            key=OBIS_POWER_FACTOR_L2_MIN,
            name='Power factor (L2) min ',
            native_unit_of_measurement=PERCENTAGE,
            device_class=SensorDeviceClass.POWER_FACTOR,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_POWER_FACTOR_L2_MAX: WallboxSensorEntityDescription(
            key=OBIS_POWER_FACTOR_L2_MAX,
            name='Power factor (L2) max ',
            native_unit_of_measurement=PERCENTAGE,
            device_class=SensorDeviceClass.POWER_FACTOR,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_ACTIVE_POWER_PLUS_L3: WallboxSensorEntityDescription(
            key=OBIS_ACTIVE_POWER_PLUS_L3,
            name='Active power + (L3)',
            native_unit_of_measurement=POWER_WATT,
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_ACTIVE_POWER_PLUS_L3_MIN: WallboxSensorEntityDescription(
            key=OBIS_ACTIVE_POWER_PLUS_L3_MIN,
            name='Active power + (L3) min ',
            native_unit_of_measurement=POWER_WATT,
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_ACTIVE_POWER_PLUS_L3_MAX: WallboxSensorEntityDescription(
            key=OBIS_ACTIVE_POWER_PLUS_L3_MAX,
            name='Active power + (L3) max ',
            native_unit_of_measurement=POWER_WATT,
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_ACTIVE_ENERGY_PLUS_L3: WallboxSensorEntityDescription(
            key=OBIS_ACTIVE_ENERGY_PLUS_L3,
            name='Active energy + (L3)',
            native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
            device_class=SensorDeviceClass.ENERGY,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_ACTIVE_POWER_MINUS_L3: WallboxSensorEntityDescription(
            key=OBIS_ACTIVE_POWER_MINUS_L3,
            name='Active power - (L3)',
            native_unit_of_measurement=POWER_WATT,
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_ACTIVE_POWER_MINUS_L3_MIN: WallboxSensorEntityDescription(
            key=OBIS_ACTIVE_POWER_MINUS_L3_MIN,
            name='Active power - (L3) min ',
            native_unit_of_measurement=POWER_WATT,
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_ACTIVE_POWER_MINUS_L3_MAX: WallboxSensorEntityDescription(
            key=OBIS_ACTIVE_POWER_MINUS_L3_MAX,
            name='Active power - (L3) max ',
            native_unit_of_measurement=POWER_WATT,
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_ACTIVE_ENERGY_MINUS_L3: WallboxSensorEntityDescription(
            key=OBIS_ACTIVE_ENERGY_MINUS_L3,
            name='Active energy - (L3) ',
            native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
            device_class=SensorDeviceClass.ENERGY,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_REACTIVE_POWER_PLUS_L3: WallboxSensorEntityDescription(
            key=OBIS_REACTIVE_POWER_PLUS_L3,
            name='Reactive power + (L3) ',
            native_unit_of_measurement=POWER_VOLT_AMPERE,
            device_class=SensorDeviceClass.REACTIVE_POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_REACTIVE_POWER_PLUS_L3_MIN: WallboxSensorEntityDescription(
            key=OBIS_REACTIVE_POWER_PLUS_L3_MIN,
            name='Reactive power + (L3) min ',
            native_unit_of_measurement=POWER_VOLT_AMPERE,
            device_class=SensorDeviceClass.REACTIVE_POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_REACTIVE_POWER_PLUS_L3_MAX: WallboxSensorEntityDescription(
            key=OBIS_REACTIVE_POWER_PLUS_L3_MAX,
            name='Reactive power + (L3) max ',
            native_unit_of_measurement=POWER_VOLT_AMPERE,
            device_class=SensorDeviceClass.REACTIVE_POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_REACTIVE_POWER_MINUS_L3: WallboxSensorEntityDescription(
            key=OBIS_REACTIVE_POWER_MINUS_L3,
            name='Reactive power - (L3) ',
            native_unit_of_measurement=POWER_VOLT_AMPERE,
            device_class=SensorDeviceClass.REACTIVE_POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_REACTIVE_POWER_MINUS_L3_MIN: WallboxSensorEntityDescription(
            key=OBIS_REACTIVE_POWER_MINUS_L3_MIN,
            name='Reactive power - (L3) min ',
            native_unit_of_measurement=POWER_VOLT_AMPERE,
            device_class=SensorDeviceClass.REACTIVE_POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_REACTIVE_POWER_MINUS_L3_MAX: WallboxSensorEntityDescription(
            key=OBIS_REACTIVE_POWER_MINUS_L3_MAX,
            name='Reactive power - (L3) max ',
            native_unit_of_measurement=POWER_VOLT_AMPERE,
            device_class=SensorDeviceClass.REACTIVE_POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_APPARENT_POWER_PLUS_L3: WallboxSensorEntityDescription(
            key=OBIS_APPARENT_POWER_PLUS_L3,
            name='Apparent power + (L3) ',
            native_unit_of_measurement=POWER_VOLT_AMPERE,
            device_class=SensorDeviceClass.APPARENT_POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_APPARENT_POWER_PLUS_L3_MIN: WallboxSensorEntityDescription(
            key=OBIS_APPARENT_POWER_PLUS_L3_MIN,
            name='Apparent power + (L3) min ',
            native_unit_of_measurement=POWER_VOLT_AMPERE,
            device_class=SensorDeviceClass.APPARENT_POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_APPARENT_POWER_PLUS_L3_MAX: WallboxSensorEntityDescription(
            key=OBIS_APPARENT_POWER_PLUS_L3_MAX,
            name='Apparent power + (L3) max ',
            native_unit_of_measurement=POWER_VOLT_AMPERE,
            device_class=SensorDeviceClass.APPARENT_POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_APPARENT_POWER_MINUS_L3: WallboxSensorEntityDescription(
            key=OBIS_APPARENT_POWER_MINUS_L3,
            name='Apparent power - (L3) ',
            native_unit_of_measurement=POWER_VOLT_AMPERE,
            device_class=SensorDeviceClass.APPARENT_POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_APPARENT_POWER_MINUS_L3_MIN: WallboxSensorEntityDescription(
            key=OBIS_APPARENT_POWER_MINUS_L3_MIN,
            name='Apparent power - (L3) min ',
            native_unit_of_measurement=POWER_VOLT_AMPERE,
            device_class=SensorDeviceClass.APPARENT_POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_APPARENT_POWER_MINUS_L3_MAX: WallboxSensorEntityDescription(
            key=OBIS_APPARENT_POWER_MINUS_L3_MAX,
            name='Apparent power - (L3) max ',
            native_unit_of_measurement=POWER_VOLT_AMPERE,
            device_class=SensorDeviceClass.APPARENT_POWER,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_CURRENT_L3: WallboxSensorEntityDescription(
            key=OBIS_CURRENT_L3,
            name='Current (L3) ',
            native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
            device_class=SensorDeviceClass.CURRENT,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_CURRENT_L3_MIN: WallboxSensorEntityDescription(
            key=OBIS_CURRENT_L3_MIN,
            name='Current (L3) min ',
            native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
            device_class=SensorDeviceClass.CURRENT,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_CURRENT_L3_MAX: WallboxSensorEntityDescription(
            key=OBIS_CURRENT_L3_MAX,
            name='Current (L3) max ',
            native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
            device_class=SensorDeviceClass.CURRENT,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_VOLTAGE_L3: WallboxSensorEntityDescription(
            key=OBIS_VOLTAGE_L3,
            name='Voltage (L3) ',
            native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
            device_class=SensorDeviceClass.VOLTAGE,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_VOLTAGE_L3_MIN: WallboxSensorEntityDescription(
            key=OBIS_VOLTAGE_L3_MIN,
            name='Voltage (L3) min ',
            native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
            device_class=SensorDeviceClass.VOLTAGE,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_VOLTAGE_L3_MAX: WallboxSensorEntityDescription(
            key=OBIS_VOLTAGE_L3_MAX,
            name='Voltage (L3) max ',
            native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
            device_class=SensorDeviceClass.VOLTAGE,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_POWER_FACTOR_L3: WallboxSensorEntityDescription(
            key=OBIS_POWER_FACTOR_L3,
            name='Power factor (L3) ',
            native_unit_of_measurement=PERCENTAGE,
            device_class=SensorDeviceClass.POWER_FACTOR,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_POWER_FACTOR_L3_MIN: WallboxSensorEntityDescription(
            key=OBIS_POWER_FACTOR_L3_MIN,
            name='Power factor (L3) min ',
            native_unit_of_measurement=PERCENTAGE,
            device_class=SensorDeviceClass.POWER_FACTOR,
            state_class=SensorStateClass.MEASUREMENT
        ),
    OBIS_POWER_FACTOR_L3_MAX: WallboxSensorEntityDescription(
            key=OBIS_POWER_FACTOR_L3_MAX,
            name='Power factor (L3) max ',
            native_unit_of_measurement=PERCENTAGE,
            device_class=SensorDeviceClass.POWER_FACTOR,
            state_class=SensorStateClass.MEASUREMENT
        )
}

SENSOR_TYPES: dict[str, WallboxSensorEntityDescription] = {
    # CONF_CHARGING_POWER_KEY: WallboxSensorEntityDescription(
    #     key=CONF_CHARGING_POWER_KEY,
    #     name="Charging Power",
    #     precision=2,
    #     native_unit_of_measurement=POWER_KILO_WATT,
    #     device_class=SensorDeviceClass.POWER,
    #     state_class=SensorStateClass.MEASUREMENT,
    # ),
    # CONF_MAX_AVAILABLE_POWER_KEY: WallboxSensorEntityDescription(
    #     key=CONF_MAX_AVAILABLE_POWER_KEY,
    #     name="Max Available Power",
    #     precision=0,
    #     native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
    #     device_class=SensorDeviceClass.CURRENT,
    #     state_class=SensorStateClass.MEASUREMENT,
    # ),
    # CONF_CHARGING_SPEED_KEY: WallboxSensorEntityDescription(
    #     key=CONF_CHARGING_SPEED_KEY,
    #     icon="mdi:speedometer",
    #     name="Charging Speed",
    #     precision=0,
    #     state_class=SensorStateClass.MEASUREMENT,
    # ),
    # CONF_ADDED_RANGE_KEY: WallboxSensorEntityDescription(
    #     key=CONF_ADDED_RANGE_KEY,
    #     icon="mdi:map-marker-distance",
    #     name="Added Range",
    #     precision=0,
    #     native_unit_of_measurement=LENGTH_KILOMETERS,
    #     state_class=SensorStateClass.TOTAL_INCREASING,
    # ),
    # CONF_ADDED_ENERGY_KEY: WallboxSensorEntityDescription(
    #     key=CONF_ADDED_ENERGY_KEY,
    #     name="Added Energy",
    #     precision=2,
    #     native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
    #     device_class=SensorDeviceClass.ENERGY,
    #     state_class=SensorStateClass.TOTAL_INCREASING,
    # ),
    # CONF_COST_KEY: WallboxSensorEntityDescription(
    #     key=CONF_COST_KEY,
    #     icon="mdi:ev-station",
    #     name="Cost",
    #     state_class=SensorStateClass.TOTAL_INCREASING,
    # ),
    # CONF_STATE_OF_CHARGE_KEY: WallboxSensorEntityDescription(
    #     key=CONF_STATE_OF_CHARGE_KEY,
    #     name="State of Charge",
    #     native_unit_of_measurement=PERCENTAGE,
    #     device_class=SensorDeviceClass.BATTERY,
    #     state_class=SensorStateClass.MEASUREMENT,
    # ),
    # CONF_CURRENT_MODE_KEY: WallboxSensorEntityDescription(
    #     key=CONF_CURRENT_MODE_KEY,
    #     icon="mdi:ev-station",
    #     name="Current Mode",
    # ),
    # CONF_DEPOT_PRICE_KEY: WallboxSensorEntityDescription(
    #     key=CONF_DEPOT_PRICE_KEY,
    #     icon="mdi:ev-station",
    #     name="Depot Price",
    #     precision=2,
    # ),
    # CONF_STATUS_DESCRIPTION_KEY: WallboxSensorEntityDescription(
    #     key=CONF_STATUS_DESCRIPTION_KEY,
    #     icon="mdi:ev-station",
    #     name="Status Description",
    # ),
    CONF_MAX_AVAILABLE_POWER_KEY: WallboxSensorEntityDescription(
        key=CONF_MAX_AVAILABLE_POWER_KEY,
        name="Max. Avail. Charging Current",
        native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    CONF_ACT_CHARGING_CURRENT_KEY: WallboxSensorEntityDescription(
        key=CONF_ACT_CHARGING_CURRENT_KEY,
        name="Actual Charging Current",
        native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # OBIS_KWH_OUT_KEY: WallboxSensorEntityDescription(
    #     key=OBIS_KWH_OUT_KEY,
    #     name="kWh Charged",
    #     native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
    #     device_class=SensorDeviceClass.ENERGY,
    #     state_class=SensorStateClass.MEASUREMENT
    # ),
    # OBIS_KWH_IN_KEY: WallboxSensorEntityDescription(
    #     key=OBIS_KWH_IN_KEY,
    #     name="kWh Received",
    #     native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
    #     device_class=SensorDeviceClass.ENERGY,
    #     state_class=SensorStateClass.MEASUREMENT
    # ),
    # OBIS_ACTIVE_POWER_PLUS: WallboxSensorEntityDescription(
    #     key=OBIS_ACTIVE_POWER_PLUS,
    #     name='Active Power +',
    #     native_unit_of_measurement=POWER_WATT,
    #     device_class=SensorDeviceClass.POWER,
    #     state_class=SensorStateClass.MEASUREMENT
    # )
}

SENSOR_TYPES = SENSOR_TYPES | OBIS_SENSORS

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Create wallbox sensor entities in HASS."""
    coordinator: WallboxCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            WallboxSensor(coordinator, entry, description)
            for ent in coordinator.data[CONF_DATA_KEY]
            if (description := SENSOR_TYPES.get(ent))
        ]
    )


class WallboxSensor(WallboxEntity, SensorEntity):
    """Representation of the Wallbox portal."""

    entity_description: WallboxSensorEntityDescription

    def __init__(
        self,
        coordinator: WallboxCoordinator,
        entry: ConfigEntry,
        description: WallboxSensorEntityDescription,
    ) -> None:
        """Initialize a Wallbox sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_name = f"{entry.title} {description.name}"
        self._attr_unique_id = f"{description.key}-{coordinator.data[CONF_DATA_KEY][CONF_SERIAL_NUMBER_KEY]}"

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if (sensor_round := self.entity_description.precision) is not None:
            return cast(
                StateType,
                round(self.coordinator.data[CONF_DATA_KEY][self.entity_description.key], sensor_round),
            )
        return cast(
                StateType,
                round(self.coordinator.data[CONF_DATA_KEY][self.entity_description.key], 2)
            )

    # def update(self) -> None:
    #     if (sensor_round := self.entity_description.precision) is not None:
    #         self._attr_native_value = cast(
    #             StateType,
    #             round(self.coordinator.data[CONF_DATA_KEY][self.entity_description.key], sensor_round),
    #         )
    #     self._attr_native_value = cast(
    #             StateType,
    #             round(self.coordinator.data[CONF_DATA_KEY][self.entity_description.key], 2)
    #         )
