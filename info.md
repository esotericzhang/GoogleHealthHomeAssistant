# Google Health Sleep

Google Health Sleep is a Home Assistant custom integration that reads sleep data from the Google Health API and exposes it as sensors.

## Sensors

- Latest minutes asleep
- Latest minutes awake
- Latest sleep period
- Latest sleep efficiency
- Latest deep, light, and REM sleep
- Latest sleep start and end timestamps
- Sleep records count with recent records as attributes

## Setup

1. Enable the Google Health API in Google Cloud.
2. Create OAuth 2.0 credentials.
3. Add the OAuth redirect URI shown by Home Assistant to your Google Cloud OAuth client.
4. Add the credentials in Home Assistant under Application Credentials.
5. Add the Google Health Sleep integration.
