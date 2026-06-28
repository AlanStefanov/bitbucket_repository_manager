from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Input, Label, Select, Static

from bbm.api import (
    delete_user_permission,
    get_permissions_groups,
    get_permissions_users,
    get_repos,
    set_user_permission,
)
from bbm.config import get_auth


class PermissionsScreen(Screen):
    BINDINGS = [
        ("h", "go_home", "Home"),
        ("b", "go_home", "Home"),
        ("escape", "go_home", "Home"),
        ("ctrl+q", "quit_app", "Salir"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._repos: list[dict] = []
        self._selected_repo: str | None = None

    def compose(self) -> ComposeResult:
        yield Static("[bold #10b981]🔐  Permisos[/]", id="screen-title")
        yield Static("[dim]Gestioná permisos de usuarios por repositorio[/]", id="screen-subtitle")

        yield Horizontal(
            Vertical(
                Label("Repositorio"),
                Select([], id="repo-select"),
                Label("Usuario"),
                Input(placeholder="nickname", id="user-input"),
                Label("Rol"),
                Select([("READ", "READ"), ("WRITE", "WRITE"), ("ADMIN", "ADMIN")],
                       id="role-select", value="READ"),
                Horizontal(
                    Button("🔍 Listar", id="list-btn"),
                    Button("🔑 Otorgar", id="grant-btn", variant="primary"),
                    Button("❌ Revocar", id="revoke-btn", variant="error"),
                    id="perm-btns",
                    classes="form-actions",
                ),
                id="perm-form",
                classes="sidebar",
            ),
            Vertical(
                Label("Resultados"),
                Static("", id="perm-output", classes="output-box"),
                id="perm-out",
            ),
            id="perm-body",
            classes="content-area",
        )
        yield Static("", id="perm-status", classes="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        self.run_worker(self._load_repos())

    async def _load_repos(self) -> None:
        _, _, workspace = get_auth()
        self._repos = get_repos(workspace)
        select = self.query_one("#repo-select", Select)
        select.set_options([(r["name"], r["name"]) for r in self._repos])
        if self._repos:
            self._selected_repo = self._repos[0]["name"]

    async def _list_perms(self) -> None:
        _, _, workspace = get_auth()
        repo = self._selected_repo
        if not repo:
            self._show("[yellow]Seleccioná un repositorio[/]")
            return

        users = get_permissions_users(workspace, repo)
        groups = get_permissions_groups(workspace, repo)

        lines: list[str] = []
        lines.append(f"[bold]Permisos en: {repo}[/]")
        lines.append("")
        lines.append("[bold]Usuarios:[/]")
        if users:
            for u in users:
                n = u.get("user", {}).get("display_name", "?")
                nick = u.get("user", {}).get("nickname", "?")
                p = u.get("permission", "?")
                lines.append(f"  · {n} ({nick}) → [bold]{p}[/]")
        else:
            lines.append("  [dim]Sin permisos de usuario[/]")
        lines.append("")
        lines.append("[bold]Grupos:[/]")
        if groups:
            for g in groups:
                lines.append(f"  · {g.get('group', {}).get('name', '?')} → [bold]{g.get('permission', '?')}[/]")
        else:
            lines.append("  [dim]Sin permisos de grupo[/]")
        self._show("\n".join(lines))

    async def _grant_perm(self) -> None:
        _, _, workspace = get_auth()
        repo = self._selected_repo
        user = self.query_one("#user-input", Input).value.strip()
        role = self.query_one("#role-select", Select).value
        if not repo:
            self._show("[yellow]Seleccioná un repositorio[/]")
            return
        if not user:
            self._show("[yellow]Ingresá un nickname[/]")
            return
        ok, err = set_user_permission(workspace, repo, user, (role or "read").lower())
        if ok:
            self._show(f"[green]✓ Permiso otorgado: {user} → {role} en {repo}[/]")
        else:
            self._show(f"[red]✗ {err}[/]")

    async def _revoke_perm(self) -> None:
        _, _, workspace = get_auth()
        repo = self._selected_repo
        user = self.query_one("#user-input", Input).value.strip()
        if not repo:
            self._show("[yellow]Seleccioná un repositorio[/]")
            return
        if not user:
            self._show("[yellow]Ingresá un nickname[/]")
            return
        ok, err = delete_user_permission(workspace, repo, user)
        if ok:
            self._show(f"[green]✓ Permiso revocado: {user} en {repo}[/]")
        else:
            self._show(f"[red]✗ {err}[/]")

    def _show(self, text: str) -> None:
        self.query_one("#perm-output", Static).update(text)

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "repo-select":
            self._selected_repo = event.value

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "list-btn":
            self.run_worker(self._list_perms())
        elif event.button.id == "grant-btn":
            self.run_worker(self._grant_perm())
        elif event.button.id == "revoke-btn":
            self.run_worker(self._revoke_perm())

    def action_go_home(self) -> None:
        from .home import HomeScreen
        self.app.switch_screen(HomeScreen())

    def action_quit_app(self) -> None:
        self.app.exit()
