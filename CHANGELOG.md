# CHANGELOG

## v0.4.3 (2026-07-02)

### Chore

* chore: update homebrew formula to 0.4.2 ([`211c7df`](https://github.com/AlanStefanov/bitbucket-manager/commit/211c7df13c24b9025f62d8f629e6bf78054dedcb))

### Fix

* fix: include styles.tcss in PyPI package via package-data

The .tcss file was missing from the published wheel because
setuptools only includes Python files by default. Added
[tool.setuptools.package-data] to include styles.tcss and
py.typed in the distribution.

Fixes StylesheetError on app startup after pipx install. ([`cbea507`](https://github.com/AlanStefanov/bitbucket-manager/commit/cbea5073e910c632d330b3db1b7f39161a1fd8cd))

## v0.4.2 (2026-07-01)

### Chore

* chore: bump to 0.4.2 ([`59736cf`](https://github.com/AlanStefanov/bitbucket-manager/commit/59736cf4101fbd05e32f95985eaf3cefb77833f0))

### Ci

* ci: add semantic-release auto-tagging on main push ([`8cc11d6`](https://github.com/AlanStefanov/bitbucket-manager/commit/8cc11d6f0a41744d301afeafdef07590d0167cbb))

### Documentation

* docs: remove opencode reference, add website and LinkedIn ([`c8f7dd8`](https://github.com/AlanStefanov/bitbucket-manager/commit/c8f7dd8ad5b8eecf75da50f50b92a09c74c6d893))

## v0.4.1 (2026-07-01)

### Chore

* chore: ignore local docs/ folder ([`b9873e2`](https://github.com/AlanStefanov/bitbucket-manager/commit/b9873e212c0d8027d73c4efba13b6941ce840f49))

### Documentation

* docs: update feature status, bump version to 0.4.1, add FAQ

- Feature table refleja estado real: todo listo salvo auto-aprobación masiva
- Versión bump 0.1.0 → 0.4.1
- FAQ.md (EN) + FAQ-es.md (ES)
- Version badge actualizado ([`1b65d37`](https://github.com/AlanStefanov/bitbucket-manager/commit/1b65d37d1a419f4cb4b098cea730381e5df4d55a))

* docs: rewrite README with vision, roadmap, TUI stack, keybindings, and auto-release plan ([`dcd81e8`](https://github.com/AlanStefanov/bitbucket-manager/commit/dcd81e8fb4a86dc7b4a1a3aa62d00a7239d2c21f))

* docs: improve .env.example structure, add FAQ section to README ([`d114b9e`](https://github.com/AlanStefanov/bitbucket-manager/commit/d114b9ec1eb5af852a15009e5c86a09278d18669))

### Feature

* feat: rebrand completo a bitbucket-manager + gestión de grupos y miembros

Rebranding completo de bbm/BRM a bitbucket-manager/Bitbucket Manager. Nuevas features: gestión de grupos y miembros del workspace. DEV_DIR configurable en setup inicial. ([`0c7abd3`](https://github.com/AlanStefanov/bitbucket-manager/commit/0c7abd3a059c193341fc68cfc19d81dedd0ce620))

* feat: implement US2-US5 (pr, migrate, archive, deps)

US2 — PR Approvals: auto-approve via YAML rules, dry-run, rules list, PR check
US3 — Migrations: plan/run/status, git mirror clone+push, migration DB, rollback support
US4 — Archiving: scan by rules or days, archive/restore/list, preserve config snapshot, ARCHIVED project
US5 — Dependency Analysis: scan repo deps by local source, dependency tree, orphans, cycle detection, impact report

Add api.py: get_pullrequests, approve/unapprove, get_branches, create/update repo,
  get/upsert workspace projects
Add pyyaml dependency ([`0fef0db`](https://github.com/AlanStefanov/bitbucket-manager/commit/0fef0db11af75f3fa9eb0d4fcb0b6807e2409af2))

* feat: refactor to package, add permissions CLI, Dockerfile, publish.sh

- Refactor monolithic repository_manager.py into modular src/bbm/ package
- Add pyproject.toml with bbm CLI entry point
- Implement US1: bulk permissions (list/grant/revoke/copy/sync) with --dry-run
- Add Dockerfile for containerized usage
- Add publish.sh for PyPI/Docker Hub/Homebrew publishing
- Create story-006-publish.md (local only)
- Update run.sh to use new package via PYTHONPATH
- Update README with install methods, CLI docs, and new project structure
- Fix .env loading to always source (not just when BB_TOKEN is missing)
- Rename USERNAME→BB_WORKSPACE, add validation for all required vars ([`fe445ff`](https://github.com/AlanStefanov/bitbucket-manager/commit/fe445ff83f0038987e25ae3ae3da497ed343e4f7))

* feat: add interactive config screen and PyPI/Homebrew setup ([`b93b998`](https://github.com/AlanStefanov/bitbucket-manager/commit/b93b9984147228e497094a9d8120bd0f3e0efd7d))

* feat: add author signature header to README ([`01bff9c`](https://github.com/AlanStefanov/bitbucket-manager/commit/01bff9cf601d093404a7fccdfe52949ccd2c0fbd))

* feat: add signature template, make config OS-agnostic via env vars ([`4b09b06`](https://github.com/AlanStefanov/bitbucket-manager/commit/4b09b06ac80a7c263d65a19aeaf7694be55ad515))

### Fix

* fix: remove invalid Textual classifier from pyproject.toml ([`a769c53`](https://github.com/AlanStefanov/bitbucket-manager/commit/a769c53af089528a136bdee6f7b4691b15738666))

* fix: replace print() with curses calls in TUI, silence API stdout during curses

- Replace print() calls inside curses.wrapper with stdscr.addstr()
- Add _silent_stdout() context manager to suppress API print() during TUI
- Show splash screen while loading, error screen with key prompt on failure ([`87b9f3b`](https://github.com/AlanStefanov/bitbucket-manager/commit/87b9f3ba803a786b8e1656ace06bd7ed783f55bb))

* fix: add Bearer auth support for Atlassian API Tokens, update docs

- Add _BearerAuth class for API Tokens from id.atlassian.com (Bearer auth)
- Keep Basic auth fallback when BB_USERNAME is set (app passwords)
- Auto-detect auth type: Bearer if only BB_TOKEN, Basic if BB_TOKEN+BB_USERNAME
- Update get_auth() to return auth_type as 4th value
- Fix all unpacking in feature modules (_, _, workspace, _ = get_auth())
- README: correct token creation URL, add alcances table, API Token vs App Password
- .env.example: update comment with correct URL and 1-year expiry note ([`ae58fec`](https://github.com/AlanStefanov/bitbucket-manager/commit/ae58fece99243f27de014b0ba767b63952181c03))

* fix: load .env always, validate all required vars, rename USERNAME→BB_WORKSPACE ([`3c79452`](https://github.com/AlanStefanov/bitbucket-manager/commit/3c7945248cda3f284b13246561085144aca6c446))

### Unknown

* Merge pull request #3 from AlanStefanov/improvement/config-screen

feat: interactive config screen + PyPI/Homebrew setup ([`25231a6`](https://github.com/AlanStefanov/bitbucket-manager/commit/25231a683b4bf81b596563b71f0ee8f14f53d852))

* Merge remote main into improvement/config-screen ([`9bcc135`](https://github.com/AlanStefanov/bitbucket-manager/commit/9bcc135414747c211131f2a63b398fe9ea37671a))

* Improve repository and pull request data retrieval

Update API to fetch repositories with &#39;member&#39; role and handle 403 errors for pull requests, providing specific guidance on token scopes.

Replit-Commit-Author: Agent
Replit-Commit-Session-Id: b238a020-68d6-4de8-8837-cb3790d7f2b4
Replit-Commit-Checkpoint-Type: full_checkpoint
Replit-Commit-Event-Id: 7261c8ce-18b3-4179-9ca2-d399366e49a5
Replit-Commit-Screenshot-Url: https://storage.googleapis.com/screenshot-production-us-central1/099cd1ac-b034-4f27-9a66-42e370fa60cc/b238a020-68d6-4de8-8837-cb3790d7f2b4/hLfvgub
Replit-Helium-Checkpoint-Created: true ([`1569f98`](https://github.com/AlanStefanov/bitbucket-manager/commit/1569f98584aa780f4591de18c79fea607070b51d))

* Improve dashboard accuracy and add repository management features

Address issues with incorrect dashboard data (activity and stale counts), implement &#39;b&#39; key navigation across screens, enhance PR fetching by distinguishing errors from empty results, refine user permission retrieval, add &#39;Pull&#39; and &#39;Checkout&#39; functionality to repository explorer, improve mouse selection in feature cards, and provide detailed explanations for dependency analysis. Includes bug fixes for date parsing with timezones and filtering git branch outputs.

Replit-Commit-Author: Agent
Replit-Commit-Session-Id: b238a020-68d6-4de8-8837-cb3790d7f2b4
Replit-Commit-Checkpoint-Type: full_checkpoint
Replit-Commit-Event-Id: 10b1a15f-a2f6-4b38-8329-f590536db51b
Replit-Commit-Screenshot-Url: https://storage.googleapis.com/screenshot-production-us-central1/099cd1ac-b034-4f27-9a66-42e370fa60cc/b238a020-68d6-4de8-8837-cb3790d7f2b4/hLfvgub
Replit-Helium-Checkpoint-Created: true ([`029f756`](https://github.com/AlanStefanov/bitbucket-manager/commit/029f7562b42aaf662068200110e3bd93957207df))

* Fix layout issues by adjusting container height

Update ScrollableContainer style from height: 1fr to height: auto in src/bbm/tui/styles.tcss to resolve rendering problems.

Replit-Commit-Author: Agent
Replit-Commit-Session-Id: b238a020-68d6-4de8-8837-cb3790d7f2b4
Replit-Commit-Checkpoint-Type: full_checkpoint
Replit-Commit-Event-Id: a0f2b0c0-c526-4631-9c7a-e33f4415335c
Replit-Commit-Screenshot-Url: https://storage.googleapis.com/screenshot-production-us-central1/099cd1ac-b034-4f27-9a66-42e370fa60cc/b238a020-68d6-4de8-8837-cb3790d7f2b4/hLfvgub
Replit-Helium-Checkpoint-Created: true ([`3fdc99a`](https://github.com/AlanStefanov/bitbucket-manager/commit/3fdc99a7e63e7d69e5ef4e1946cc35a5c216c62e))

* Fix layout issues that prevent content from displaying correctly

Update CSS rules to resolve rendering problems and ensure all content is visible.

Replit-Commit-Author: Agent
Replit-Commit-Session-Id: b238a020-68d6-4de8-8837-cb3790d7f2b4
Replit-Commit-Checkpoint-Type: full_checkpoint
Replit-Commit-Event-Id: 143a6066-b046-4a96-a87f-f70613517d8e
Replit-Commit-Screenshot-Url: https://storage.googleapis.com/screenshot-production-us-central1/099cd1ac-b034-4f27-9a66-42e370fa60cc/b238a020-68d6-4de8-8837-cb3790d7f2b4/hLfvgub
Replit-Helium-Checkpoint-Created: true ([`6864938`](https://github.com/AlanStefanov/bitbucket-manager/commit/6864938a6331b4f9d36e5ac12cc1f92ff293fb29))

* Fix screen layout to correctly display all content

Adjusted home screen layout to use VerticalScroll and modify CSS to ensure all content is visible and the footer is docked correctly.

Replit-Commit-Author: Agent
Replit-Commit-Session-Id: b238a020-68d6-4de8-8837-cb3790d7f2b4
Replit-Commit-Checkpoint-Type: full_checkpoint
Replit-Commit-Event-Id: 8c7321a1-5d79-433f-9a45-06f1be0e696f
Replit-Commit-Screenshot-Url: https://storage.googleapis.com/screenshot-production-us-central1/099cd1ac-b034-4f27-9a66-42e370fa60cc/b238a020-68d6-4de8-8837-cb3790d7f2b4/hLfvgub
Replit-Helium-Checkpoint-Created: true ([`b098b93`](https://github.com/AlanStefanov/bitbucket-manager/commit/b098b9379465a1f800c02f45cd1cd6cecb06585c))

* Update keyboard shortcuts to be more accessible and user-friendly

Replaces F1-F7 shortcuts with letter keys, adds Spacebar for opening selections, and clarifies metric labels in the dashboard.

Replit-Commit-Author: Agent
Replit-Commit-Session-Id: b238a020-68d6-4de8-8837-cb3790d7f2b4
Replit-Commit-Checkpoint-Type: full_checkpoint
Replit-Commit-Event-Id: b287d5a4-a375-4a6a-817c-4659efa00702
Replit-Commit-Screenshot-Url: https://storage.googleapis.com/screenshot-production-us-central1/099cd1ac-b034-4f27-9a66-42e370fa60cc/b238a020-68d6-4de8-8837-cb3790d7f2b4/hLfvgub
Replit-Helium-Checkpoint-Created: true ([`0221abd`](https://github.com/AlanStefanov/bitbucket-manager/commit/0221abd6cd7e0dcf847c231c3ef333202b62fe53))

* Update application with new dashboard and improved navigation

Introduce a new dashboard screen for workspace metrics and refine TUI keybindings and navigation across all screens.

Replit-Commit-Author: Agent
Replit-Commit-Session-Id: b238a020-68d6-4de8-8837-cb3790d7f2b4
Replit-Commit-Checkpoint-Type: full_checkpoint
Replit-Commit-Event-Id: e5b2c2cf-b5c1-4d80-9215-5d0998923f00
Replit-Commit-Screenshot-Url: https://storage.googleapis.com/screenshot-production-us-central1/099cd1ac-b034-4f27-9a66-42e370fa60cc/b238a020-68d6-4de8-8837-cb3790d7f2b4/hLfvgub
Replit-Helium-Checkpoint-Created: true ([`01d58ef`](https://github.com/AlanStefanov/bitbucket-manager/commit/01d58efc5536873432760961f6f62fdb3392f967))

* Remove web serving and make the application a pure terminal app

Remove `serve.py`, `textual-serve` dependency from `pyproject.toml`, and update `replit.md` to reflect the change to a pure TUI application.

Replit-Commit-Author: Agent
Replit-Commit-Session-Id: b238a020-68d6-4de8-8837-cb3790d7f2b4
Replit-Commit-Checkpoint-Type: full_checkpoint
Replit-Commit-Event-Id: 7e20b8e3-b0e0-4043-ae3d-a1396729acad
Replit-Commit-Screenshot-Url: https://storage.googleapis.com/screenshot-production-us-central1/099cd1ac-b034-4f27-9a66-42e370fa60cc/b238a020-68d6-4de8-8837-cb3790d7f2b4/hLfvgub
Replit-Helium-Checkpoint-Created: true ([`2b21c9a`](https://github.com/AlanStefanov/bitbucket-manager/commit/2b21c9a42e767d75a5b42d9525501668496088f8))

* Update project configuration and add web serving for the terminal application

Fixes pyproject.toml build backend and Python version requirements, adds textual-serve dependency, and introduces serve.py to enable web deployment of the Textual TUI. Includes replit.md documentation.

Replit-Commit-Author: Agent
Replit-Commit-Session-Id: b238a020-68d6-4de8-8837-cb3790d7f2b4
Replit-Commit-Checkpoint-Type: full_checkpoint
Replit-Commit-Event-Id: f8c02676-af61-49db-84bb-d267809d1701
Replit-Commit-Screenshot-Url: https://storage.googleapis.com/screenshot-production-us-central1/099cd1ac-b034-4f27-9a66-42e370fa60cc/b238a020-68d6-4de8-8837-cb3790d7f2b4/hLfvgub
Replit-Helium-Checkpoint-Created: true ([`9e76d9e`](https://github.com/AlanStefanov/bitbucket-manager/commit/9e76d9eb218f56e23b462a920e3f1ae0cbe79437))

* change ui ([`84c0a45`](https://github.com/AlanStefanov/bitbucket-manager/commit/84c0a453bc6c682feeb221e0f7d208cd1b5db3ea))

* Add website badge: astefanov.com ([`a930642`](https://github.com/AlanStefanov/bitbucket-manager/commit/a930642522806538c6f5ce0716c21758092d71ac))

* Add CI workflow

Add CI workflow ([`ff15661`](https://github.com/AlanStefanov/bitbucket-manager/commit/ff15661f9215c95cc4a63115b6553cb0d1f6810e))

* Add CI workflow ([`b098786`](https://github.com/AlanStefanov/bitbucket-manager/commit/b0987867da816fda6b83c819f79c4759c6e2eba1))

* Merge pull request #1 from AlanStefanov/feature/add-signature-template

Mejoras: firma, config por env vars, requisitos multi-OS ([`cf7a147`](https://github.com/AlanStefanov/bitbucket-manager/commit/cf7a14753c46717c991b42947710887fc448ac85))

* Improve README with .env setup instructions ([`7020784`](https://github.com/AlanStefanov/bitbucket-manager/commit/7020784cd48dd5f0a15854251b20b40b6ecf64eb))

* Initial commit ([`432cb9e`](https://github.com/AlanStefanov/bitbucket-manager/commit/432cb9e9fede37a59f1fc01d51f14ff32038a550))
