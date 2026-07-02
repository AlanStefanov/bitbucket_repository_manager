from __future__ import annotations

import os

from textual.app import ComposeResult
from textual.containers import Center, Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Footer, Input, Label, Static

CONFIG_DIR = os.path.expanduser("~/.config/bitbucket-manager")
CONFIG_PATH = os.path.join(CONFIG_DIR, "env")


def config_is_missing() -> bool:
    token = os.environ.get("BB_TOKEN") or ""
    username = os.environ.get("BB_USERNAME") or ""
    workspace = os.environ.get("BB_WORKSPACE") or ""
    return not (token and username and workspace)


class SetupScreen(Screen):
    BINDINGS = [
        ("escape", "go_home", "Omitir"),
        ("ctrl+q", "app.quit", "Salir"),
    ]

    def compose(self) -> ComposeResult:
        yield Center(
            Vertical(
                Static("[bold #10b891]Configuracion Inicial[/]", id="setup-title"),
                Static(
                    "[dim]Completa los datos para conectar con Bitbucket Cloud[/]",
                    id="setup-subtitle",
                ),
                Label("Email de Atlassian (BB_USERNAME)"),
                Input(
                    placeholder="alan@ejemplo.com",
                    id="input-username",
                ),
                Label("Token de app (BB_TOKEN)"),
                Input(
                    placeholder="ATCTT3xFf...",
                    id="input-token",
                    password=True,
                ),
                Label("Workspace (BB_WORKSPACE)"),
                Input(
                    placeholder="mi-equipo",
                    id="input-workspace",
                ),
                Label("Directorio de desarrollo (DEV_DIR)"),
                Input(
                    placeholder="/home/user/Documents/bitbucket-repos",
                    id="input-devdir",
                ),
                Horizontal(
                    Button("Guardar", variant="primary", id="btn-save"),
                    Button("Omitir", id="btn-skip"),
                    classes="setup-actions",
                ),
                Static("", id="setup-status"),
                id="setup-panel",
            ),
            id="setup-root",
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-save":
            self._save()
        elif event.button.id == "btn-skip":
            self._go_home()

    def action_go_home(self) -> None:
        self._go_home()

    def _go_home(self) -> None:
        from .home import HomeScreen

        self.app.switch_screen(HomeScreen())

    def _save(self) -> None:
        username = self.query_one("#input-username", Input).value.strip()
        token = self.query_one("#input-token", Input).value.strip()
        workspace = self.query_one("#input-workspace", Input).value.strip()
        devdir = self.query_one("#input-devdir", Input).value.strip()

        if not username:
            self._set_status("[red]El email es obligatorio[/]")
            return
        if not token:
            self._set_status("[red]El token es obligatorio[/]")
            return
        if not workspace:
            self._set_status("[red]El workspace es obligatorio[/]")
            return
        if not devdir:
            devdir = os.path.expanduser("~/Documents/bitbucket-repos")

        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_PATH, "w") as f:
            f.write(f"BB_USERNAME={username}\n")
            f.write(f"BB_TOKEN={token}\n")
            f.write(f"BB_WORKSPACE={workspace}\n")
            f.write(f"DEV_DIR={devdir}\n")

        os.environ["BB_USERNAME"] = username
        os.environ["BB_TOKEN"] = token
        os.environ["BB_WORKSPACE"] = workspace
        os.environ["DEV_DIR"] = devdir

        self._set_status("[green]Configuracion guardada[/]")
        self.app.set_timer(0.5, self._go_home)

    def _set_status(self, msg: str) -> None:
        self.query_one("#setup-status", Static).update(msg)
