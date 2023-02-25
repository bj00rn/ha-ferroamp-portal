"""Config flow for integration"""
import logging

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME, CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .api import ApiClient
from .const import CONF_SYSTEM_ID, DOMAIN, NAME

_LOGGER: logging.Logger = logging.getLogger(__package__)


class FerroampPortalFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for integration"""

    VERSION = 1

    def __init__(self):
        """Initialize."""
        self._errors = {}

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        self._errors = {}

        # Uncomment the next 2 lines if only a single instance of the integration is allowed:
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            try:
                await self._test_connection(
                    user_input[CONF_USERNAME],
                    user_input[CONF_PASSWORD],
                    user_input[CONF_SYSTEM_ID],
                )
            except Exception:
                self._errors["base"] = "connect"
            else:
                return self.async_create_entry(
                    title=user_input[CONF_NAME], data=user_input
                )
            return await self._show_config_form(user_input)

        # Provide defaults for form
        user_input = {}
        user_input[CONF_NAME] = NAME
        return await self._show_config_form(user_input)

    async def _show_config_form(self, user_input):  # pylint: disable=unused-argument
        """Show the configuration form to edit configuration data."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_NAME,
                        default=user_input.get(CONF_NAME),
                    ): str,
                    vol.Required(
                        CONF_USERNAME, default=user_input.get(CONF_USERNAME)
                    ): str,
                    vol.Required(
                        CONF_PASSWORD,
                    ): str,
                    vol.Required(
                        CONF_SYSTEM_ID, default=user_input.get(CONF_SYSTEM_ID)
                    ): int,
                }
            ),
            errors=self._errors,
        )

    async def _test_connection(self, username, password, system_id):
        """Return true if connection is working"""

        try:
            async with ApiClient(
                async_create_clientsession(self.hass, raise_for_status=True),
                username,
                password,
                system_id,
            ) as client:
                await client.connect()
        except Exception as e:  # pylint: disable=broad-except
            raise Exception("Could not connect") from e
