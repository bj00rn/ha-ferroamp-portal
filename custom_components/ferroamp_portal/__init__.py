"""
Custom integration to integrate Saleryd HRV system with Home Assistant.
"""
import asyncio
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.loader import async_get_integration

from .api import ApiClient
from .const import (
    CONF_PASSWORD,
    CONF_SYSTEM_ID,
    CONF_USERNAME,
    DOMAIN,
    PLATFORMS,
    STARTUP_MESSAGE,
)
from .coordinator import FerroampPortalDataUpdateCoordinator

SCAN_INTERVAL = timedelta(seconds=5)

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})

    integration = await async_get_integration(hass, DOMAIN)
    _LOGGER.info(STARTUP_MESSAGE, integration.version)

    username = entry.data.get(CONF_USERNAME)
    password = entry.data.get(CONF_PASSWORD)
    system_id = entry.data.get(CONF_SYSTEM_ID)

    session = async_create_clientsession(hass, raise_for_status=True)
    client = ApiClient(session, username, password, system_id)
    try:
        await client.connect()
    except (asyncio.TimeoutError, TimeoutError) as ex:
        raise ConfigEntryNotReady(
            f"Timeout while connecting to Ferroamp Portal"
        ) from ex

    coordinator = FerroampPortalDataUpdateCoordinator(
        hass,
        client,
        update_interval=SCAN_INTERVAL,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Setup platforms
    for platform in PLATFORMS:
        if entry.options.get(platform, True):
            coordinator.platforms.append(platform)
            hass.async_add_job(
                hass.config_entries.async_forward_entry_setup(entry, platform)
            )

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    coordinator: FerroampPortalDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    coordinator.client.stop()

    unloaded = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
                if platform in coordinator.platforms
            ]
        )
    )
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
