# 40th Century Grain Markets

A small installable web app for planning 40th Century Grain's markets, pop-ups and holiday ads.

## Using it
- **Install on iPhone:** open the site in Safari → Share → Add to Home Screen.
- **Apple Calendar:** tap "Subscribe in Apple Calendar" once. The subscription refreshes on its own, so changes here show up on your phone.
- **One event at a time:** each upcoming event has an "Add to Calendar" button.
- **Checklist:** saved on each phone separately.

## Changing events
1. Edit `events.json` (each event has `id`, `title`, `date` as YYYY-MM-DD, optional `start`/`end` as HH:MM, `type` = market / ad / task, `status` = planned / confirm / done, `location`, `cost`, `notes`).
2. Run `python3 build.py` to regenerate `events.ics` and the per-event files in `events/`.
3. Commit and push. GitHub Pages updates in a minute or two.
