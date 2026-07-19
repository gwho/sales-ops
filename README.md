# Sales Admin Automation Toolkit

Fictional-data Excel automation for order validation, inventory allocation, and payment aging. See `CLAUDE.md` and `context/` for the full project plan.

## Live Demo

- App: <https://sales-ops-gamma.vercel.app/>
- API: <https://sales-ops-6e84.onrender.com>

Try it: open the app, view the Dashboard and Reports pages, then visit any of the three workflow pages (Order Validation, Inventory Allocation, Payment Aging) and click **Run sample data** — no file to find or prepare, it runs the workflow against the same committed fictional dataset shown throughout the demo. Each page also lets you download the resulting Excel report.

**Note:** the backend is hosted on Render's free tier, which sleeps after ~15 minutes of inactivity. The first request after a period of idle time can take up to about a minute while it wakes up — a later request will be fast. This is expected, not a bug.

## Setup

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

## Local development

The frontend and backend are two independent local processes — starting one does
**not** start the other. This is the most common cause of `/dashboard` showing
**Could not reach the API server**: the Next.js dev server is running, but
FastAPI was never started (or was stopped) in its own terminal.

**Terminal 1 — backend (FastAPI, `127.0.0.1:8000`):**

```bash
uv run fastapi dev backend/main.py
```

**Terminal 2 — frontend (Next.js, `localhost:3000`):**

```bash
npm install   # first time only
npm run dev
```

Before opening the app, or whenever you see the "Could not reach the API
server" banner, confirm the backend is actually up:

```bash
curl -fsS --max-time 3 http://127.0.0.1:8000/health
# expected: {"status":"ok"}
```

If that call fails to connect, the backend simply isn't running in a
terminal right now — start it with the command above. `DATABASE_URL` is
optional locally; persistence is cleanly disabled without it (see
`context/architecture.md`'s "Persistence" section), and the rest of the app
works normally either way.

## Running tests

```bash
uv run pytest
```
