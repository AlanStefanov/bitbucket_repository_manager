import fnmatch
import os
import sys
import yaml

from bbm.api import get_pullrequests, approve_pullrequest
from bbm.config import get_auth

DEFAULT_RULES_PATH = os.path.join(os.path.expanduser("~"), ".bbm", "pr-rules.yml")


def _load_rules(path):
    try:
        with open(path, 'r') as f:
            config = yaml.safe_load(f)
        return config.get('rules', []) if config else []
    except FileNotFoundError:
        return None
    except yaml.YAMLError as e:
        print(f"  Error en el archivo YAML: {e}")
        sys.exit(1)


def _match_rule(pr, rule):
    conditions = rule.get('conditions', {})
    author = pr.get('author', {}).get('nickname', '') or pr.get('author', {}).get('display_name', '')
    source = pr.get('source', {}).get('branch', {}).get('name', '')
    dest = pr.get('destination', {}).get('branch', {}).get('name', '')
    title = pr.get('title', '')
    files_changed = len(pr.get('summary', {}).get('raw', ''))  # approximate

    if 'author' in conditions:
        if not fnmatch.fnmatch(author, conditions['author']):
            return False
    if 'source_branch' in conditions:
        if not fnmatch.fnmatch(source, conditions['source_branch']):
            return False
    if 'target_branch' in conditions:
        if not fnmatch.fnmatch(dest, conditions['target_branch']):
            return False
    if 'title_pattern' in conditions:
        import re
        if not re.search(conditions['title_pattern'], title):
            return False
    if 'max_files_changed' in conditions:
        if pr.get('summary', {}).get('raw', '').count('\n') > conditions['max_files_changed']:
            return False
    return True


def _pr_is_already_approved(pr):
    participants = pr.get('participants', [])
    return any(p.get('approved') for p in participants
               if p.get('user', {}).get('nickname') != 'bbm-auto')


def cmd_auto_approve(args):
    _, _, workspace, _ = get_auth()
    if not workspace:
        print("Error: BB_WORKSPACE no está configurado")
        sys.exit(1)

    rules_path = args.rules or DEFAULT_RULES_PATH
    rules = _load_rules(rules_path)
    if rules is None:
        print(f"  Archivo de reglas no encontrado: {rules_path}")
        print("  Creá uno en ~/.bbm/pr-rules.yml (ver documentación)")
        return

    repos = args.repo if args.repo else None
    if not repos:
        from bbm.api import get_repos
        all_repos = get_repos(workspace)
        repos = [r['name'] for r in all_repos]

    total_approved = 0
    total_skipped = 0
    total_errors = 0

    for repo in repos:
        prs = get_pullrequests(workspace, repo, state='OPEN')
        if prs is None:
            print(f"  ✗ {repo}: no se pudieron obtener PRs")
            total_errors += 1
            continue

        for pr in prs:
            pr_id = pr['id']
            if _pr_is_already_approved(pr):
                total_skipped += 1
                continue

            for rule in rules:
                if not rule.get('enabled', True):
                    continue
                if _match_rule(pr, rule):
                    action = rule.get('action', 'approve')
                    rule_name = rule.get('name', 'unnamed')

                    if args.dry_run:
                        print(f"  [DRY-RUN] {repo}#{pr_id} \"{pr['title'][:50]}\" "
                              f"→ {action} (regla: {rule_name})")
                    else:
                        if action == 'approve':
                            ok, err = approve_pullrequest(workspace, repo, pr_id)
                            if ok:
                                print(f"  ✓ {repo}#{pr_id} \"{pr['title'][:50]}\" → aprobado ({rule_name})")
                                total_approved += 1
                            else:
                                print(f"  ✗ {repo}#{pr_id}: {err}")
                                total_errors += 1
                        elif action == 'comment':
                            print(f"  ~ {repo}#{pr_id}: comentario pendiente ({rule_name})")
                    break

    print(f"\n  Resumen: {total_approved} aprobados, {total_skipped} ya aprobados, {total_errors} errores")


def cmd_rules_list(args):
    rules_path = args.rules or DEFAULT_RULES_PATH
    rules = _load_rules(rules_path)
    if rules is None:
        print(f"  No se encontró archivo de reglas en {rules_path}")
        return
    if not rules:
        print("  No hay reglas configuradas")
        return
    print(f"  Reglas cargadas desde: {rules_path}\n")
    for i, r in enumerate(rules, 1):
        status = '✓' if r.get('enabled', True) else '✗'
        print(f"  {i}. [{status}] {r.get('name', 'sin nombre')}")
        for k, v in r.get('conditions', {}).items():
            print(f"       {k}: {v}")
        print(f"       action: {r.get('action', 'approve')}")
        print()


def cmd_pr_check(args):
    _, _, workspace, _ = get_auth()
    if not workspace:
        print("Error: BB_WORKSPACE no está configurado")
        sys.exit(1)

    rules_path = args.rules or DEFAULT_RULES_PATH
    rules = _load_rules(rules_path)
    if not rules:
        print("  No hay reglas para evaluar")
        return

    prs = get_pullrequests(workspace, args.repo, state='OPEN')
    if not prs:
        print(f"  No se encontró el PR #{args.pr} en {args.repo}")
        return

    for pr in prs:
        if pr['id'] != args.pr:
            continue
        print(f"  PR #{args.pr} en {args.repo}: \"{pr['title']}\"")
        matched = False
        for rule in rules:
            if not rule.get('enabled', True):
                continue
            if _match_rule(pr, rule):
                print(f"    ✓ Matchea regla: {rule.get('name', 'unnamed')} → {rule.get('action', 'approve')}")
                matched = True
        if not matched:
            print("    - No matchea ninguna regla activa")
        return

    print(f"  PR #{args.pr} no encontrado o no está abierto")


def handle_pr(args):
    if args.action == 'auto-approve':
        cmd_auto_approve(args)
    elif args.action == 'rules':
        cmd_rules_list(args)
    elif args.action == 'check':
        cmd_pr_check(args)
