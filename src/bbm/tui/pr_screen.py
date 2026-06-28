from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Static

from bbm.api import approve_pullrequest, get_pullrequests, get_repos
from bbm.config import get_auth


class PRScreen(Screen):
    BINDINGS = [
        ("h", "go_home", "Home"),
        ("escape", "go_home", "Home"),
        ("ctrl+q", "quit_app", "Salir"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._repos: list[dict] = []

    def compose(self) -> ComposeResult:
        yield Static("[bold #10b981]✅  Pull Requests[/]", id="screen-title")
        yield Static("[dim]Gestión de Pull Requests abiertos[/]", id="screen-subtitle")
        yield DataTable(id="pr-table")
        yield Horizontal(
            Button("📋 Listar abiertos", id="list-btn"),
            Button("✅ Auto-approve", id="approve-btn", variant="primary"),
            Button("🔙 Volver", id="back-btn"),
            id="pr-bar",
            classes="action-bar",
        )
        yield Static("", id="pr-status", classes="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        self._update_status("[dim]Presioná 'Listar abiertos' para cargar[/]")

    async def _load_repos(self) -> None:
        _, _, workspace = get_auth()
        self._repos = get_repos(workspace)

    async def _list_prs(self) -> None:
        await self._load_repos()
        _, _, workspace = get_auth()
        table = self.query_one("#pr-table", DataTable)
        table.clear(columns=True)
        table.add_columns("Repo", "#", "Título", "Autor", "Branch")

        self._update_status("[yellow]Cargando PRs...[/]")
        total = 0
        for repo in self._repos[:20]:
            prs = get_pullrequests(workspace, repo["name"], state="OPEN")
            if not prs:
                continue
            for pr in prs:
                author = pr.get("author", {}).get("nickname", "?")
                src = pr.get("source", {}).get("branch", {}).get("name", "?")
                table.add_row(repo["name"], str(pr["id"]), pr["title"][:45], author, src)
                total += 1

        self._update_status(f"[dim]{total} PRs abiertos en {len(self._repos)} repos[/]")

    async def _auto_approve(self) -> None:
        await self._load_repos()
        _, _, workspace = get_auth()

        table = self.query_one("#pr-table", DataTable)
        table.clear(columns=True)
        table.add_columns("Repo", "#", "Resultado")

        self._update_status("[yellow]Procesando PRs...[/]")
        approved = 0
        skipped = 0
        errors = 0

        for repo in self._repos[:20]:
            prs = get_pullrequests(workspace, repo["name"], state="OPEN")
            if not prs:
                continue
            for pr in prs:
                pid = pr["id"]
                participants = pr.get("participants", [])
                already = any(p.get("approved") for p in participants if p.get("user", {}).get("nickname") != "bbm-auto")
                if already:
                    skipped += 1
                    table.add_row(repo["name"], str(pid), "[dim]ya aprobado[/]")
                    continue
                ok, err = approve_pullrequest(workspace, repo["name"], pid)
                if ok:
                    approved += 1
                    table.add_row(repo["name"], str(pid), "[green]✓ aprobado[/]")
                else:
                    errors += 1
                    table.add_row(repo["name"], str(pid), f"[red]✗ {err[:25]}[/]")

        self._update_status(
            f"[green]{approved} aprobados[/]  "
            f"[dim]{skipped} ya aprobados[/]  "
            f"[red]{errors} errores[/]"
        )

    def _update_status(self, msg: str) -> None:
        try:
            self.query_one("#pr-status", Static).update(msg)
        except Exception:
            pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "list-btn":
            self.run_worker(self._list_prs())
        elif event.button.id == "approve-btn":
            self.run_worker(self._auto_approve())
        elif event.button.id == "back-btn":
            self.action_go_home()

    def action_go_home(self) -> None:
        from .home import HomeScreen
        self.app.switch_screen(HomeScreen())

    def action_quit_app(self) -> None:
        self.app.exit()
