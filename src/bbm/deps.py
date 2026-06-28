import json
import os
import re
import sys
from collections import defaultdict

from bbm.api import get_repos
from bbm.config import get_auth

CACHE_FILE = os.path.join(os.path.expanduser("~"), ".bbm", "deps-cache.json")


def _load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def _save_cache(cache):
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)


def _find_references_in_file(filepath, repo_names):
    refs = defaultdict(list)
    try:
        with open(filepath, 'r', errors='ignore') as f:
            content = f.read()
    except (OSError, UnicodeDecodeError):
        return refs

    for name in repo_names:
        patterns = [
            rf'from\s+{re.escape(name)}\s+import',
            rf'import\s+{re.escape(name)}',
            rf'bitbucket\.org/[^/]+/{re.escape(name)}',
            rf'\"@{re.escape(name)}/',
            rf"'{re.escape(name)}'",
            rf'"{re.escape(name)}"',
            rf'require\([\'\"]{re.escape(name)}[\'\"]\)',
        ]
        for p in patterns:
            matches = re.finditer(p, content)
            for m in matches:
                line_num = content[:m.start()].count('\n') + 1
                refs[name].append(f"{os.path.basename(filepath)}:{line_num}")
    return refs


def _scan_repo_deps(repo_name, dev_dir, all_repo_names):
    repo_path = os.path.join(dev_dir, repo_name)
    if not os.path.isdir(repo_path) or not os.path.isdir(os.path.join(repo_path, '.git')):
        return None

    deps = defaultdict(list)
    src_extensions = ('.py', '.js', '.ts', '.tsx', '.jsx', '.yml', '.yaml', '.json',
                      '.md', '.cfg', '.ini', '.txt', '.toml', '.cfg', '.sh')

    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in ('.git', '__pycache__', 'node_modules', '.venv', 'venv')]
        for fname in files:
            if fname.endswith(src_extensions):
                fpath = os.path.join(root, fname)
                refs = _find_references_in_file(fpath, all_repo_names)
                for target, locations in refs.items():
                    if target != repo_name:
                        deps[target].extend(locations)

    return dict(deps)


def cmd_deps_scan(args):
    _, _, workspace, _ = get_auth()
    dev_dir = os.environ.get("DEV_DIR", os.path.join(os.path.expanduser("~"), "bitbucket-repos"))

    all_repos = get_repos(workspace)
    if not all_repos:
        print("  No se pudieron obtener los repositorios")
        return

    all_names = [r['name'] for r in all_repos]

    if args.all:
        targets = all_names
    elif args.repo:
        targets = args.repo
    else:
        print("  Especificá --repo o --all")
        return

    cache = _load_cache() if not args.refresh else {}

    for repo_name in targets:
        if repo_name not in all_names:
            print(f"  ✗ {repo_name}: no encontrado en el workspace")
            continue

        if repo_name in cache:
            deps = cache[repo_name]
        else:
            deps = _scan_repo_deps(repo_name, dev_dir, all_names)
            if deps is None:
                print(f"  ~ {repo_name}: no clonado localmente, no se puede escanear")
                continue
            cache[repo_name] = deps
            _save_cache(cache)

        print(f"\n  Dependencias de {repo_name}:")
        if deps:
            for target, locations in sorted(deps.items()):
                locs = ', '.join(locations[:3])
                rest = f" (+{len(locations)-3} más)" if len(locations) > 3 else ""
                print(f"    → {target} ({locs}{rest})")
        else:
            print("    (sin dependencias internas detectadas)")

    _save_cache(cache)


def cmd_deps_tree(args):
    _, _, workspace, _ = get_auth()
    dev_dir = os.environ.get("DEV_DIR", os.path.join(os.path.expanduser("~"), "bitbucket-repos"))
    all_repos = get_repos(workspace)
    all_names = [r['name'] for r in all_repos]
    cache = _load_cache()

    repo_name = args.repo
    if repo_name not in all_names:
        print(f"  {repo_name}: no encontrado")
        return

    if repo_name not in cache:
        deps = _scan_repo_deps(repo_name, dev_dir, all_names)
        if deps is None:
            print(f"  {repo_name}: no clonado localmente")
            return
        cache[repo_name] = deps
        _save_cache(cache)
    else:
        deps = cache[repo_name]

    def _print_tree(node, indent=0, visited=None):
        if visited is None:
            visited = set()
        if node in visited:
            print(" " * indent + "  ↻ (ciclo)")
            return
        visited.add(node)
        node_deps = cache.get(node, {})
        for dep in sorted(node_deps.keys())[:10]:
            print(" " * (indent + 2) + f"└─ {dep}")
            _print_tree(dep, indent + 4, visited.copy())

    print(f"\n  Árbol de dependencias de {repo_name}:")
    print(f"  {'='*40}")
    if deps:
        for dep in sorted(deps.keys())[:10]:
            print(f"  └─ {dep}")
            _print_tree(dep, 2)
        if len(deps) > 10:
            print(f"  ... y {len(deps) - 10} más")
    else:
        print("  (sin dependencias)")


