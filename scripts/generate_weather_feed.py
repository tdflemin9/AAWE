import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.request import Request, urlopen


LATITUDE = 42.2808
LONGITUDE = -83.7430
POINTS_URL = f"https://api.weather.gov/points/{LATITUDE},{LONGITUDE}"
USER_AGENT = "ann-arbor-weather-ics-feed/1.0"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "public"
OUTPUT_FILE = OUTPUT_DIR / "weather.ics"


def main():
    weather_data = fetch_weather()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(build_ics(weather_data), encoding="utf-8", newline="")
    write_index(weather_data)
    print(f"Wrote {OUTPUT_FILE}")


def fetch_weather():
    point_data = get_json(POINTS_URL)
    properties = point_data["properties"]
    forecast_data = get_json(properties["forecast"])
    location = properties.get("relativeLocation", {}).get("properties", {})

    return {
        "city": location.get("city", "Ann Arbor"),
        "state": location.get("state", "MI"),
        "office": properties.get("cwa", "NWS"),
        "updated": forecast_data["properties"].get("updated"),
        "periods": forecast_data["properties"]["periods"],
    }


def get_json(url):
    request = Request(
        url,
        headers={
            "Accept": "application/geo+json",
            "User-Agent": USER_AGENT,
        },
    )
    with urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def build_ics(weather_data):
    location = f"{weather_data.get('city', 'Ann Arbor')}, {weather_data.get('state', 'MI')}"
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Ann Arbor Weather Feed//NOAA Forecast//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:Ann Arbor NOAA Weather",
        "X-WR-CALDESC:Hourly refreshed NOAA/NWS forecast for Ann Arbor, Michigan",
    ]

    for period in weather_data.get("periods", [])[:28]:
        start = parse_time(period.get("startTime"))
        if not start:
            continue

        event_date = start.date()
        end_date = event_date + timedelta(days=1)
        day_part = period_day_part(period)
        short_forecast = period.get("shortForecast", "No summary available")
        emoji = weather_emoji(short_forecast)
        temperature = period.get("temperature")
        unit = period.get("temperatureUnit", "F")
        wind_speed = period.get("windSpeed", "Unknown")
        wind_direction = period.get("windDirection", "")
        details = period.get("detailedForecast", "No detailed forecast available.")

        summary = f"{emoji} {day_part}: {temperature}\u00b0{unit}, {short_forecast}"
        description = "\n".join(
            [
                f"NOAA forecast for {location}",
                f"Forecast period: {day_part}",
                f"Temperature: {temperature}\u00b0{unit}",
                f"Conditions: {short_forecast}",
                f"Wind: {wind_direction} {wind_speed}".strip(),
                "",
                details,
            ]
        )

        lines.extend(
            [
                "BEGIN:VEVENT",
                f"UID:ann-arbor-weather-{ics_date(event_date)}-{day_part.lower()}@github-pages-feed",
                f"DTSTAMP:{ics_datetime(datetime.now(timezone.utc))}",
                f"DTSTART;VALUE=DATE:{ics_date(event_date)}",
                f"DTEND;VALUE=DATE:{ics_date(end_date)}",
                f"SUMMARY:{ics_text(summary)}",
                f"LOCATION:{ics_text(location)}",
                f"DESCRIPTION:{ics_text(description)}",
                "TRANSP:TRANSPARENT",
                "END:VEVENT",
            ]
        )

    lines.append("END:VCALENDAR")
    return fold_ics_lines(lines)


def write_index(weather_data):
    updated = format_display_time(weather_data.get("updated"))
    content = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Ann Arbor NOAA Weather Calendar</title>
</head>
<body>
  <main>
    <h1>Ann Arbor NOAA Weather Calendar</h1>
    <p>Latest NOAA/NWS forecast update: {updated}</p>
    <p><a href="weather.ics">Subscribe to weather.ics</a></p>
  </main>
</body>
</html>
"""
    (OUTPUT_DIR / "index.html").write_text(content, encoding="utf-8")


def parse_time(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def format_display_time(value):
    parsed = parse_time(value)
    if not parsed:
        return value or "Unknown"
    return parsed.strftime("%b %d, %Y %I:%M %p")


def period_day_part(period):
    if period.get("isDaytime") is False:
        return "Night"
    return "Day"


def weather_emoji(short_forecast):
    forecast = short_forecast.lower()
    if any(word in forecast for word in ("thunder", "storm")):
        return "\u26c8\ufe0f"
    if any(word in forecast for word in ("snow", "sleet", "flurr")):
        return "\u2744\ufe0f"
    if any(word in forecast for word in ("rain", "showers", "drizzle")):
        return "\U0001f327\ufe0f"
    if any(word in forecast for word in ("fog", "haze", "smoke")):
        return "\U0001f32b\ufe0f"
    if "wind" in forecast or "breezy" in forecast:
        return "\U0001f4a8"
    if any(word in forecast for word in ("sunny", "clear")):
        return "\u2600\ufe0f"
    if any(word in forecast for word in ("cloud", "overcast")):
        return "\u2601\ufe0f"
    return "\U0001f324\ufe0f"


def ics_date(value):
    return value.strftime("%Y%m%d")


def ics_datetime(value):
    return value.strftime("%Y%m%dT%H%M%SZ")


def ics_text(value):
    return (
        str(value)
        .replace("\\", "\\\\")
        .replace("\n", "\\n")
        .replace(";", "\\;")
        .replace(",", "\\,")
    )


def fold_ics_lines(lines):
    folded = []
    for line in lines:
        while len(line.encode("utf-8")) > 75:
            chunk = line[:74]
            while len(chunk.encode("utf-8")) > 74:
                chunk = chunk[:-1]
            folded.append(chunk)
            line = " " + line[len(chunk):]
        folded.append(line)
    return "\r\n".join(folded) + "\r\n"


if __name__ == "__main__":
    main()
