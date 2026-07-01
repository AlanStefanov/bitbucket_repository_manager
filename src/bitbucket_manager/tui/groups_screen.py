from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Input, Label, Static, Select

from bitbucket_manager.api import (
    create_workspace_group,
    delete_workspace_group,
    get_group_members,
    get_workspace_groups,
    add_group_member,
    remove_group_member,
)
from bitbucket_manager.config import get_auth


class GroupsScreen(Screen):
    BINDINGS = [
        ("h", "go_home", "Home"),
        ("b", "go_home", "Home"),
        ("escape", "go_home", "Home"),
        ("ctrl+q", "quit_app", "Salir"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._groups: list[dict] = []
        self._selected_group: str | None = None

    def compose(self) -> ComposeResult:
        yield Static("[bold #10b981]👥  Grupos[/]", id="screen-title")
        yield Static("[dim]Gestioná grupos del workspace y sus miembros[/]", id="screen-subtitle")

        yield Horizontal(
            Vertical(
                Label("Grupos"),
                Select([], id="group-select"),
                Label("Nombre del nuevo grupo"),
                Input(placeholder="nombre-del-grupo", id="new-group-input"),
                Horizontal(
                    Button("➕ Crear", id="create-btn", variant="primary"),
                    Button("🗑️ Eliminar", id="delete-btn", variant="error"),
                    id="group-btns",
                    classes="form-actions",
                ),
                id="groups-form",
                classes="sidebar",
            ),
            Vertical(
                Label(f"Miembros"),
                Static("", id="members-output", classes="output-box"),
                Label("Agregar miembro"),
                Input(placeholder="nickname", id="member-input"),
                Horizontal(
                    Button("➕ Agregar", id="add-member-btn", variant="primary"),
                    Button("❌ Remover", id="remove-member-btn", variant="error"),
                    id="member-btns",
                    classes="form-actions",
                ),
                id="members-out",
            ),
            id="groups-body",
            classes="content-area",
        )
        yield Static("", id="groups-status", classes="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        self.run_worker(self._load_groups())

    async def _load_groups(self) -> None:
        _, _, workspace = get_auth()
        self._groups = get_workspace_groups(workspace) or []
        select = self.query_one("#group-select", Select)
        opts = [(g.get("name", "?"), g.get("slug", "")) for g in self._groups]
        select.set_options(opts)
        if self._groups:
            self._selected_group = self._groups[0].get("slug")

    async def _show_members(self) -> None:
        _, _, workspace = get_auth()
        slug = self._selected_group
        if not slug:
            self._status("[yellow]Seleccioná un grupo[/]")
            return
        members = get_group_members(workspace, slug)
        lines = [f"[bold]Miembros de: {slug}[/]", ""]
        if members:
            for m in members:
                name = m.get("display_name", m.get("nickname", "?"))
                lines.append(f"  · {name}")
        else:
            lines.append("  [dim]Sin miembros[/]")
        self._show("\n".join(lines))

    async def _create_group(self) -> None:
        _, _, workspace = get_auth()
        name = self.query_one("#new-group-input", Input).value.strip()
        if not name:
            self._status("[yellow]Ingresá un nombre para el grupo[/]")
            return
        ok, result = create_workspace_group(workspace, name)
        if ok:
            self._status(f"[green]✓ Grupo '{name}' creado[/]")
            self.query_one("#new-group-input", Input).value = ""
            await self._load_groups()
        else:
            self._status(f"[red]✗ {result}[/]")

    async def _delete_group(self) -> None:
        _, _, workspace = get_auth()
        slug = self._selected_group
        if not slug:
            self._status("[yellow]Seleccioná un grupo[/]")
            return
        ok, err = delete_workspace_group(workspace, slug)
        if ok:
            self._status(f"[green]✓ Grupo '{slug}' eliminado[/]")
            self._selected_group = None
            await self._load_groups()
            self._show("")
        else:
            self._status(f"[red]✗ {err}[/]")

    async def _add_member(self) -> None:
        _, _, workspace = get_auth()
        slug = self._selected_group
        member = self.query_one("#member-input", Input).value.strip()
        if not slug:
            self._status("[yellow]Seleccioná un grupo[/]")
            return
        if not member:
            self._status("[yellow]Ingresá un nickname[/]")
            return
        ok, err = add_group_member(workspace, slug, member)
        if ok:
            self._status(f"[green]✓ {member} agregado a {slug}[/]")
            self.query_one("#member-input", Input).value = ""
            await self._show_members()
        else:
            self._status(f"[red]✗ {err}[/]")

    async def _remove_member(self) -> None:
        _, _, workspace = get_auth()
        slug = self._selected_group
        member = self.query_one("#member-input", Input).value.strip()
        if not slug:
            self._status("[yellow]Seleccioná un grupo[/]")
            return
        if not member:
            self._status("[yellow]Ingresá un nickname[/]")
            return
        ok, err = remove_group_member(workspace, slug, member)
        if ok:
            self._status(f"[green]✓ {member} removido de {slug}[/]")
            self.query_one("#member-input", Input).value = ""
            await self._show_members()
        else:
            self._status(f"[red]✗ {err}[/]")

    def _show(self, text: str) -> None:
        self.query_one("#members-output", Static).update(text)

    def _status(self, text: str) -> None:
        self.query_one("#groups-status", Static).update(text)

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "group-select":
            self._selected_group = event.value
            self.run_worker(self._show_members())

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "create-btn":
            self.run_worker(self._create_group())
        elif event.button.id == "delete-btn":
            self.run_worker(self._delete_group())
        elif event.button.id == "add-member-btn":
            self.run_worker(self._add_member())
        elif event.button.id == "remove-member-btn":
            self.run_worker(self._remove_member())

    def action_go_home(self) -> None:
        from .home import HomeScreen
        self.app.switch_screen(HomeScreen())

    def action_quit_app(self) -> None:
        self.app.exit()
