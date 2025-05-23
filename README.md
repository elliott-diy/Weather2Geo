

# Weather2Geo

## Overview

**Weather2Geo** is a focused OSINT tool that turns weather widget leaks into geolocation data.

People post screenshots with the Windows weather widget in their taskbar all the time, showing the exact temperature, weather condition, and local time. This tool uses the same API as the widget to find cities where those conditions are currently true.

It’s built for one job:

> Find out roughly where someone is based on a single corner of their screen.


> ⚠️ This tool works best if used shortly after the screenshot is posted — conditions change fast.

---

## Features

* 🌍 **Geolocation from Widgets**: Match weather condition, temp, and time to a list of real cities.
* 🕒 **Timezone-Aware**: Localizes your input to each city’s timezone to compare properly.
* 🗺️ **Clustering**: Groups nearby hits so you don’t get overwhelmed by noise.
* 🧪 **Extensible**: Tweak tolerance, data sources, and distance for your use case.

---

## Installation

```bash
git clone https://github.com/elliott-diy/Weather2Geo
cd Weather2Geo
pip install -r requirements.txt
```

---

## Usage

```bash
python main.py run \
  --time "2025-05-22 14:00" \
  --condition "Mostly cloudy" \
  --temp 18 \
  --tolerance 1.0
```

### Options

| Flag                 | Description                                               |
| -------------------- | --------------------------------------------------------- |
| `--time`             | Local time shown in the screenshot (`YYYY-MM-DD HH:MM`)   |
| `--condition`        | Weather condition string (e.g., "Partly cloudy")          |
| `--temp`             | Temperature in Celsius                                    |
| `--tolerance`        | Temp wiggle room (default: 1.0°C)                         |
| `--cluster-distance` | Max distance in KM to group hits (default: 15)            |
| `--cities-file`      | Path to GeoNames cities file (default: `cities15000.txt`) |

---

## Example Use Case

You spot a screenshot that says:

```
Mostly clear | 13°C | 10:09 PM | May 22
```

Run:

```bash
python main.py run \
  --time "2025-05-22 22:09" \
  --condition "Mostly clear" \
  --temp 13
```

And you’ll get clusters of cities like:

```
Cluster 1 – 10 locations:
- US Seattle — 13°C, mostly clear
- US Bellevue — 13°C, mostly clear
...
```

---

## Data Sources

* **City List**: [GeoNames `cities15000.txt`](https://download.geonames.org/export/dump/)
* **Weather**: [MSN Weather API](https://www.msn.com/en-ca/weather) - same backend as the Windows widget

---

## Disclaimer

This tool is for ethical, educational OSINT use only. Don’t be a creep, respect privacy and legal boundaries.



