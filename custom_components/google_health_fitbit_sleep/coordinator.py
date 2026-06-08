"""Data update coordinator for Google Health Sleep."""

from __future__ import annotations

from datetime import datetime, timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import GoogleHealthApi
from .const import (
    CONF_DAYS_TO_FETCH,
    CONF_UPDATE_INTERVAL,
    DEFAULT_DAYS_TO_FETCH,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class GoogleHealthSleepCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Manage Google Health sleep updates."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: GoogleHealthApi,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(
                minutes=entry.options.get(
                    CONF_UPDATE_INTERVAL,
                    DEFAULT_UPDATE_INTERVAL,
                )
            ),
        )
        self.api = api
        self.entry = entry

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch Google Health sleep data."""
        try:
            records = await self.api.async_get_sleep_records(
                self.entry.options.get(CONF_DAYS_TO_FETCH, DEFAULT_DAYS_TO_FETCH)
            )
        except Exception as err:
            _LOGGER.warning("Unable to fetch Google Health sleep data: %s", err)
            if self.data:
                return self.data
            raise UpdateFailed(f"Unable to fetch Google Health sleep data: {err}") from err

        latest = records[0] if records else {}
        if not latest and self.data:
            return self.data

        return {
            "latest": latest,
            "records": records,
            "last_update": datetime.now().astimezone().isoformat(),
        }