def cmd_deps_orphans(args):
    _, _, workspace, _ = get_auth()
    dev_dir = os.environ.get("DEV_DIR", os.path.join(os.path.expanduser("~"), "bitbucket-repos"))
    all_repos = get_repos(workspace)
    all_names = [r['name'] for r in all_repos]
    cache = _load_cache()

    # Scan any unscanned repos
    for name in all_names:
        if name not in cache:
            deps = _scan_repo_deps(name, dev_dir, all_names)
            if deps is not None:
                cache[name] = deps

    _save_cache(cache)

    # Build dependency graph
    depends_on = defaultdict(set)  # repo → repos it depends on
    depended_by = defaultdict(set)  # repo → repos that depend on it

    for name, deps in cache.items():
        for dep in deps:
            depends_on[name].add(dep)
            depended_by[dep].add(name)

    orphans = [n for n in all_names
               if n not in depends_on and n not in depended_by]

    if orphans:
        print(f"\n  Repositorios huérfanos (sin dependencias entrantes ni salientes):\n")
        for o in orphans:
            print(f"    - {o}")
    else:
        print("  No se detectaron repositorios huérfanos")


def cmd_deps_cycles(args):
    _, _, workspace, _ = get_auth()
    dev_dir = os.environ.get("DEV_DIR", os.path.join(os.path.expanduser("~"), "bitbucket-repos"))
    all_repos = get_repos(workspace)
    all_names = [r['name'] for r in all_repos]
    cache = _load_cache()

    for name in all_names:
        if name not in cache:
            deps = _scan_repo_deps(name, dev_dir, all_names)
            if deps is not None:
                cache[name] = deps
    _save_cache(cache)

    graph = {}
    for name in all_names:
        graph[name] = list(cache.get(name, {}).keys())

    cycles_found = []

    def _dfs(start, current, visited, path):
        visited.add(current)
        path.append(current)
        for neighbor in graph.get(current, []):
            if neighbor in all_names:
                if neighbor not in visited:
                    if _dfs(start, neighbor, visited, path):
                        return True
                elif neighbor == start and len(path) > 2:
                    cycles_found.append(path[:])
                    return True
        path.pop()
        return False

    for name in all_names:
        _dfs(name, name, set(), [])

    if cycles_found:
        print(f"\n  Dependencias circulares detectadas:\n")
        seen = set()
        for cycle in cycles_found:
            key = tuple(sorted(cycle))
            if key not in seen:
                seen.add(key)
                print(f"    ↻ {' → '.join(cycle)} → {cycle[0]}")
    else:
        print("  No se detectaron dependencias circulares")


def cmd_deps_impact(args):
    _, _, workspace, _ = get_auth()
    dev_dir = os.environ.get("DEV_DIR", os.path.join(os.path.expanduser("~"), "bitbucket-repos"))
    all_repos = get_repos(workspace)
    all_names = [r['name'] for r in all_repos]
    cache = _load_cache()

    repo_name = args.repo
    if repo_name not in all_names:
        print(f"  {repo_name}: no encontrado")
        return

    if repo_name not in cache:
        deps = _scan_repo_deps(repo_name, dev_dir, all_names)
        if deps is None:
            print(f"  {repo_name}: no clonado localmente")
            return
        cache[repo_name] = deps
        _save_cache(cache)

    deps = cache.get(repo_name, {})

    # Find who depends on this repo
    reverse_deps = defaultdict(list)
    for name, deps_dict in cache.items():
        if repo_name in deps_dict:
            reverse_deps[name].extend(deps_dict[repo_name])

    n_imports = sum(len(locs) for locs in reverse_deps.values())

    print(f"\n  Impacto de migrar/archivar '{repo_name}':\n")
    if deps:
        print(f"  Depende de {len(deps)} repositorio(s):")
        for target, locs in sorted(deps.items())[:10]:
            print(f"    → {target} ({', '.join(locs[:2])})")
        if len(deps) > 10:
            print(f"    ... y {len(deps) - 10} más")
    else:
        print(f"  Depende de: (ninguno)")

    print()
    if reverse_deps:
        print(f"  Es dependencia de {len(reverse_deps)} repositorio(s) ({n_imports} imports):")
        for source, locs in sorted(reverse_deps.items()):
            print(f"    ← {source} ({', '.join(locs[:2])})")
    else:
        print(f"  Es dependencia de: (ninguno)")

    print(f"\n  {'⚠' if reverse_deps else '✓'} Si se migra/archiva: "
          f"{len(reverse_deps)} repos afectados, {n_imports} imports rotos")


def handle_deps(args):
    if args.action == 'scan':
        cmd_deps_scan(args)
    elif args.action == 'tree':
        cmd_deps_tree(args)
    elif args.action == 'orphans':
        cmd_deps_orphans(args)
    elif args.action == 'cycles':
        cmd_deps_cycles(args)
    elif args.action == 'impact':
        cmd_deps_impact(args)
