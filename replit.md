# Bitbucket Manager

## Overview
`bitbucket-manager` is a terminal user interface (TUI) for managing Bitbucket Cloud,
built with the [Textual](https://textual.textualize.io/) framework. It offers screens
for workspace dashboard, repository exploration, group and member management, mass permission management,
PR auto-approval, project migration, smart archiving, and dependency analysis.

This is a **pure TUI application** that runs directly in the terminal (Shell).
No server, no web serving, no preview pane. Test it from the Shell tab.

## Architecture
- **Language:** Python 3.11
- **TUI framework:** Textual 8.x (`src/bitbucket_manager/tui/`)
- **HTTP/API:** `requests` (Bitbucket Cloud REST API v2.0)
- **Package layout:** `src/bitbucket_manager/` (src-layout, configured in `pyproject.toml`)
- **Entry point:** `python -m bitbucket_manager` or `./run.sh`

## Replit Setup
- **No workflow** — this is a terminal app, not a web server.
- Run it from the **Shell** tab: `./run.sh`
- `run.sh` sets `PYTHONPATH=src` and sources `.env` if present.

## Configuration
The app reads Bitbucket credentials from environment variables (or a `.env` file at the
repo root). These are only needed for live Bitbucket operations; the app boots and renders
without them.

| Variable | Description |
|----------|-------------|
| `BB_TOKEN` | Bitbucket API token (id.atlassian.com) |
| `BB_USERNAME` | Atlassian account email |
| `BB_WORKSPACE` | Bitbucket workspace slug |
| `DEV_DIR` | Optional clone directory |

See `.env.example` for the full template.

## User Preferences
(none recorded yet)
