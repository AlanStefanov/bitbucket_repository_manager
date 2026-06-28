from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Input, Label, Select, Static

from bbm.api import get_branches, get_pullrequests, get_repos, get_repository
from bbm.config import get_auth


class MigrationScreen(Screen):
    BINDINGS = [
        ("h", "go_home", "Home"),
        ("b", "go_home", "Home"),
        ("escape", "go_home", "Home"),
        ("ctrl+q", "quit_app", "Salir"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._repos: list[dict] = []

    def compose(self) -> ComposeResult:
        yield Static("[bold #10b981]📋  Migración[/]", id="screen-title")
        yield Static("[dim]Migrá repositorios entre workspaces[/]", id="screen-subtitle")

        yield Horizontal(
            Vertical(
                Label("Workspace destino"),
                Input(placeholder="nombre-workspace", id="target-ws"),
                Label("Repositorio"),
                Select([], id="repo-select"),
                Horizontal(
                    Button("🔍 Plan", id="plan-btn"),
                    Button("▶️ Migrar", id="run-btn", variant="primary"),
                    id="mig-btns",
                    classes="form-actions",
                ),
                id="mig-form",
                classes="sidebar",
            ),
            Vertical(
                Label("Plan de migración"),
                DataTable(id="mig-table"),
                Label("Estado"),
                Static("", id="mig-output", classes="output-box"),
                id="mig-out",
            ),
            id="mig-body",
            classes="content-area",
        )
        yield Static("", id="mig-status", classes="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        self.run_worker(self._load_repos())

    async def _load_repos(self) -> None:
        _, _, workspace = get_auth()
        self._repos = get_repos(workspace)
        select = self.query_one("#repo-select", Select)
        select.set_options([(r["name"], r["name"]) for r in self._repos])
        self._show(f"[dim]{len(self._repos)} repositorios cargados[/]")

    def _show(self, text: str) -> None:
        self.query_one("#mig-output", Static).update(text)

    def _status(self, text: str) -> None:
        try:
            self.query_one("#mig-status", Static).update(text)
        except Exception:
            pass

    async def _plan(self) -> None:
        target = self.query_one("#target-ws", Input).value.strip()
        select = self.query_one("#repo-select", Select)
        repo = select.value

        if not target:
            self._show("[yellow]Ingresá un workspace destino[/]")
            return
        if not repo:
            self._show("[yellow]Seleccioná un repositorio[/]")
            return

        _, _, workspace = get_auth()
        self._show(f"[yellow]Analizando {repo}...[/]")

        table = self.query_one("#mig-table", DataTable)
        table.clear(columns=True)
        table.add_columns("Item", "Detalle")

        info = get_repository(workspace, repo)
        branches = get_branches(workspace, repo)
        prs = get_pullrequests(workspace, repo)

        table.add_row("Repositorio", repo or "")
        table.add_row("Origen", workspace or "")
        table.add_row("Destino", target)
        table.add_row("Branches", str(len(branches) if branches else 0))
        table.add_row("PRs abiertos", str(len(prs) if prs else 0))

        self._show(
            f"[green]Plan listo[/]\n"
            f"[dim]• {repo}[/dim] [dim]#10b981]→[/] {target}\n"
            f"[dim]• Ejecutar con ▶ Migrar[/]"
        )

    async def _run(self) -> None:
        import os
        import subprocess
        import shutil

        target = self.query_one("#target-ws", Input).value.strip()
        select = self.query_one("#repo-select", Select)
        repo = select.value

        if not target:
            self._show("[yellow]Ingresá un workspace destino[/]")
            return
        if not repo:
            self._show("[yellow]Seleccioná un repositorio[/]")
            return

        _, _, workspace = get_auth()
        self._status(f"[yellow]Migrando {repo} → {target}...[/]")
        self._show(f"[yellow]Creando repositorio en {target}...[/]")

        from bbm.api import create_repository
        ok, result = create_repository(target, repo)
        if not ok:
            self._show(f"[red]✗ Error al crear repo: {result}[/]")
            self._status("[red]Migración fallida[/]")
            return

        clone_url = f"https://bitbucket.org/{workspace}/{repo}.git"
        push_url = f"https://bitbucket.org/{target}/{repo}.git"
        dest = f"/tmp/bbm-migrate-{repo}"

        self._show(f"[yellow]Clonando mirror...[/]")
        try:
            r = subprocess.run(["git", "clone", "--mirror", clone_url, dest],
                               capture_output=True, text=True, timeout=300)
            if r.returncode != 0:
                shutil.rmtree(dest, ignore_errors=True)
                self._show(f"[red]✗ Error al clonar: {r.stderr[:200]}[/]")
                self._status("[red]Migración fallida[/]")
                return
        except Exception as e:
            shutil.rmtree(dest, ignore_errors=True)
            self._show(f"[red]✗ {e}[/]")
            self._status("[red]Migración fallida[/]")
            return

        self._show(f"[yellow]Subiendo a {target}...[/]")
        try:
            r = subprocess.run(["git", "push", "--mirror", push_url],
                               capture_output=True, text=True, timeout=300, cwd=dest)
            shutil.rmtree(dest, ignore_errors=True)
            if r.returncode == 0:
                self._show(f"[green]✓ Migración completada: {repo} → {target}[/]")
                self._status("[green]Migración exitosa[/]")
            else:
                self._show(f"[red]✗ Error al pushear: {r.stderr[:200]}[/]")
                self._status("[red]Migración fallida[/]")
        except subprocess.TimeoutExpired:
            shutil.rmtree(dest, ignore_errors=True)
            self._show("[red]✗ Timeout (5 min)[/]")
            self._status("[red]Migración fallida[/]")
        except Exception as e:
            shutil.rmtree(dest, ignore_errors=True)
            self._show(f"[red]✗ {e}[/]")
            self._status("[red]Migración fallida[/]")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "plan-btn":
            self.run_worker(self._plan())
        elif event.button.id == "run-btn":
            self.run_worker(self._run())

    def action_go_home(self) -> None:
        from .home import HomeScreen
        self.app.switch_screen(HomeScreen())

    def action_quit_app(self) -> None:
        self.app.exit()
