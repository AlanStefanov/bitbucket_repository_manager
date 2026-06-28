from __future__ import annotations

import json
import os
from collections import defaultdict

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Static

from bbm.api import get_repos
from bbm.config import get_auth


class DepsScreen(Screen):
    BINDINGS = [
        ("h", "go_home", "Home"),
        ("escape", "go_home", "Home"),
        ("ctrl+q", "quit_app", "Salir"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._repos: list[dict] = []

    def compose(self) -> ComposeResult:
        yield Static("[bold #10b981]🔗  Dependencias[/]", id="screen-title")
        yield Static("[dim]Análisis de dependencias entre repos[/]", id="screen-subtitle")
        yield DataTable(id="deps-table")
        yield Horizontal(
            Button("🔍 Escanear", id="scan-btn"),
            Button("👻 Huérfanos", id="orphans-btn", variant="warning"),
            Button("🔙 Volver", id="back-btn"),
            id="deps-bar",
            classes="action-bar",
        )
        yield Static("", id="deps-status", classes="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        self._update_status("[dim]Presioná 'Escanear' para analizar[/]")
        self.run_worker(self._load_repos())

    async def _load_repos(self) -> None:
        _, _, workspace = get_auth()
        self._repos = get_repos(workspace)

    def _update_status(self, text: str) -> None:
        try:
            self.query_one("#deps-status", Static).update(text)
        except Exception:
            pass

    def _load_dev_dir(self) -> str:
        return os.environ.get("DEV_DIR", os.path.join(os.path.expanduser("~"), "bitbucket-repos"))

    async def _scan(self) -> None:
        dev_dir = self._load_dev_dir()
        names = [r["name"] for r in self._repos]
        table = self.query_one("#deps-table", DataTable)
        table.clear(columns=True)
        table.add_columns("Repositorio", "Dependencias")

        self._update_status("[yellow]Escaneando dependencias...[/]")
        found = 0
        total_deps = 0

        for name in names[:30]:
            path = os.path.join(dev_dir, name)
            deps: list[str] = []

            for fname in ("setup.py", "setup.cfg", "pyproject.toml", "requirements.txt"):
                fp = os.path.join(path, fname)
                if os.path.exists(fp):
                    with open(fp, "r", errors="ignore") as f:
                        content = f.read()
                    for ref in names:
                        if ref != name and ref in content and ref not in deps:
                            deps.append(ref)

            pkg = os.path.join(path, "package.json")
            if os.path.exists(pkg):
                try:
                    with open(pkg) as f:
                        data = json.load(f)
                    for dep_name in list(data.get("dependencies", {})) + list(data.get("devDependencies", {})):
                        for ref in names:
                            if ref != name and ref.lower() in dep_name.lower() and ref not in deps:
                                deps.append(ref)
                except Exception:
                    pass

            table.add_row(name, ", ".join(deps) if deps else "[dim]ninguna[/]")
            if deps:
                found += 1
                total_deps += len(deps)

        self._update_status(f"[dim]{found} repos con {total_deps} dependencias[/]")

    async def _orphans(self) -> None:
        dev_dir = self._load_dev_dir()
        names = [r["name"] for r in self._repos]

        referenced: set[str] = set()
        for name in names:
            path = os.path.join(dev_dir, name)
            for fname in ("setup.py", "setup.cfg", "pyproject.toml", "requirements.txt"):
                fp = os.path.join(path, fname)
                if os.path.exists(fp):
                    with open(fp, "r", errors="ignore") as f:
                        content = f.read()
                    for ref in names:
                        if ref != name and ref in content:
                            referenced.add(ref)

            pkg = os.path.join(path, "package.json")
            if os.path.exists(pkg):
                try:
                    with open(pkg) as f:
                        data = json.load(f)
                    for dep_name in list(data.get("dependencies", {})) + list(data.get("devDependencies", {})):
                        for ref in names:
                            if ref != name and ref.lower() in dep_name.lower():
                                referenced.add(ref)
                except Exception:
                    pass

        table = self.query_one("#deps-table", DataTable)
        table.clear(columns=True)
        table.add_columns("Repositorio", "Estado")

        orphans = sorted(set(names) - referenced)
        if orphans:
            for name in orphans:
                table.add_row(name, "[yellow]huérfano[/]")
            self._update_status(f"[yellow]{len(orphans)} repos huérfanos[/]")
        else:
            table.add_row("(todos)", "[green]sin huérfanos[/]")
            self._update_status("[green]✓ No hay repos huérfanos[/]")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "scan-btn":
            self.run_worker(self._scan())
        elif event.button.id == "orphans-btn":
            self.run_worker(self._orphans())
        elif event.button.id == "back-btn":
            self.action_go_home()

    def action_go_home(self) -> None:
        from .home import HomeScreen
        self.app.switch_screen(HomeScreen())

    def action_quit_app(self) -> None:
        self.app.exit()
