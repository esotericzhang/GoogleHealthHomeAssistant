"""Google Health API client for sleep data."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any

from homeassistant.helpers.config_entry_oauth2_flow import OAuth2Session

from .const import GOOGLE_HEALTH_API_BASE


class GoogleHealthApi:
    """Small Google Health API client."""

    def __init__(self, session: OAuth2Session) -> None:
        """Initialize the API client."""
        self._session = session

    async def async_get_identity(self) -> dict[str, Any]:
        """Fetch the Google Health identity."""
        return await self._get("/users/me/identity")

    async def async_get_sleep_records(self, days: int) -> list[dict[str, Any]]:
        """Fetch reconciled Google wearable sleep records."""
        start = (date.today() - timedelta(days=days)).isoformat()
        params = {
            "dataSourceFamily": "users/me/dataSourceFamilies/google-wearables",
            "filter": f'sleep.interval.civil_end_time >= "{start}"',
        }
        records: list[dict[str, Any]] = []

        while True:
            data = await self._get(
                "/users/me/dataTypes/sleep/dataPoints:reconcile",
                params=params,
            )
            records.extend(data.get("dataPoints", []))
            token = data.get("nextPageToken")
            if not token:
                break
            params["pageToken"] = token

        return sorted(
            (self._normalize_sleep_record(record) for record in records),
            key=lambda record: record.get("end_time") or "",
            reverse=True,
        )

    async def _get(
        self,
        path: str,
        params: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Run an authenticated GET request."""
        response = await self._session.async_request(
            "GET",
            f"{GOOGLE_HEALTH_API_BASE}{path}",
            params=params,
            headers={"Accept": "application/json"},
        )
        response.raise_for_status()
        return await response.json()

    def _normalize_sleep_record(self, record: dict[str, Any]) -> dict[str, Any]:
        sleep = record.get("sleep", {})
        interval = sleep.get("interval", {})
        summary = sleep.get("summary", {})
        stages_summary = {
            item.get("type", "").lower(): self._to_int(item.get("minutes"))
            for item in summary.get("stagesSummary", [])
        }
        minutes_asleep = self._to_int(summary.get("minutesAsleep"))
        minutes_awake = self._to_int(summary.get("minutesAwake"))
        sleep_period = self._to_int(summary.get("minutesInSleepPeriod"))

        return {
            "name": record.get("name"),
            "source_platform": record.get("dataSource", {}).get("platform"),
            "device": record.get("dataSource", {}).get("device", {}).get("displayName"),
            "start_time": interval.get("startTime"),
            "end_time": interval.get("endTime"),
            "minutes_in_sleep_period": sleep_period,
            "minutes_asleep": minutes_asleep,
            "minutes_awake": minutes_awake,
            "minutes_to_fall_asleep": self._to_int(summary.get("minutesToFallAsleep")),
            "minutes_after_wake_up": self._to_int(summary.get("minutesAfterWakeUp")),
            "efficiency": self._efficiency(minutes_asleep, sleep_period),
            "stage_minutes": stages_summary,
            "stage_counts": {
                item.get("type", "").lower(): self._to_int(item.get("count"))
                for item in summary.get("stagesSummary", [])
            },
            "stages": [
                {
                    "start_time": stage.get("startTime"),
                    "end_time": stage.get("endTime"),
                    "type": stage.get("type"),
                    "minutes": self._stage_minutes(stage),
                }
                for stage in sleep.get("stages", [])
            ],
            "processed": sleep.get("metadata", {}).get("processed"),
            "main": sleep.get("metadata", {}).get("main"),
        }

    @staticmethod
    def _to_int(value: Any) -> int | None:
        if value in (None, ""):
            return None
        return int(value)

    @staticmethod
    def _efficiency(minutes_asleep: int | None, sleep_period: int | None) -> float | None:
        if not minutes_asleep or not sleep_period:
            return None
        return round(minutes_asleep / sleep_period * 100, 1)

    @staticmethod
    def _stage_minutes(stage: dict[str, Any]) -> int | None:
        start = stage.get("startTime")
        end = stage.get("endTime")
        if not start or not end:
            return None
        start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
        end_dt = datetime.fromisoformat(end.replace("Z", "+00:00"))
        return int((end_dt - start_dt).total_seconds() / 60)


def utc_now_iso() -> str:
    """Return the current UTC time as an ISO string."""
    return datetime.now(timezone.utc).isoformat()
