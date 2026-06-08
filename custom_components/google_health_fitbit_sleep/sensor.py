"""Sensors for Google Health Sleep."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import GoogleHealthSleepCoordinator


@dataclass(frozen=True, kw_only=True)
class GoogleHealthSleepSensorDescription(SensorEntityDescription):
    """Describe a Google Health sleep sensor."""

    value_fn: Callable[[dict[str, Any], list[dict[str, Any]]], Any]
    attributes_fn: Callable[[dict[str, Any], list[dict[str, Any]]], dict[str, Any]] | None = None


SENSOR_DESCRIPTIONS: tuple[GoogleHealthSleepSensorDescription, ...] = (
    GoogleHealthSleepSensorDescription(
        key="latest_minutes_asleep",
        name="Latest minutes asleep",
        translation_key="latest_minutes_asleep",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda latest, records: latest.get("minutes_asleep"),
    ),
    GoogleHealthSleepSensorDescription(
        key="latest_minutes_awake",
        name="Latest minutes awake",
        translation_key="latest_minutes_awake",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda latest, records: latest.get("minutes_awake"),
    ),
    GoogleHealthSleepSensorDescription(
        key="latest_sleep_period",
        name="Latest sleep period",
        translation_key="latest_sleep_period",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda latest, records: latest.get("minutes_in_sleep_period"),
    ),
    GoogleHealthSleepSensorDescription(
        key="latest_sleep_efficiency",
        name="Latest sleep efficiency",
        translation_key="latest_sleep_efficiency",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda latest, records: latest.get("efficiency"),
    ),
    GoogleHealthSleepSensorDescription(
        key="latest_deep_sleep",
        name="Latest deep sleep",
        translation_key="latest_deep_sleep",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda latest, records: latest.get("stage_minutes", {}).get("deep"),
    ),
    GoogleHealthSleepSensorDescription(
        key="latest_light_sleep",
        name="Latest light sleep",
        translation_key="latest_light_sleep",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda latest, records: latest.get("stage_minutes", {}).get("light"),
    ),
    GoogleHealthSleepSensorDescription(
        key="latest_rem_sleep",
        name="Latest REM sleep",
        translation_key="latest_rem_sleep",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda latest, records: latest.get("stage_minutes", {}).get("rem"),
    ),
    GoogleHealthSleepSensorDescription(
        key="latest_sleep_start",
        name="Latest sleep start",
        translation_key="latest_sleep_start",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda latest, records: _parse_time(latest.get("start_time")),
    ),
    GoogleHealthSleepSensorDescription(
        key="latest_sleep_end",
        name="Latest sleep end",
        translation_key="latest_sleep_end",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda latest, records: _parse_time(latest.get("end_time")),
    ),
    GoogleHealthSleepSensorDescription(
        key="sleep_records",
        name="Sleep records",
        translation_key="sleep_records",
        value_fn=lambda latest, records: len(records),
        attributes_fn=lambda latest, records: {"records": records},
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Google Health sleep sensors."""
    coordinator: GoogleHealthSleepCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        GoogleHealthSleepSensor(coordinator, entry, description)
        for description in SENSOR_DESCRIPTIONS
    )


class GoogleHealthSleepSensor(CoordinatorEntity[GoogleHealthSleepCoordinator], SensorEntity):
    """Google Health sleep sensor."""

    entity_description: GoogleHealthSleepSensorDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: GoogleHealthSleepCoordinator,
        entry: ConfigEntry,
        description: GoogleHealthSleepSensorDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_name = description.name
        self._attr_translation_key = description.translation_key
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._entry = entry

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        latest = self.coordinator.data.get("latest", {}) if self.coordinator.data else {}
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name="Google Health Sleep",
            manufacturer="Google",
            model=latest.get("device") or "Google Health",
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def native_value(self) -> Any:
        """Return the sensor value."""
        if not self.coordinator.data:
            return None
        latest = self.coordinator.data.get("latest", {})
        records = self.coordinator.data.get("records", [])
        return self.entity_description.value_fn(latest, records)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        if not self.coordinator.data:
            return {}
        latest = self.coordinator.data.get("latest", {})
        records = self.coordinator.data.get("records", [])
        attrs = {
            "last_update": self.coordinator.data.get("last_update"),
            "source_platform": latest.get("source_platform"),
            "device": latest.get("device"),
        }
        if self.entity_description.attributes_fn:
            attrs.update(self.entity_description.attributes_fn(latest, records))
        return attrs

    @property
    def available(self) -> bool:
        """Return whether the entity has data."""
        return self.native_value is not None


def _parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))
