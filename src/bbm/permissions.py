import csv
import sys

from bbm.api import (
    get_permissions_users, get_permissions_groups,
    set_user_permission, delete_user_permission,
    set_group_permission, delete_group_permission,
)
from bbm.config import get_auth

ROLES = ['read', 'write', 'admin']

def _normalize_role(role):
    r = role.lower().strip()
    if r in ('read', 'write', 'admin'):
        return r
    print(f"  Rol inválido: {role}. Usá READ, WRITE o ADMIN.")
    return None

def _confirm(count, dry_run):
    if dry_run:
        return True
    try:
        resp = input(f"\nSe modificarán permisos en {count} repositorios. ¿Continuar? (s/N): ")
        return resp.lower().strip() == 's'
    except (EOFError, KeyboardInterrupt):
        return False

def cmd_list(args):
    _, _, workspace, _ = get_auth()
    if not workspace:
        print("Error: BB_WORKSPACE no está configurado")
        sys.exit(1)

    for repo in args.repo:
        print(f"\n{'='*60}")
        print(f"  Permisos para: {repo}")
        print(f"{'='*60}")

        users = get_permissions_users(workspace, repo)
        if users is not None:
            print(f"\n  Usuarios:")
            if users:
                for u in users:
                    print(f"    - {u['user']['display_name']} ({u['user']['nickname']}) → {u.get('permission', '?')}")
            else:
                print("    (sin permisos de usuario)")

        groups = get_permissions_groups(workspace, repo)
        if groups is not None:
            print(f"\n  Grupos:")
            if groups:
                for g in groups:
                    print(f"    - {g['group']['name']} → {g.get('permission', '?')}")
            else:
                print("    (sin permisos de grupo")

def cmd_grant(args):
    _, _, workspace, _ = get_auth()
    if not workspace:
        print("Error: BB_WORKSPACE no está configurado")
        sys.exit(1)

    role = _normalize_role(args.role)
    if not role:
        sys.exit(1)

    if args.dry_run:
        print(f"\n  [DRY-RUN] Se otorgaría rol '{role}' a '{args.user}' en {len(args.repo)} repo(s):")
        for r in args.repo:
            print(f"    ✓ {r}")
        return

    if not _confirm(len(args.repo), args.dry_run):
        print("  Operación cancelada.")
        return

    ok = 0
    fail = 0
    for repo in args.repo:
        if args.group:
            success, err = set_group_permission(workspace, repo, args.user, role)
        else:
            success, err = set_user_permission(workspace, repo, args.user, role)
        if success:
            print(f"  ✓ {repo}")
            ok += 1
        else:
            print(f"  ✗ {repo}: {err}")
            fail += 1

    print(f"\n  Resultado: {ok} ok, {fail} errores")

def cmd_revoke(args):
    _, _, workspace, _ = get_auth()
    if not workspace:
        print("Error: BB_WORKSPACE no está configurado")
        sys.exit(1)

    if args.dry_run:
        print(f"\n  [DRY-RUN] Se revocaría permiso a '{args.user}' en {len(args.repo)} repo(s):")
        for r in args.repo:
            print(f"    ✓ {r}")
        return

    if not _confirm(len(args.repo), args.dry_run):
        print("  Operación cancelada.")
        return

    ok = 0
    fail = 0
    for repo in args.repo:
        if args.group:
            success, err = delete_group_permission(workspace, repo, args.user)
        else:
            success, err = delete_user_permission(workspace, repo, args.user)
        if success:
            print(f"  ✓ {repo}")
            ok += 1
        else:
            print(f"  ✗ {repo}: {err}")
            fail += 1

    print(f"\n  Resultado: {ok} ok, {fail} errores")

