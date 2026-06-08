# Google Health Sleep for Home Assistant

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz/)

A Home Assistant custom integration that syncs sleep data from the Google Health API into Home Assistant sensors. It is intended for Fitbit/Google wearable sleep data exposed through Google Health, avoiding the deprecated Fitbit Web API.

## Disclaimer

This is an unofficial project and is not affiliated with, endorsed by, sponsored by, or associated with Google, Google Health, Fitbit, or Home Assistant.

## Installation with HACS

1. Open HACS in Home Assistant.
2. Go to **Integrations**.
3. Open the three-dot menu and choose **Custom repositories**.
4. Add this repository URL:

   ```text
   https://github.com/esotericzhang/GoogleHealthHomeAssistant
   ```

5. Select category **Integration**.
6. Download **Google Health Sleep**.
7. Restart Home Assistant.

## Manual Installation

Copy:

```text
custom_components/google_health_fitbit_sleep
```

to:

```text
config/custom_components/google_health_fitbit_sleep
```

Then restart Home Assistant.

## Google Cloud Setup

1. Enable the **Google Health API** in Google Cloud.
2. Create an OAuth 2.0 client ID and secret.
3. Add this authorized redirect URI to the OAuth client:

   ```text
   https://my.home-assistant.io/redirect/oauth
   ```

   Use this even when Home Assistant is hosted only on your local network.
4. In Home Assistant, go to **Settings → Devices & services → Application Credentials** and add the Google OAuth client ID and secret.
5. Add the **Google Health Sleep** integration from **Settings → Devices & services → Add Integration**.

## Sensors

- Latest minutes asleep
- Latest minutes awake
- Latest sleep period
- Latest sleep efficiency
- Latest deep sleep
- Latest light sleep
- Latest REM sleep
- Latest sleep start
- Latest sleep end
- Sleep records

The `sleep_records` sensor includes recent normalized sleep records in attributes for dashboards, templates, and plotting.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
