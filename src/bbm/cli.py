import argparse
import sys

from bbm import __version__
from bbm.config import load_env_file

load_env_file()


def main():
    parser = argparse.ArgumentParser(
        prog='bbm',
        description='Bitbucket Repository Manager — CLI/TUI suite for Bitbucket Cloud',
    )
    parser.add_argument('--version', '-V', action='store_true', help='Show version')

    subparsers = parser.add_subparsers(dest='command')

    p = subparsers.add_parser('permissions', help='Manage repository permissions')
    perm_sub = p.add_subparsers(dest='action')

    list_p = perm_sub.add_parser('list', help='List current permissions for repos')
    list_p.add_argument('--repo', '-r', action='append', required=True,
                        help='Repository name (can be repeated)')

    grant_p = perm_sub.add_parser('grant', help='Grant permission to a user or group')
    grant_p.add_argument('--user', required=True, help='Username or group name')
    grant_p.add_argument('--role', required=True, choices=['READ', 'WRITE', 'ADMIN'],
                         help='Permission level')
    grant_p.add_argument('--repo', '-r', action='append', required=True,
                         help='Repository name (can be repeated)')
    grant_p.add_argument('--group', action='store_true', help='Target is a group, not a user')
    grant_p.add_argument('--dry-run', action='store_true', help='Simulate without making changes')

    revoke_p = perm_sub.add_parser('revoke', help='Revoke permission from a user or group')
    revoke_p.add_argument('--user', required=True, help='Username or group name')
    revoke_p.add_argument('--repo', '-r', action='append', required=True,
                          help='Repository name (can be repeated)')
    revoke_p.add_argument('--group', action='store_true', help='Target is a group, not a user')
    revoke_p.add_argument('--dry-run', action='store_true', help='Simulate without making changes')

    copy_p = perm_sub.add_parser('copy', help='Copy permissions from one repo to others')
    copy_p.add_argument('--from', dest='source', required=True, help='Source repository')
    copy_p.add_argument('--to', '-t', action='append', required=True,
                        help='Target repository (can be repeated)')
    copy_p.add_argument('--dry-run', action='store_true', help='Simulate without making changes')

    sync_p = perm_sub.add_parser('sync', help='Sync permissions from a CSV file')
    sync_p.add_argument('--file', '-f', required=True, help='CSV file path')
    sync_p.add_argument('--dry-run', action='store_true', help='Simulate without making changes')

    args = parser.parse_args()

    if args.version:
        print(f"bbm v{__version__}")
        return

    if not args.command:
        from bbm.tui import main as tui_main
        tui_main()
        return

    if args.command == 'permissions':
        if not args.action:
            print("Usá: bbm permissions list|grant|revoke|copy|sync")
            print("Ej:   bbm permissions list --repo repo-a")
            return
        from bbm.permissions import handle_permissions
        handle_permissions(args)


if __name__ == "__main__":
    main()
