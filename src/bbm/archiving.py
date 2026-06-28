import json
import os
import sys
import yaml

from bbm.api import get_repos, update_repository, get_repository
from bbm.config import get_auth

ARCHIVE_DB = os.path.join(os.path.expanduser("~"), ".bbm", "archive.json")
DEFAULT_RULES_PATH = os.path.join(os.path.expanduser("~"), ".bbm", "archive-rules.yml")
ARCHIVE_PROJECT_KEY = "ARCHIVED"


def _load_archive_db():
    if os.path.exists(ARCHIVE_DB):
        try:
            with open(ARCHIVE_DB, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return []


def _save_archive_db(entries):
    os.makedirs(os.path.dirname(ARCHIVE_DB), exist_ok=True)
    with open(ARCHIVE_DB, 'w') as f:
        json.dump(entries, f, indent=2)


def _load_rules(path):
    try:
        with open(path, 'r') as f:
            config = yaml.safe_load(f)
        return config.get('archive_rules', []) if config else []
    except FileNotFoundError:
        return None
    except yaml.YAMLError as e:
        print(f"  Error en el archivo YAML: {e}")
        sys.exit(1)


def cmd_archive_scan(args):
    _, _, workspace, _ = get_auth()
    if not workspace:
        print("Error: BB_WORKSPACE no está configurado")
        sys.exit(1)

    rules_path = args.rules or DEFAULT_RULES_PATH
    rules = _load_rules(rules_path)
    days = args.days

    if rules is None and not days:
        print("  Especificá --days o un archivo de reglas con --rules")
        return

    repos = get_repos(workspace)
    if not repos:
        print("  No se encontraron repositorios")
        return

    candidates = []
    from datetime import datetime, timezone

    for repo in repos:
        reason = None
        # Check rules
        if rules:
            for rule in rules:
                if not rule.get('enabled', True):
                    continue
                conds = rule.get('conditions', {})
                max_days = conds.get('last_commit_days', days or 365)
                exclude = conds.get('exclude_repos', [])
                exclude_patterns = conds.get('exclude_patterns', [])

                if repo['name'] in exclude:
                    continue

                import fnmatch
                if any(fnmatch.fnmatch(repo['name'], p) for p in exclude_patterns):
                    continue

                updated = repo.get('updated', datetime.min)
                if hasattr(updated, 'tzinfo') and updated.tzinfo is None:
                    updated = updated.replace(tzinfo=timezone.utc)
                age_days = (datetime.now(timezone.utc) - updated).days if updated != datetime.min else 9999

                if age_days >= max_days:
                    reason = f"sin commits en {age_days} días (regla: {rule.get('name', 'unnamed')})"
                    break

        elif days:
            updated = repo.get('updated', datetime.min)
            if hasattr(updated, 'tzinfo') and updated.tzinfo is None:
                updated = updated.replace(tzinfo=timezone.utc)
            age_days = (datetime.now(timezone.utc) - updated).days if updated != datetime.min else 9999
            if age_days >= days:
                reason = f"sin commits en {age_days} días"

        if reason:
            candidates.append({**repo, 'archive_reason': reason})
            print(f"  ✓ {repo['name']}: {reason}")

    if not candidates:
        print("  No se encontraron repositorios candidatos para archivar")

    return candidates


def cmd_archive_run(args):
    _, _, workspace, _ = get_auth()
    if not workspace:
        print("Error: BB_WORKSPACE no está configurado")
        sys.exit(1)

    repos = args.repo
    if not repos:
        candidates = cmd_archive_scan(args)
        if not candidates:
            return
        repos = [r['name'] for r in candidates]

    if args.dry_run:
        print(f"\n  [DRY-RUN] Se archivarían {len(repos)} repositorio(s):")
        for r in repos:
            print(f"    → {r}")
        return

    print(f"\n  Se archivarán {len(repos)} repositorio(s)") if not args.yes else None
    if not args.yes:
        resp = input("  ¿Continuar? (s/N): ").strip().lower()
        if resp != 's':
            print("  Cancelado.")
            return

    archive_db = _load_archive_db()
    ok_count = 0
    fail_count = 0

    for repo_name in repos:
        repo_data = get_repository(workspace, repo_name)
        if not repo_data:
            print(f"  ✗ {repo_name}: no encontrado")
            fail_count += 1
            continue

        # Check if already archived
        project = repo_data.get('project', {})
        if project.get('key') == ARCHIVE_PROJECT_KEY:
            print(f"  ~ {repo_name}: ya archivado (proyecto {ARCHIVE_PROJECT_KEY})")
            continue

        # Save snapshot before archiving
        snapshot = {
            'name': repo_name,
            'workspace': workspace,
            'project_key': project.get('key', ''),
            'project_name': project.get('name', ''),
            'is_private': repo_data.get('is_private', True),
            'description': repo_data.get('description', ''),
            'archived_at': __import__('datetime').datetime.now().isoformat(),
        }

        # Ensure ARCHIVED project exists
        from bbm.api import upsert_workspace_project
        upsert_workspace_project(workspace, ARCHIVE_PROJECT_KEY, "ARCHIVED — Inactive Repositories",
                                 "Repositorios archivados automáticamente")

        # Mark as archived: set private + move to ARCHIVED project + update description
        new_desc = f"{repo_data.get('description', '')}\n[ARCHIVED: {snapshot['archived_at'][:10]}]"
        ok, err = update_repository(workspace, repo_name, {
            'is_private': True,
            'description': new_desc,
            'project': {'key': ARCHIVE_PROJECT_KEY},
        })

        if ok:
            archive_db.append(snapshot)
            _save_archive_db(archive_db)
            print(f"  ✓ {repo_name}: archivado")
            ok_count += 1
        else:
            print(f"  ✗ {repo_name}: {err}")
            fail_count += 1

    print(f"\n  Resultado: {ok_count} archivados, {fail_count} errores")


def cmd_archive_restore(args):
    _, _, workspace, _ = get_auth()
    if not workspace:
        print("Error: BB_WORKSPACE no está configurado")
        sys.exit(1)

    archive_db = _load_archive_db()
    target_repo = args.repo

    snapshot = None
    for s in archive_db:
        if s['name'] == target_repo and s['workspace'] == workspace:
            snapshot = s
            break

    if not snapshot:
        print(f"  No se encontró registro de archivado para {target_repo}")
        return

    # Check if original project still exists
    project_key = snapshot['project_key']

    ok, err = update_repository(workspace, target_repo, {
        'is_private': snapshot.get('is_private', True),
        'description': snapshot.get('description', '').split('\n[ARCHIVED:')[0],
        'project': {'key': project_key or 'PROJECT'},
    })

    if ok:
        archive_db = [s for s in archive_db if s['name'] != target_repo or s['workspace'] != workspace]
        _save_archive_db(archive_db)
        print(f"  ✓ {target_repo}: restaurado")
    else:
        print(f"  ✗ {target_repo}: {err}")


def cmd_archive_list(args):
    _, _, workspace, _ = get_auth()
    archive_db = _load_archive_db()
    ws_archived = [s for s in archive_db if s['workspace'] == workspace]

    if not ws_archived:
        print(f"  No hay repositorios archivados registrados para {workspace}")
        return

    print(f"\n  Repositorios archivados en {workspace}:\n")
    for s in ws_archived:
        print(f"  ✓ {s['name']} — archivado el {s['archived_at'][:19]}")
        if s.get('project_name'):
            print(f"      proyecto original: {s['project_name']}")


def handle_archive(args):
    if args.action == 'scan':
        cmd_archive_scan(args)
    elif args.action == 'run':
        cmd_archive_run(args)
    elif args.action == 'restore':
        cmd_archive_restore(args)
    elif args.action == 'list':
        cmd_archive_list(args)
