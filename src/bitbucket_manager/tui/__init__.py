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
from .groups_screen import GroupsScreen
from .members_screen import MembersScreen
from .setup_screen import SetupScreen


class BitbucketManagerApp(App):
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
        "groups": GroupsScreen,
        "members": MembersScreen,
        "setup": SetupScreen,
    }

    TITLE = "Bitbucket Manager"
    BINDINGS = [
        ("ctrl+q", "quit", "Salir"),
    ]

    def on_mount(self) -> None:
        self.push_screen("boot")


def run_tui() -> None:
    app = BitbucketManagerApp()
    app.run()
