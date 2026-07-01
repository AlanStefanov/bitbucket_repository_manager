from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Static

from bitbucket_manager.api import get_workspace_members
from bitbucket_manager.config import get_auth


class MembersScreen(Screen):
    BINDINGS = [
        ("h", "go_home", "Home"),
        ("b", "go_home", "Home"),
        ("escape", "go_home", "Home"),
        ("ctrl+q", "quit_app", "Salir"),
    ]

    def compose(self) -> ComposeResult:
        yield Static("[bold #10b981]👤  Miembros del Workspace[/]", id="screen-title")
        yield Static("[dim]Lista de miembros del workspace de Bitbucket[/]", id="screen-subtitle")
        yield DataTable(id="members-table")
        yield Footer()

    def on_mount(self) -> None:
        self.run_worker(self._load_members())

    async def _load_members(self) -> None:
        _, _, workspace = get_auth()
        table = self.query_one("#members-table", DataTable)
        table.clear()
        table.add_columns("Display Name", "Nickname", "Account ID", "Tipo")

        members = get_workspace_members(workspace) or []
        if not members:
            table.add_row("[dim]No se pudieron cargar miembros[/]", "", "", "")
            return

        for m in members:
            user = m.get("user", m)
            name = user.get("display_name", "?")
            nick = user.get("nickname", "?")
            aid = user.get("account_id", "?")
            t = user.get("type", "user")
            table.add_row(name, nick, aid, t)

    def action_go_home(self) -> None:
        from .home import HomeScreen
        self.app.switch_screen(HomeScreen())

    def action_quit_app(self) -> None:
        self.app.exit()
