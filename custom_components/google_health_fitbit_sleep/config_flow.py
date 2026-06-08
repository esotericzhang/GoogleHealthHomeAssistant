"""Config flow for Google Health Sleep."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import SOURCE_REAUTH
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import config_entry_oauth2_flow

from .const import (
    CONF_DAYS_TO_FETCH,
    DEFAULT_DAYS_TO_FETCH,
    DOMAIN,
    GOOGLE_HEALTH_API_BASE,
    MAX_DAYS_TO_FETCH,
    OAUTH2_SCOPES,
)

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entry_oauth2_flow.AbstractOAuth2FlowHandler, domain=DOMAIN):
    """Handle a Google Health Sleep config flow."""

    DOMAIN = DOMAIN
    VERSION = 1

    @property
    def logger(self) -> logging.Logger:
        """Return logger."""
        return _LOGGER

    @property
    def extra_authorize_data(self) -> dict[str, Any]:
        """Return extra authorization data."""
        return {
            "scope": " ".join(OAUTH2_SCOPES),
            "access_type": "offline",
            "prompt": "consent",
        }

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Pick an OAuth implementation."""
        return await super().async_step_user(user_input)

    async def async_step_reauth(
        self, entry_data: dict[str, Any]
    ) -> config_entries.ConfigFlowResult:
        """Handle re-authentication."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Confirm re-authentication."""
        if user_input is None:
            return self.async_show_form(
                step_id="reauth_confirm",
                data_schema=vol.Schema({}),
            )
        return await self.async_step_user()

    async def async_oauth_create_entry(
        self, data: dict[str, Any]
    ) -> config_entries.ConfigFlowResult:
        """Create an entry after OAuth succeeds."""
        try:
            identity = await self._async_get_identity(data)
        except Exception:
            _LOGGER.exception("Failed to get Google Health identity")
            return self.async_abort(reason="cannot_connect")

        user_id = identity.get("healthUserId") or identity.get("legacyUserId")
        if not user_id:
            return self.async_abort(reason="invalid_identity")

        await self.async_set_unique_id(user_id)
        if self.source == SOURCE_REAUTH:
            self._abort_if_unique_id_mismatch(reason="wrong_account")
            return self.async_update_reload_and_abort(
                self._get_reauth_entry(),
                data=data,
            )

        self._abort_if_unique_id_configured()
        return self.async_create_entry(
            title="Google Health Sleep",
            data=data,
            options={CONF_DAYS_TO_FETCH: DEFAULT_DAYS_TO_FETCH},
        )

    async def _async_get_identity(self, data: dict[str, Any]) -> dict[str, Any]:
        """Fetch the Google Health identity for unique ID handling."""
        access_token = data["token"]["access_token"]
        session = async_get_clientsession(self.hass)

        async with session.get(
            f"{GOOGLE_HEALTH_API_BASE}/users/me/identity",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            },
        ) as response:
            response.raise_for_status()
            return await response.json()

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        """Create the options flow."""
        return OptionsFlowHandler(config_entry)


async def async_get_options_flow(
    config_entry: config_entries.ConfigEntry,
) -> config_entries.OptionsFlow:
    """Return the options flow."""
    return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle Google Health Sleep options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Manage options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_DAYS_TO_FETCH,
                        default=self._config_entry.options.get(
                            CONF_DAYS_TO_FETCH, DEFAULT_DAYS_TO_FETCH
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=MAX_DAYS_TO_FETCH)),
                }
            ),
        )
