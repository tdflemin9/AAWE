import unittest

from scripts.generate_weather_feed import build_ics


class BuildIcsTests(unittest.TestCase):
    def test_summary_places_temperature_before_emoji(self):
        feed = build_ics(
            {
                "city": "Ann Arbor",
                "state": "MI",
                "periods": [
                    {
                        "startTime": "2026-05-05T06:00:00-04:00",
                        "isDaytime": True,
                        "shortForecast": "Chance Rain Showers",
                        "temperature": 57,
                        "temperatureUnit": "F",
                        "windSpeed": "12 mph",
                        "windDirection": "WNW",
                        "detailedForecast": "A chance of rain showers.",
                    }
                ],
            }
        )

        self.assertIn("SUMMARY:57°F 🌧️ Day: Chance Rain Showers", feed)
        self.assertNotIn("SUMMARY:🌧️ Day: Chance Rain Showers\\, 57°F", feed)


if __name__ == "__main__":
    unittest.main()
