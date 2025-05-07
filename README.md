# Pi‑hole DHCP Presence

**Version:** 0.2.1
**Domain:** `pihole_dhcp`
**IoT Class:** local\_polling

A Home Assistant custom integration that leverages Pi‑hole’s DHCP and network endpoints to monitor device presence and diagnostics. It unifies Pi‑hole data with your existing HA devices by matching on MAC address, exposing detailed sensors and a device tracker for each client.

---

## Table of Contents

1. [Features](#features)
2. [Screenshots](#screenshots)
3. [Installation](#installation)

   * [HACS](#hacs)
   * [Manual](#manual)
4. [Configuration](#configuration)
5. [Entities](#entities)

   * [Sensors](#sensors)
   * [Device Tracker](#device-tracker)
6. [Usage Examples](#usage-examples)
7. [Advanced Topics](#advanced-topics)

   * [Automations & Alerts](#automations--alerts)
   * [Customizing Entity Names & Icons](#customizing-entity-names--icons)
8. [Troubleshooting](#troubleshooting)
9. [Development](#development)
10. [Contributing](#contributing)
11. [License](#license)

---

** Settings -> System -> 'Flush Network Table' before install is recommended to avoid importing stale devices into your HA instance **

## Features

* 🔎 **Unified Device Registry**
  Merges Pi‑hole DHCP data with existing HA devices based on MAC address (`connections`). No duplicate `eth0` entries.

* 📊 **Diagnostic Sensors**
  Exposes:

  * *First Seen* (ISO 8601 timestamp)
  * *Last Query (seconds ago)*
  * *Query Count* (cumulative, `total_increasing`)
  * *IP Addresses* (comma‑separated list)
  * *Lease Expires (hours remaining)*
  * *MAC Vendor* (diagnostic)
  * *Device Name* (diagnostic)

* 🚶‍♂️ **Presence Tracking**
  Implements a `device_tracker` named *Presence via Pi‑hole* with `_pihole` suffix. Marks devices away if no DNS query within *Consider Away* threshold.

* ⚙️ **UI Config Flow**
  Configure Pi‑hole host, polling interval, and away timeout entirely in HA UI. No YAML required.

* ⚡ **Efficient Polling**
  Fetches only two endpoints (`/api/dhcp/leases`, `/api/network/devices`) at configurable intervals. Lightweight and non‑blocking.

## Screenshots

## Installation

### HACS

1. Ensure HACS is installed.
2. In GitHub, add this repository as a custom integration:

   * **URL:** `https://github.com/lrehmann/pihole_dhcp`
3. In Home Assistant, navigate to **HACS → Integrations → + → Explore & Add Repositories**, search for **Pi‑hole DHCP Presence**, and install.
4. Restart Home Assistant.

### Manual

1. Clone or download this repo.
2. Copy the `custom_components/pihole_dhcp/` folder into `<config>/custom_components/`.
3. Restart Home Assistant.

## Configuration

After restart, go to **Settings → Devices & Services → + Add Integration** and search **Pi‑hole DHCP Presence**.

| Option                 | Description                                     | Default          |
| ---------------------- | ----------------------------------------------- | ---------------- |
| **Host/IP**            | Pi‑hole API base URL (`http://pi.hole` or IP)   | `http://pi.hole` |
| **Poll Frequency (s)** | Seconds between API polls (min 5 s)             | `30`             |
| **Consider Away (s)**  | Seconds without DNS query to mark device *away* | `900`            |

Click **Submit**. The integration will appear under **Settings → Devices & Services**.

---

## Entities

### Sensors

All sensors are **Diagnostic**. They will not record to the logbook.

| Entity ID Pattern                      | Friendly Name      | Unit            | State Class        |
| -------------------------------------- | ------------------ | --------------- | ------------------ |
| `sensor.<mac>_firstseen`               | First Seen         | ISO 8601 string | —                  |
| `sensor.<mac>_lastquery`               | Last Query (s ago) | seconds         | `measurement`      |
| `sensor.<mac>_querycount`              | Query Count        | queries         | `total_increasing` |
| `sensor.<mac>_ipaddresses`             | IP Addresses       | —               | —                  |
| `sensor.<mac>_leaseexpires`            | Lease Expires (h)  | hours           | —                  |
| `sensor.<mac>_macvendor` (diagnostic)  | MAC Vendor         | —               | —                  |
| `sensor.<mac>_devicename` (diagnostic) | Device Name        | —               | —                  |

### Device Tracker

| Entity ID Pattern             | Friendly Name        | Description                                         |
| ----------------------------- | -------------------- | --------------------------------------------------- |
| `device_tracker.<mac>_pihole` | Presence via Pi‑hole | *On* if last query ≤ away timeout; otherwise *Off*. |

Under **Settings → Devices & Services → Devices**, each MAC will now have:

* 7 *Diagnostic* sensors
* 1 *device\_tracker* entry

---

## Usage Examples

### Lovelace Card: Presence & Stats

```yaml
type: entities
entities:
  - entity: device_tracker.abcdef123456_pihole
    name: My Phone (Pi‑hole)
  - entity: sensor.abcdef123456_querycount
    name: Total Queries
  - entity: sensor.abcdef123456_lastquery
    name: Last DNS Query
  - entity: sensor.abcdef123456_leaseexpires
    name: Hours till Lease Expiry
```

### Automation: Notify on Absence

```yaml
alias: "Notify when My Phone Away"
trigger:
  - platform: state
    entity_id: device_tracker.abcdef123456_pihole
    to: 'not_home'
action:
  - service: notify.mobile_app
    data:
      message: "Your phone hasn't queried Pi‑hole in 30 min!"
```

— adapt `entity_id` and thresholds as needed.

---

## Advanced Topics

### Automations & Alerts

* Use `sensor.<mac>_querycount`’s `total_increasing` for long‑term traffic graphs.
* Link *Lease Expires* sensors to trigger binary sensors when < X h.

### Customizing Entity Names & Icons

Add in `customize.yaml`:

```yaml
sensor.abcdef123456_querycount:
  icon: mdi:dns
```

Or set friendly names via **Settings → Entities** for clearer labels.

---

## Troubleshooting

* **No entities created**: Check Pi‑hole API base URL and network connectivity.
* **Duplicate devices**: Ensure other integrations don’t use `connections`; clear old device registry entries if needed.
* **Presence always Unknown**: Verify `Consider Away (s)` and HA time sync (`NTP`).

Logs: Look for `pihole_dhcp` entries under **Supervisor → System → Logs**.

---

## Development

1. Fork the repo
2. Clone locally and install dev dependencies:

   ```bash
   poetry install  # or pip install -r requirements.txt
   ```
3. Link your dev folder:

   ```bash
   ln -s $(pwd)/custom_components/pihole_dhcp <config>/custom_components/
   ```
4. Restart HA and develop.
5. Write tests under `tests/` (pytest with `pytest-homeassistant-custom-component`).

---

## Contributing

Pull requests welcome!
Please follow these steps:

1. Open an issue describing your feature or bug.
2. Create a branch: `git checkout -b feature/my-feature`.
3. Commit changes and add tests.
4. Push & open a PR.

---

## License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.
