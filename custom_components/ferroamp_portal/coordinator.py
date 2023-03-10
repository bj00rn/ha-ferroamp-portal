"""Data update coordinator"""

import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import ApiClient
from .const import DOMAIN

_LOGGER: logging.Logger = logging.getLogger(__package__)


class FerroampPortalDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass: HomeAssistant, client: ApiClient, update_interval) -> None:
        """Initialize."""
        self.platforms = []
        self.client = client
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=update_interval)

    async def _async_update_data(self):
        """Fetch the latest data from the source."""
        data = self.client.data
        return data
