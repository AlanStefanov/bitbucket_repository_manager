# Session: 2026-06-28 — TUI Rewrite (curses → Textual)

## What we did
- Replaced curses TUI with **Textual 8.x** framework
- Created 6 feature screens: Explorer, Permissions, PR, Migration, Archive, Deps
- Home screen with 6 responsive cards, keyboard nav (↑↓←→ + Enter)
- Animated boot splash with step indicators
- Removed all CLI code (cli.py, permissions.py, pr_approval.py, migration.py, archiving.py, deps.py)
- Entry point: `bbm = bbm.tui:run_tui`
- Dependencies: textual, rich, requests, pyyaml
- Rewrote README.md with vision, roadmap (US1-US6), keybindings, stack
- All 6 screens verified working with Textual test probe

## Key decisions
- Pure TUI, no CLI subcommands
- Dark theme `#10b981` accent
- Auth: Basic (email + API Token from id.atlassian.com)
- Permissions/Migration/Archive use sidebar layout; Explorer/PR/Deps use full-width + docked action bar

## Keyboard
- Home: ↑↓←→ + Enter to open, Escape/Q to quit
- Feature screens: Escape → Home, Ctrl+Q/Q → quit

## Files
`src/bbm/tui/` — all screens + styles.tcss + widgets.py
`run.sh` — `PYTHONPATH=src exec python3 -m bbm`
`.env` — working credentials (39 repos from `farmu`)
