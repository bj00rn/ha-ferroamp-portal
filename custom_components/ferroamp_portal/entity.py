"""Entity"""

from homeassistant.helpers.entity import DeviceInfo, EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import slugify

from .const import DEFAULT_NAME, DOMAIN, MANUFACTURER
from .coordinator import FerroampPortalDataUpdateCoordinator


class FerroampPortalEntity(CoordinatorEntity):
    """Entity base class"""

    def __init__(
        self,
        coordinator: FerroampPortalDataUpdateCoordinator,
        entry_id,
        entity_description: EntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self._id = entry_id
        self.entity_description = entity_description
        self._attr_name = entity_description.name
        self._attr_unique_id = f"{entry_id}_{slugify(entity_description.name)}"
        self._id = entry_id

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name=DEFAULT_NAME,
            manufacturer=MANUFACTURER,
        )
