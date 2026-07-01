from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Static

from bitbucket_manager.api import get_repos, get_pullrequests
from bitbucket_manager.config import get_auth


class DashboardScreen(Screen):
    """Pantalla resumen para devs y líderes técnicos.

    Nota: para workspaces con >50 repos, el dashboard escanea los primeros 50
    para evitar saturar la API de Bitbucket. Los conteos se muestran como
    'en repos escaneados' para ser honestos con el usuario.
    """

    BINDINGS = [
        ("h", "go_home", "Home"),
        ("b", "go_home", "Home"),
        ("escape", "go_home", "Home"),
        ("ctrl+q", "quit_app", "Salir"),
        ("r", "refresh", "Refrescar"),
        ("ctrl+r", "refresh", "Refrescar"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._repos: list[dict] = []
        self._total_prs = 0

    def compose(self) -> ComposeResult:
        yield Static("[bold #10b981]📊  Dashboard[/]", id="screen-title")
        yield Static("[dim]Resumen del workspace — para devs y líderes técnicos[/]", id="screen-subtitle")

        yield Horizontal(
            Vertical(
                Static("[bold]Repos totales[/]", classes="dash-metric-label"),
                Static("0", id="dash-repos", classes="dash-metric-value"),
                id="dash-box-repos",
                classes="dash-box",
            ),
            Vertical(
                Static("[bold]PRs abiertos (escaneados)[/]", classes="dash-metric-label"),
                Static("0", id="dash-prs", classes="dash-metric-value"),
                id="dash-box-prs",
                classes="dash-box",
            ),
            Vertical(
                Static("[bold]Actividad reciente (escaneados)[/]", classes="dash-metric-label"),
                Static("0", id="dash-active", classes="dash-metric-value"),
                id="dash-box-active",
                classes="dash-box",
            ),
            Vertical(
                Static("[bold]Sin actividad 90d (escaneados)[/]", classes="dash-metric-label"),
                Static("0", id="dash-stale", classes="dash-metric-value"),
                id="dash-box-stale",
                classes="dash-box",
            ),
            id="dash-metrics",
        )

        yield Static("[bold]PRs abiertos más recientes[/]", classes="dash-section-title")
        yield DataTable(id="dash-table")
        yield Static("", id="dash-status", classes="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        self.run_worker(self._load_dashboard())

    async def _load_dashboard(self) -> None:
        from datetime import datetime, timezone, timedelta
        _, _, workspace = get_auth()
        self._repos = get_repos(workspace)
        total_repos = len(self._repos)
        now = datetime.now(timezone.utc)
        cutoff_90d = now - timedelta(days=90)
        cutoff_7d = now - timedelta(days=7)

        total_prs = 0
        recent_prs: list[tuple] = []
        active_count = 0
        stale_count = 0
        scanned = min(total_repos, 50)

        for repo in self._repos[:50]:
            updated = repo.get("updated")
            dt: datetime | None = None
            if isinstance(updated, datetime):
                dt = updated
            elif updated and isinstance(updated, str):
                try:
                    dt = datetime.fromisoformat(updated.replace("Z", "+00:00"))
                except Exception:
                    dt = None
            if dt:
                if dt > cutoff_7d:
                    active_count += 1
                if dt < cutoff_90d:
                    stale_count += 1

            prs = get_pullrequests(workspace, repo["name"], state="OPEN")
            if prs:
                total_prs += len(prs)
                for pr in prs[:3]:
                    recent_prs.append((
                        repo["name"],
                        pr.get("id", 0),
                        pr.get("title", "")[:40],
                        pr.get("author", {}).get("nickname", "?"),
                        pr.get("created_on", ""),
                    ))

        self._update_metric("dash-repos", str(total_repos))
        self._update_metric("dash-prs", str(total_prs))
        self._update_metric("dash-active", str(active_count))
        self._update_metric("dash-stale", str(stale_count))

        table = self.query_one("#dash-table", DataTable)
        table.clear(columns=True)
        table.add_columns("Repo", "#", "Título", "Autor")

        def _to_timestamp(value) -> int:
            if value and isinstance(value, str):
                try:
                    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
                    return int(dt.timestamp())
                except Exception:
                    pass
            return 0

        try:
            for row in sorted(
                recent_prs,
                key=lambda item: (_to_timestamp(item[4]), -item[1]),
                reverse=True,
            )[:15]:
                table.add_row(row[0], str(row[1]), row[2], row[3])
        except Exception as e:
            self._update_status(f"[red]Error ordenando PRs: {e}[/]")
            for row in recent_prs[:15]:
                table.add_row(row[0], str(row[1]), row[2], row[3])
            return

        self._update_status(
            f"[dim]{total_repos} repos totales | {total_prs} PRs en {scanned} escaneados | "
            f"{active_count} activos | {stale_count} stale[/]"
        )

    def _update_metric(self, widget_id: str, value: str) -> None:
        try:
            self.query_one(f"#{widget_id}", Static).update(f"[bold #10b981]{value}[/]")
        except Exception:
            pass

    def _update_status(self, msg: str) -> None:
        try:
            self.query_one("#dash-status", Static).update(msg)
        except Exception:
            pass

    def action_refresh(self) -> None:
        self._update_status("[yellow]Refrescando...[/]")
        self.run_worker(self._load_dashboard())

    def action_go_home(self) -> None:
        from .home import HomeScreen
        self.app.switch_screen(HomeScreen())

    def action_quit_app(self) -> None:
        self.app.exit()
