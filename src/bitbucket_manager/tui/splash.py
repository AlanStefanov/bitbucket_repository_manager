from __future__ import annotations

import asyncio

from textual.app import ComposeResult
from textual.containers import Center, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Static

from ..version import VERSION

LOGO = """\
[bold #10b981]██████╗  ██████╗ ███╗   ███╗[/]
[bold #10b981]██╔══██╗ ██╔══██╗████╗ ████║[/]
[bold #10b981]██████╔╝ ██████╔╝██╔████╔██║[/]
[bold #10b981]██╔══██╗ ██╔══██╗██║╚██╔╝██║[/]
[bold #10b981]██████╔╝ ██║  ██║██║ ╚═╝ ██║[/]
[bold #10b981]╚═════╝  ╚═╝  ╚═╝╚═╝     ╚═╝[/]"""

STEPS: list[tuple[str, str]] = [
    ("Inicializando módulos", "#10b981"),
    ("Verificando configuración", "#22d3ee"),
    ("Conectando con Bitbucket API", "#22d3ee"),
    ("Preparando workspace", "#10b981"),
    ("Listo", "#10b981"),
]


class BootScreen(Screen):
    BINDINGS = [
        ("enter", "skip", "Saltar"),
        ("space", "skip", "Saltar"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._done = False

    def compose(self) -> ComposeResult:
        yield Center(
            Vertical(
                Static(LOGO, id="boot-brand"),
                Static(f"[dim]v{VERSION} · Bitbucket Manager[/]", id="boot-sub"),
                Static("", id="boot-bar"),
                Static("", id="boot-msgs"),
                id="boot-panel",
            ),
            id="boot-root",
        )
        yield Footer()

    async def on_mount(self) -> None:
        asyncio.create_task(self._boot_seq())

    async def _boot_seq(self) -> None:
        widget = self.query_one("#boot-msgs", Static)
        lines: list[str] = []
        for text, color in STEPS:
            if self._done:
                break
            lines.append(f"  [{color}]▶[/]  {text}[dim]...[/]")
            widget.update("\n".join(lines))
            await asyncio.sleep(0.1)
            lines[-1] = f"  [{color}]✓[/]  {text}"
            widget.update("\n".join(lines))
            await asyncio.sleep(0.07)
        if not self._done:
            await asyncio.sleep(0.25)
        self._go_home_or_setup()

    def _go_home_or_setup(self) -> None:
        if self._done:
            return
        self._done = True
        from .setup_screen import SetupScreen, config_is_missing
        if config_is_missing():
            self.app.push_screen(SetupScreen())
        else:
            from .home import HomeScreen
            self.app.switch_screen(HomeScreen())

    def _go_home(self) -> None:
        self._go_home_or_setup()

    def action_skip(self) -> None:
        self._go_home()
