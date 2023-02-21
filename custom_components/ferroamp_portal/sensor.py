"""Sensor platform"""

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import UnitOfElectricCurrent, UnitOfEnergy, UnitOfPower
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import slugify

from .const import DEFAULT_NAME, DOMAIN
from .entity import FerroampPortalEntity


class FerroampPortalSensor(FerroampPortalEntity, SensorEntity):
    """Sensor base class."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        entry_id,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        self.entity_id = f"sensor.${DEFAULT_NAME}_${slugify(entity_description.name)}"

        super().__init__(coordinator, entry_id, entity_description)

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        value = self.coordinator.data.get(self.entity_description.key)
        if value:
            value = value[0] if isinstance(value, list) else value
            return value


# {'terminalId': '4:0', 'timestamp': '2023-02-20T13:56:54.818Z', 'powerActive': 3.9000000953674316, 'energyActiveMeter': 1103357, 'currentL1': 0.5, 'currentL2': 0.5, 'currentL3': 0.5, '__typename': 'EvseMeterValue'}

sensors = {
    "powerActive": {
        "klass": FerroampPortalSensor,
        "description": SensorEntityDescription(
            key="powerActive",
            icon="mdi:wrench-clock",
            name="EV Active power",
            device_class=SensorDeviceClass.POWER,
            native_unit_of_measurement=UnitOfPower.WATT,
            suggested_display_precision=1,
            suggested_unit_of_measurement=UnitOfPower.KILO_WATT,
        ),
    },
    "energyActiveMeter": {
        "klass": FerroampPortalSensor,
        "description": SensorEntityDescription(
            key="energyActiveMeter",
            icon="mdi:wrench-clock",
            name="EV Energy meter",
            device_class=SensorDeviceClass.ENERGY,
            native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
            state_class=SensorStateClass.TOTAL_INCREASING,
            suggested_display_precision=1,
            suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        ),
    },
    "currentL1": {
        "klass": FerroampPortalSensor,
        "description": SensorEntityDescription(
            key="currentL1",
            icon="mdi:wrench-clock",
            name="EV Current L1",
            device_class=SensorDeviceClass.CURRENT,
            native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
            suggested_display_precision=1,
        ),
    },
    "currentL2": {
        "klass": FerroampPortalSensor,
        "description": SensorEntityDescription(
            key="currentL2",
            icon="mdi:wrench-clock",
            name="EV Current L2",
            device_class=SensorDeviceClass.CURRENT,
            native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
            suggested_display_precision=1,
        ),
    },
    "currentL3": {
        "klass": FerroampPortalSensor,
        "description": SensorEntityDescription(
            key="currentL3",
            icon="mdi:wrench-clock",
            name="EV Current L3",
            device_class=SensorDeviceClass.CURRENT,
            native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
            suggested_display_precision=1,
        ),
    },
}


async def async_setup_entry(hass, entry, async_add_entities: AddEntitiesCallback):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        sensor.get("klass")(coordinator, entry.entry_id, sensor.get("description"))
        for sensor in sensors.values()
    ]

    async_add_entities(entities)