def cmd_copy(args):
    _, _, workspace, _ = get_auth()
    if not workspace:
        print("Error: BB_WORKSPACE no está configurado")
        sys.exit(1)

    source_users = get_permissions_users(workspace, args.source)
    source_groups = get_permissions_groups(workspace, args.source)

    if source_users is None and source_groups is None:
        print(f"  Error: no se pudieron leer permisos de '{args.source}'")
        sys.exit(1)

    users_perm = []
    if source_users:
        for u in source_users:
            users_perm.append((u['user']['nickname'], u.get('permission', 'read')))
    groups_perm = []
    if source_groups:
        for g in source_groups:
            groups_perm.append((g['group']['name'], g.get('permission', 'read')))

    if args.dry_run:
        print(f"\n  [DRY-RUN] Se copiarían permisos desde '{args.source}' a {len(args.to)} repo(s):")
        if users_perm:
            print(f"    Usuarios: {', '.join(f'{u}→{p}' for u, p in users_perm)}")
        if groups_perm:
            print(f"    Grupos: {', '.join(f'{g}→{p}' for g, p in groups_perm)}")
        for t in args.to:
            print(f"    → {t}")
        return

    targets = len(args.to) * (len(users_perm) + len(groups_perm))
    if not _confirm(targets, args.dry_run):
        print("  Operación cancelada.")
        return

    for t in args.to:
        for user, perm in users_perm:
            success, err = set_user_permission(workspace, t, user, perm)
            if success:
                print(f"  ✓ {t}: usuario {user} → {perm}")
            else:
                print(f"  ✗ {t}: usuario {user} → {err}")
        for group, perm in groups_perm:
            success, err = set_group_permission(workspace, t, group, perm)
            if success:
                print(f"  ✓ {t}: grupo {group} → {perm}")
            else:
                print(f"  ✗ {t}: grupo {group} → {err}")

def cmd_sync(args):
    _, _, workspace, _ = get_auth()
    if not workspace:
        print("Error: BB_WORKSPACE no está configurado")
        sys.exit(1)

    entries = []
    try:
        with open(args.file, 'r') as f:
            if args.file.endswith('.csv'):
                reader = csv.DictReader(f)
                for row in reader:
                    entries.append(row)
            else:
                print("  Solo se soporta CSV por ahora")
                sys.exit(1)
    except FileNotFoundError:
        print(f"  Archivo no encontrado: {args.file}")
        sys.exit(1)
    except Exception as e:
        print(f"  Error al leer archivo: {e}")
        sys.exit(1)

    if not entries:
        print("  Archivo vacío o sin datos válidos")
        return

    if args.dry_run:
        print(f"\n  [DRY-RUN] Se procesarían {len(entries)} entradas del archivo '{args.file}':")
        for e in entries:
            action = e.get('action', 'grant')
            target = e.get('type', 'user')
            who = e.get('user') or e.get('group', '?')
            role = e.get('role', 'read')
            repos = e.get('repos', '')
            print(f"    {action} {target} '{who}' → {role} en {repos}")
        return

    total = len(entries)
    if not _confirm(total, args.dry_run):
        print("  Operación cancelada.")
        return

    ok = 0
    fail = 0
    for e in entries:
        action = e.get('action', 'grant')
        target = e.get('type', 'user')
        who = e.get('user') or e.get('group', '')
        role = e.get('role', 'read')
        repos_str = e.get('repos', '')
        repos = [r.strip() for r in repos_str.split(',') if r.strip()]

        for repo in repos:
            if action == 'revoke':
                if target == 'group':
                    success, err = delete_group_permission(workspace, repo, who)
                else:
                    success, err = delete_user_permission(workspace, repo, who)
            else:
                if target == 'group':
                    success, err = set_group_permission(workspace, repo, who, role)
                else:
                    success, err = set_user_permission(workspace, repo, who, role)

            if success:
                print(f"  ✓ {repo}: {action} {who} → {role if action == 'grant' else 'revocado'}")
                ok += 1
            else:
                print(f"  ✗ {repo}: {action} {who} → {err}")
                fail += 1

    print(f"\n  Resultado: {ok} ok, {fail} errores")

def handle_permissions(args):
    if args.action == 'list':
        cmd_list(args)
    elif args.action == 'grant':
        cmd_grant(args)
    elif args.action == 'revoke':
        cmd_revoke(args)
    elif args.action == 'copy':
        cmd_copy(args)
    elif args.action == 'sync':
        cmd_sync(args)
    else:
        print("Comando de permisos no reconocido. Usá: list, grant, revoke, copy, sync")
