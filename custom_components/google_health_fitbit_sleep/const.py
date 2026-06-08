"""Constants for the Google Health Sleep integration."""

from datetime import timedelta

DOMAIN = "google_health_fitbit_sleep"

OAUTH2_AUTHORIZE = "https://accounts.google.com/o/oauth2/v2/auth"
OAUTH2_TOKEN = "https://oauth2.googleapis.com/token"
GOOGLE_HEALTH_API_BASE = "https://health.googleapis.com/v4"
OAUTH2_SCOPES = [
    "https://www.googleapis.com/auth/googlehealth.sleep.readonly",
    "https://www.googleapis.com/auth/googlehealth.profile.readonly",
]

CONF_DAYS_TO_FETCH = "days_to_fetch"
DEFAULT_DAYS_TO_FETCH = 7
MAX_DAYS_TO_FETCH = 30

SCAN_INTERVAL = timedelta(hours=6)
