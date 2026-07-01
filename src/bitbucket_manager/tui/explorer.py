from __future__ import annotations

import os

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Static

from bitbucket_manager.api import (
    checkout_repo,
    clone_repo,
    get_repo_branches,
    get_repos,
    pull_repo,
)
from bitbucket_manager.config import get_auth


class ExplorerScreen(Screen):
    BINDINGS = [
        ("h", "go_home", "Home"),
        ("b", "go_home", "Home"),
        ("escape", "go_home", "Home"),
        ("r", "refresh", "Refrescar"),
        ("ctrl+r", "refresh", "Refrescar"),
        ("ctrl+q", "quit_app", "Salir"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._repos: list[dict] = []
        self._cloned: list[bool] = []
        self._loading = False

    def compose(self) -> ComposeResult:
        yield Static("[bold #10b981]📦  Repos[/]", id="screen-title")
        yield Static("[dim]Repositorios del workspace[/]", id="screen-subtitle")
        yield DataTable(id="repo-table")
        yield Horizontal(
            Button("📋 Clonar", id="clone-btn", variant="primary"),
            Button("⬇️ Pull", id="pull-btn"),
            Button("🔄 Checkout", id="checkout-btn"),
            Button("🔄 Refrescar", id="refresh-btn"),
            Button("🔙 Volver", id="back-btn"),
            id="exp-bar",
            classes="action-bar",
        )
        yield Static("", id="exp-status", classes="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        self._loading = True
        self._update_status("Cargando repositorios...")
        self.run_worker(self._load_repos())

    async def _load_repos(self) -> None:
        _, _, workspace = get_auth()
        repos = get_repos(workspace)
        self._repos = repos
        dev_dir = os.environ.get("DEV_DIR", os.path.join(os.path.expanduser("~"), "bitbucket-repos"))
        self._cloned = [
            os.path.exists(os.path.join(dev_dir, r["name"]))
            and os.path.isdir(os.path.join(dev_dir, r["name"], ".git"))
            for r in repos
        ]
        self._loading = False
        self._update_table()
        if not repos:
            self._update_status("[yellow]No se pudieron cargar repositorios. Verificá credenciales.[/]")
        else:
            self._update_status(f"[dim]{len(repos)} repositorios[/]")

    def _update_table(self) -> None:
        table = self.query_one("#repo-table", DataTable)
        table.clear(columns=True)
        table.add_columns("", "Nombre", "Última actividad")
        for i, repo in enumerate(self._repos):
            status = "✅" if self._cloned[i] else "⬜"
            table.add_row(status, repo["name"], repo.get("updated_str", ""))

    def _update_status(self, msg: str) -> None:
        try:
            self.query_one("#exp-status", Static).update(msg)
        except Exception:
            pass

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if event.cursor_row is not None:
            self.run_worker(self._clone_row(event.cursor_row))

    async def _clone_row(self, row: int) -> None:
        if self._loading or row >= len(self._repos):
            return
        repo = self._repos[row]
        if self._cloned[row]:
            self._update_status(f"[green]✓ Ya clonado: {repo['name']}[/]")
            return
        self._update_status(f"[yellow]📥 Clonando {repo['name']}...[/]")
        ok, msg = clone_repo(repo["name"], repo.get("ws_slug"))
        if ok:
            self._cloned[row] = True
            self._update_table()
            self._update_status(f"[green]✓ Clonado: {repo['name']}[/]")
        else:
            self._update_status(f"[red]✗ {msg}[/]")

    async def _pull_row(self, row: int) -> None:
        if self._loading or row >= len(self._repos):
            return
        repo = self._repos[row]
        if not self._cloned[row]:
            self._update_status(f"[yellow]⚠️ {repo['name']} no está clonado[/]")
            return
        self._update_status(f"[yellow]⬇️ Pull de {repo['name']}...[/]")
        ok, msg = pull_repo(repo["name"], repo.get("ws_slug"))
        if ok:
            self._update_status(f"[green]✓ Pull OK: {repo['name']} — {msg[:60]}[/]")
        else:
            self._update_status(f"[red]✗ Pull falló: {msg[:80]}[/]")

    async def _checkout_row(self, row: int) -> None:
        if self._loading or row >= len(self._repos):
            return
        repo = self._repos[row]
        if not self._cloned[row]:
            self._update_status(f"[yellow]⚠️ {repo['name']} no está clonado[/]")
            return
        branches = get_repo_branches(repo["name"])
        if not branches:
            self._update_status(f"[red]✗ No se pudieron leer branches de {repo['name']}[/]")
            return
        # For now checkout to the first non-current branch, or main/master if available
        target = None
        for b in branches:
            if b in ("main", "master"):
                target = b
                break
        if not target and len(branches) > 1:
            # Try to find a branch that isn't HEAD
            for b in branches:
                if b != "HEAD":
                    target = b
                    break
        if not target:
            target = branches[0] if branches else None
        if not target:
            self._update_status(f"[red]✗ No hay branches disponibles[/]")
            return
        self._update_status(f"[yellow]🔄 Checkout {repo['name']} → {target}...[/]")
        ok, msg = checkout_repo(repo["name"], target)
        if ok:
            self._update_status(f"[green]✓ Checkout OK: {repo['name']} → {target}[/]")
        else:
            self._update_status(f"[red]✗ Checkout falló: {msg[:80]}[/]")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        table = self.query_one("#repo-table", DataTable)
        cursor = table.cursor_row
        if event.button.id == "clone-btn":
            if cursor is not None:
                self.run_worker(self._clone_row(cursor))
        elif event.button.id == "pull-btn":
            if cursor is not None:
                self.run_worker(self._pull_row(cursor))
        elif event.button.id == "checkout-btn":
            if cursor is not None:
                self.run_worker(self._checkout_row(cursor))
        elif event.button.id == "refresh-btn":
            self._loading = True
            self._update_status("[yellow]Refrescando...[/]")
            self.run_worker(self._load_repos())
        elif event.button.id == "back-btn":
            self.action_go_home()

    def action_refresh(self) -> None:
        self._loading = True
        self._update_status("[yellow]Refrescando...[/]")
        self.run_worker(self._load_repos())

    def action_go_home(self) -> None:
        from .home import HomeScreen
        self.app.switch_screen(HomeScreen())

    def action_quit_app(self) -> None:
        self.app.exit()
