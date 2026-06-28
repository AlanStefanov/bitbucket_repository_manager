from __future__ import annotations

from datetime import datetime, timezone

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Input, Label, Static

from bbm.api import get_repos, update_repository
from bbm.config import get_auth


class ArchiveScreen(Screen):
    BINDINGS = [
        ("h", "go_home", "Home"),
        ("escape", "go_home", "Home"),
        ("ctrl+q", "quit_app", "Salir"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._repos: list[dict] = []

    def compose(self) -> ComposeResult:
        yield Static("[bold #10b981]🗄️  Archive[/]", id="screen-title")
        yield Static("[dim]Archivá repositorios inactivos[/]", id="screen-subtitle")

        yield Horizontal(
            Vertical(
                Label("Días sin actividad"),
                Input(placeholder="180", id="days-input"),
                Horizontal(
                    Button("🔍 Escanear", id="scan-btn"),
                    Button("📦 Archivar", id="archive-btn", variant="primary"),
                    Button("🔙 Volver", id="back-btn"),
                    id="arc-btns",
                    classes="form-actions",
                ),
                id="arc-form",
                classes="sidebar",
            ),
            Vertical(
                Label("Candidatos"),
                DataTable(id="arc-table"),
                Label("Estado"),
                Static("", id="arc-output", classes="output-box"),
                id="arc-out",
            ),
            id="arc-body",
            classes="content-area",
        )
        yield Static("", id="arc-status", classes="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        self.run_worker(self._load_repos())

    async def _load_repos(self) -> None:
        _, _, workspace = get_auth()
        self._repos = get_repos(workspace)
        self._show(f"[dim]{len(self._repos)} repositorios[/]")

    def _show(self, text: str) -> None:
        self.query_one("#arc-output", Static).update(text)

    def _status(self, text: str) -> None:
        try:
            self.query_one("#arc-status", Static).update(text)
        except Exception:
            pass

    async def _scan(self) -> None:
        days_str = self.query_one("#days-input", Input).value.strip()
        try:
            days = int(days_str) if days_str else 180
        except ValueError:
            self._show("[yellow]Ingresá un número válido[/]")
            return

        _, _, workspace = get_auth()
        table = self.query_one("#arc-table", DataTable)
        table.clear(columns=True)
        table.add_columns("Repositorio", "Última actividad", "Días")

        now = datetime.now(timezone.utc)
        candidates = 0
        for repo in self._repos:
            updated = repo.get("updated", now)
            if isinstance(updated, str):
                try:
                    updated = datetime.fromisoformat(updated.replace("Z", "+00:00"))
                except Exception:
                    updated = now
            delta = (now - updated).days
            if delta >= days:
                candidates += 1
                table.add_row(repo["name"], repo.get("updated_str", ""), str(delta))

        if candidates == 0:
            self._show(f"[green]No hay repos inactivos por {days} días[/]")
        else:
            self._show(f"[yellow]{candidates} candidatos para archivar ({days}+ días inactivos)[/]")

    async def _archive(self) -> None:
        _, _, workspace = get_auth()
        table = self.query_one("#arc-table", DataTable)
        rows = list(table.rows)
        if not rows:
            self._show("[yellow]Primero ejecutá un escaneo[/]")
            return

        self._status("[yellow]Archivando...[/]")
        archived = 0
        errors = 0
        for row in rows:
            name = row.label
            if not name:
                continue
            ok, _ = update_repository(workspace, name, {"project": {"key": "ARCHIVED"}})
            if ok:
                archived += 1
            else:
                errors += 1

        self._show(f"[green]{archived} archivados[/]  [red]{errors} errores[/]")
        self._status(f"[green]{archived} archivados[/]" if errors == 0 else f"[yellow]{archived} arch, {errors} err[/]")
        await self._scan()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "scan-btn":
            self.run_worker(self._scan())
        elif event.button.id == "archive-btn":
            self.run_worker(self._archive())
        elif event.button.id == "back-btn":
            self.action_go_home()

    def action_go_home(self) -> None:
        from .home import HomeScreen
        self.app.switch_screen(HomeScreen())

    def action_quit_app(self) -> None:
        self.app.exit()
