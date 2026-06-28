import csv
import json
import os
import subprocess
import sys
import time
from datetime import datetime

from bbm.api import (
    get_repos, create_repository, get_branches,
    get_pullrequests, get_repository, update_repository,
)
from bbm.config import get_auth

MIGRATIONS_DB = os.path.join(os.path.expanduser("~"), ".bbm", "migrations.json")


def _load_migrations():
    if os.path.exists(MIGRATIONS_DB):
        try:
            with open(MIGRATIONS_DB, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return []


def _save_migrations(migrations):
    os.makedirs(os.path.dirname(MIGRATIONS_DB), exist_ok=True)
    with open(MIGRATIONS_DB, 'w') as f:
        json.dump(migrations, f, indent=2)


def _git_mirror_clone(source_url, dest_dir):
    result = subprocess.run(
        ['git', 'clone', '--mirror', source_url, dest_dir],
        capture_output=True, text=True, timeout=300
    )
    if result.returncode != 0:
        return False, result.stderr
    return True, None


def _git_mirror_push(dest_url, dest_dir):
    result = subprocess.run(
        ['git', 'push', '--mirror', dest_url],
        capture_output=True, text=True, timeout=300,
        cwd=dest_dir
    )
    if result.returncode != 0:
        return False, result.stderr
    return True, None


def _estimate_migration_time(repo_name, workspace):
    repo_data = get_repository(workspace, repo_name)
    if not repo_data:
        return "desconocido"
    size = repo_data.get('size', 0)
    if size > 1048576000:  # > 1GB
        return "> 5 minutos (repo grande)"
    elif size > 104857600:  # > 100MB
        return "~ 1-2 minutos"
    else:
        return "~ 10-30 segundos"


def cmd_migrate_plan(args):
    _, _, workspace, _ = get_auth()
    if not workspace:
        print("Error: BB_WORKSPACE no está configurado")
        sys.exit(1)

    repos = args.repo
    target = args.target_workspace

    print(f"\n  Plan de migración:")
    print(f"  {'='*50}")
    print(f"  Origen:  {workspace}")
    print(f"  Destino: {target}")
    print(f"  Repos:   {', '.join(repos)}\n")

    for repo in repos:
        repo_data = get_repository(workspace, repo)
        if not repo_data:
            print(f"  ✗ {repo}: no encontrado o sin acceso")
            continue

        branches = get_branches(workspace, repo)
        prs = get_pullrequests(workspace, repo, state='OPEN')
        n_branches = len(branches) if branches else 0
        n_prs = len(prs) if prs else 0
        eta = _estimate_migration_time(repo, workspace)
        size_mb = repo_data.get('size', 0) / (1024 * 1024)

        dest_exists = get_repository(target, repo)
        print(f"  📦 {repo}")
        print(f"       Tamaño:   {size_mb:.1f} MB")
        print(f"       Branches: {n_branches}")
        print(f"       PRs abiertos: {n_prs}")
        print(f"       ETA:      {eta}")
        print(f"       Destino:  {'EXISTE' if dest_exists else 'no existe aún'}")

    print()
    if not args.dry_run:
        print("  Usá: bbm migrate run ...  para ejecutar la migración")


def cmd_migrate_run(args):
    _, _, workspace, _ = get_auth()
    if not workspace:
        print("Error: BB_WORKSPACE no está configurado")
        sys.exit(1)

    repos = args.repo
    target = args.target_workspace
    dev_dir = os.environ.get("DEV_DIR", os.path.join(os.path.expanduser("~"), "bitbucket-repos"))
    temp_dir = os.path.join(dev_dir, ".migrations")

    if not args.yes:
        print(f"\n  Se migrarán {len(repos)} repo(s) de '{workspace}' a '{target}'.")
        print(f"  Esto clonará con mirror y forzará push al destino.")
        resp = input("  ¿Continuar? (s/N): ").strip().lower()
        if resp != 's':
            print("  Cancelado.")
            return

    results = []
    for repo in repos:
        print(f"\n  Migrando {repo}...")

        # 1. Validate source exists
        repo_data = get_repository(workspace, repo)
        if not repo_data:
            print(f"  ✗ {repo}: origen no encontrado")
            results.append({'repo': repo, 'status': 'error', 'reason': 'origen no encontrado'})
            continue

        # 2. Check destination doesn't exist (or skip)
        dest_exists = get_repository(target, repo)
        if dest_exists:
            if args.force:
                print(f"  ⚠ {repo}: destino ya existe, --force → continuando")
            else:
                print(f"  ✗ {repo}: destino ya existe. Usá --force para sobrescribir o elegí otro nombre")
                results.append({'repo': repo, 'status': 'skipped', 'reason': 'destino existe'})
                continue

        # 3. Create repo in target
        ok, result = create_repository(target, repo)
        if not ok:
            print(f"  ✗ {repo}: no se pudo crear en destino: {result}")
            results.append({'repo': repo, 'status': 'error', 'reason': result})
            continue
        print(f"  ✓ Repositorio creado en {target}")

        # 4. Mirror clone
        clone_url = f"https://x-token-auth:{get_auth()[0]}@bitbucket.org/{workspace}/{repo}.git"
        push_url = f"https://x-token-auth:{get_auth()[0]}@bitbucket.org/{target}/{repo}.git"

        mirror_dir = os.path.join(temp_dir, f"{workspace}_{repo}")
        if os.path.exists(mirror_dir):
            subprocess.run(['rm', '-rf', mirror_dir])

        ok, err = _git_mirror_clone(clone_url, mirror_dir)
        if not ok:
            print(f"  ✗ {repo}: error en mirror clone: {err}")
            results.append({'repo': repo, 'status': 'error', 'reason': err})
            continue
        print(f"  ✓ Mirror clone exitoso")

        # 5. Mirror push
        ok, err = _git_mirror_push(push_url, mirror_dir)
        if not ok:
            print(f"  ✗ {repo}: error en mirror push: {err}")
            results.append({'repo': repo, 'status': 'error', 'reason': err})
            continue
        print(f"  ✓ Mirror push exitoso")

        # 6. Cleanup temp mirror
        subprocess.run(['rm', '-rf', mirror_dir])

        results.append({'repo': repo, 'status': 'ok'})
        print(f"  ✓ {repo} migrado exitosamente")

    # Save to migrations DB
    migs = _load_migrations()
    migs.append({
        'id': f"mig-{int(time.time())}",
        'date': datetime.now().isoformat(),
        'source': workspace,
        'target': target,
        'repos': results,
    })
    _save_migrations(migs)

    print(f"\n  {'='*50}")
    ok = sum(1 for r in results if r['status'] == 'ok')
    err = sum(1 for r in results if r['status'] == 'error')
    skipped = sum(1 for r in results if r['status'] == 'skipped')
    print(f"  Resultado: {ok} migrados, {err} errores, {skipped} omitidos")


def cmd_migrate_status(args):
    migs = _load_migrations()
    if not migs:
        print("  No hay migraciones registradas")
        return
    print(f"\n  Migraciones registradas:\n")
    for m in reversed(migs):
        ok = sum(1 for r in m['repos'] if r['status'] == 'ok')
        err = sum(1 for r in m['repos'] if r['status'] == 'error')
        print(f"  [{m['id']}] {m['date'][:19]} — {m['source']} → {m['target']}")
        print(f"       {ok} ok, {err} errores")
        for r in m['repos']:
            icon = '✓' if r['status'] == 'ok' else '✗' if r['status'] == 'error' else '~'
            reason = f": {r['reason']}" if r.get('reason') else ''
            print(f"       {icon} {r['repo']}{reason}")
        print()


def handle_migrate(args):
    if args.action == 'plan':
        cmd_migrate_plan(args)
    elif args.action == 'run':
        cmd_migrate_run(args)
    elif args.action == 'status':
        cmd_migrate_status(args)
