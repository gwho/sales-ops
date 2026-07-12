# Sales Admin Automation Toolkit

Fictional-data Excel automation for order validation, inventory allocation, and payment aging. See `CLAUDE.md` and `context/` for the full project plan.

## Live Demo

- App: `<TODO: fill in the Vercel production URL after deployment>`
- API: `<TODO: fill in the Render production URL after deployment>`

Try it: open the app, view the Dashboard and Reports pages, then visit any of the three workflow pages (Order Validation, Inventory Allocation, Payment Aging) and click **Run sample data** — no file to find or prepare, it runs the workflow against the same committed fictional dataset shown throughout the demo. Each page also lets you download the resulting Excel report.

**Note:** the backend is hosted on Render's free tier, which sleeps after ~15 minutes of inactivity. The first request after a period of idle time can take up to about a minute while it wakes up — a later request will be fast. This is expected, not a bug.

## Setup

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

## Running tests

```bash
uv run pytest
```
