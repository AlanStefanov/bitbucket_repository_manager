from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import Static


class SectionHeader(Static):
    def __init__(self, text: str, icon: str = "") -> None:
        super().__init__(f"[bold #10b981]{icon} {text}[/]" if icon else f"[bold #10b981]{text}[/]")


class RepoStatusDot(Static):
    def __init__(self, cloned: bool) -> None:
        color = "#10b981" if cloned else "#555"
        label = "[OK]" if cloned else "[  ]"
        super().__init__(f"[bold {color}]{label}[/]")


class LoadingOverlay(Static):
    _dots: reactive[int] = reactive(0)

    def __init__(self, message: str = "Cargando") -> None:
        super().__init__("", id="loading-overlay")
        self._message = message

    def on_mount(self) -> None:
        self.set_interval(0.3, self._tick)

    def _tick(self) -> None:
        self._dots = (self._dots + 1) % 4

    def watch__dots(self, dots: int) -> None:
        self.update(f"[dim #22d3ee]{self._message}{'.' * dots}[/]")


class LogPanel(Static):
    def __init__(self) -> None:
        super().__init__("", id="log-panel")

    def clear(self) -> None:
        self.update("")

    def append(self, line: str) -> None:
        current = str(self.renderable or "")
        lines = current.split("\n") if current else []
        lines.append(line)
        if len(lines) > 500:
            lines = lines[-500:]
        self.update("\n".join(lines))


class KeyHintBar(Horizontal):
    def __init__(self, hints: list[tuple[str, str]]) -> None:
        super().__init__(id="key-hint-bar")
        self._hints = hints

    def compose(self) -> ComposeResult:
        parts = []
        for i, (key, desc) in enumerate(self._hints):
            parts.append(f"[#555]{desc}[/] [#10b981]{key}[/]")
        if parts:
            yield Static("  " + "  ·  ".join(parts) + "  ", id="hint-text")
