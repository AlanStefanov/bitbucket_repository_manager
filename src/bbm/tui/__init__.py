from __future__ import annotations

from textual.app import App

from .splash import BootScreen
from .home import HomeScreen
from .dashboard_screen import DashboardScreen
from .explorer import ExplorerScreen
from .permissions_screen import PermissionsScreen
from .pr_screen import PRScreen
from .migration_screen import MigrationScreen
from .archive_screen import ArchiveScreen
from .deps_screen import DepsScreen


class BBMApp(App):
    CSS_PATH = "styles.tcss"
    SCREENS = {
        "boot": BootScreen,
        "home": HomeScreen,
        "dashboard": DashboardScreen,
        "explorer": ExplorerScreen,
        "permissions": PermissionsScreen,
        "pr": PRScreen,
        "migration": MigrationScreen,
        "archive": ArchiveScreen,
        "deps": DepsScreen,
    }

    TITLE = "BRM — Bitbucket Repository Manager"
    BINDINGS = [
        ("ctrl+q", "quit", "Salir"),
    ]

    def on_mount(self) -> None:
        self.push_screen("boot")


def run_tui() -> None:
    app = BBMApp()
    app.run()
