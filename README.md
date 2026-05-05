# Ann Arbor NOAA Weather ICS Feed

This folder is a small, standalone GitHub Pages project that publishes an
hourly refreshed `.ics` calendar feed from NOAA/NWS data.

## What It Publishes

- `weather.ics`: the calendar feed to subscribe to.
- `index.html`: a tiny landing page with a link to the feed.
- Forecast events are all-day events.
- Event titles use only `Day` or `Night`, not weekday names.

## Setup

1. Create a new GitHub repository.
2. Copy the contents of this `weather_ics_feed` folder into the repository root.
3. Commit and push the files.
4. In GitHub, go to `Settings > Pages`.
5. Set `Build and deployment` to `GitHub Actions`.
6. Run the `Refresh NOAA Weather ICS Feed` workflow manually once, or wait for the hourly schedule.

After the workflow runs, your feed URL will look like:

```text
https://YOUR-USERNAME.github.io/YOUR-REPO/weather.ics
```

Use that URL when subscribing from Outlook, Google Calendar, Apple Calendar, or
another calendar app that accepts `.ics` subscriptions.

## Notes

- NOAA/NWS does not require an API key for this data.
- The workflow uses Python only; there are no package dependencies.
- GitHub Actions scheduled workflows usually run close to hourly, but GitHub does
  not guarantee exact timing.
