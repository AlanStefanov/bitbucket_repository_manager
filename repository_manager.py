#!/usr/bin/env python3
VERSION = "1.0.0"
import subprocess
import os
import requests
import sys
import curses
import time
from datetime import datetime

CONFIG_DIR = os.path.expanduser("~/.config/bbm")
CONFIG_FILE = os.path.join(CONFIG_DIR, "env")

def _load_env_file():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip())
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip())

def _set_config():
    global BB_WORKSPACE, DEV_DIR, BB_TOKEN, BB_AUTH
    BB_WORKSPACE = os.environ.get("BB_WORKSPACE")
    DEV_DIR = os.environ.get("DEV_DIR", os.path.join(os.path.expanduser("~"), "bitbucket-repos"))
    BB_TOKEN = os.environ.get("BB_TOKEN")
    BB_AUTH = (os.environ.get("BB_USERNAME"), BB_TOKEN) if BB_TOKEN else (None, None)

_load_env_file()
_set_config()

def get_repos():
    if not BB_AUTH[1]:
        print("Error: BB_TOKEN no está configurado")
        print("Exporta el token: export BB_TOKEN='tu_token_aqui'")
        return []
    if not BB_AUTH[0]:
        print("Error: BB_USERNAME no está configurado")
        print("Defínelo en .env o via export: export BB_USERNAME='tu-email@example.com'")
        return []
    if not BB_WORKSPACE:
        print("Error: BB_WORKSPACE no está configurado")
        print("Defínelo en .env o via export: export BB_WORKSPACE='mi-workspace'")
        return []
    try:
        all_repos = []
        
        repos_url = f"https://api.bitbucket.org/2.0/repositories/{BB_WORKSPACE}?pagelen=100"
        
        while repos_url:
            response = requests.get(repos_url, auth=BB_AUTH, timeout=10)
            if response.status_code != 200:
                print(f"Error: {response.status_code}")
                break
            data = response.json()
            for repo in data.get('values', []):
                updated = repo.get('updated_on', '')
                try:
                    updated_dt = datetime.fromisoformat(updated.replace('Z', '+00:00'))
                except:
                    updated_dt = datetime.min
                all_repos.append({
                    'name': repo['name'],
                    'url': repo['links']['html']['href'],
                    'workspace': BB_WORKSPACE,
                    'ws_slug': BB_WORKSPACE,
                    'updated': updated_dt,
                    'updated_str': updated[:10] if updated else 'N/A'
                })
            repos_url = data.get('next')
        
        all_repos.sort(key=lambda x: x['updated'], reverse=True)
        print(f"Cargados {len(all_repos)} repositorios")
        return all_repos
    except Exception as e:
        print(f"Error de conexión: {e}")
        return []

def is_cloned(repo_name):
    target_dir = os.path.join(DEV_DIR, repo_name)
    return os.path.exists(target_dir) and os.path.isdir(os.path.join(target_dir, '.git'))

def clone_repo(repo_name, ws_slug=None):
    repo_url = f"git@bitbucket.org:{ws_slug or BB_WORKSPACE}/{repo_name}.git"
    target_dir = os.path.join(DEV_DIR, repo_name)
    
    if os.path.exists(target_dir):
        return False, f"El directorio {target_dir} ya existe"
    
    try:
        os.makedirs(DEV_DIR, exist_ok=True)
        result = subprocess.run(['git', 'clone', repo_url, target_dir], 
                                capture_output=True, text=True)
        if result.returncode == 0:
            subprocess.run(['git', 'config', 'user.name', os.environ.get('GIT_USER_NAME', 'Your Name')], cwd=target_dir)
            subprocess.run(['git', 'config', 'user.email', os.environ.get('GIT_USER_EMAIL', 'your-email@example.com')], cwd=target_dir)
            return True, f"Repositorio clonado en: {target_dir}"
        return False, result.stderr
    except Exception as e:
        return False, str(e)

def draw_menu(stdscr, repos, selected, cloned_status, search_query=""):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    
    title = "REPOSITORY MANAGER - Bitbucket"
    stdscr.addstr(0, (w - len(title)) // 2, title, curses.A_BOLD)
    stdscr.addstr(1, 0, "=" * (w - 1))
    stdscr.addstr(2, 0, f"{'#':<3} {'Nombre':<30} {'Proyecto':<22} {'Última act.':<10} {'Estado':<8}")
    stdscr.addstr(3, 0, "-" * (w - 1))
    
    for i, repo in enumerate(repos):
        if i >= h - 6:
            break
        row = 4 + i
        if row < 0:
            continue
        name = repo['name'][:30]
        workspace = repo.get('workspace', '')[:22]
        updated = repo['updated_str']
        status = "[OK]" if cloned_status[i] else ""
        
        if i == selected:
            stdscr.addstr(row, 0, f" > ", curses.A_REVERSE)
            stdscr.addstr(row, 3, f"{name:<30}", curses.A_REVERSE)
            stdscr.addstr(row, 34, f"{workspace:<22}", curses.A_REVERSE)
            stdscr.addstr(row, 57, f"{updated:<10}", curses.A_REVERSE)
            stdscr.addstr(row, 68, f"{status:<8}", curses.A_REVERSE)
        else:
            stdscr.addstr(row, 0, f"{i+1:<3} {name:<30} {workspace:<22} {updated:<10} {status:<8}")
    
    stdscr.addstr(h-3, 0, "-" * (w - 1))
    if search_query:
        stdscr.addstr(h-2, 0, f"Buscar: {search_query}" + " " * (w - len(search_query) - 10))
        stdscr.addstr(h-2, w - 15, "ESC: Salir", curses.A_DIM)
    else:
        stdscr.addstr(h-2, 0, "↑↓ Navegar  ENTER: Ver/Clonar  /: Buscar  R: Refrescar  Q: Salir")
    stdscr.refresh()

def search_repos(stdscr, repos):
    search_query = ""
    curses.curs_set(1)
    h, w = stdscr.getmaxyx()
    
    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "BUSCAR REPOSITORIO", curses.A_BOLD)
        stdscr.addstr(1, 0, "=" * (w - 1))
        stdscr.addstr(3, 0, "Buscar: " + search_query)
        stdscr.addstr(5, 0, f"Resultados: {len(search_query)} caracteres")
        
        stdscr.addstr(h-2, 0, "ESC: Cancelar  ENTER: Buscar")
        stdscr.move(3, 9 + len(search_query))
        stdscr.refresh()
        
        key = stdscr.getch()
        
        if key == 27:
            break
        elif key == 10:
            break
        elif key == curses.KEY_BACKSPACE or key == 127:
            search_query = search_query[:-1]
        elif 32 <= key <= 126:
            search_query += chr(key)
    
    curses.curs_set(0)
    return search_query

def config_screen(stdscr):
    curses.curs_set(1)
    h, w = stdscr.getmaxyx()

    fields = [
        ["BB_TOKEN", "", True],
        ["BB_USERNAME", "", False],
        ["BB_WORKSPACE", "", False],
    ]
    current_field = 0
    in_buttons = False
    button_idx = 0
    buttons = ["Guardar", "Salir"]

    while True:
        stdscr.clear()
        title = "BBM — Configuración Inicial"
        try:
            stdscr.addstr(1, (w - len(title)) // 2, title, curses.A_BOLD)
        except curses.error:
            pass
        try:
            stdscr.addstr(2, 0, "=" * (w - 1))
        except curses.error:
            pass

        for i, (label, value, masked) in enumerate(fields):
            y = 4 + i * 2
            display = "*" * len(value) if masked else value
            label_text = f"{label}: "
            try:
                stdscr.addstr(y, 4, label_text)
                if not in_buttons and i == current_field:
                    stdscr.addstr(y, 4 + len(label_text), f"[{display}]", curses.A_REVERSE)
                else:
                    stdscr.addstr(y, 4 + len(label_text), f"[{display}]")
            except curses.error:
                pass

        for i, btn in enumerate(buttons):
            y = 11
            x = 10 + i * 15
            try:
                if in_buttons and i == button_idx:
                    stdscr.addstr(y, x, f"<{btn}>", curses.A_REVERSE)
                else:
                    stdscr.addstr(y, x, f" {btn} ")
            except curses.error:
                pass

        try:
            stdscr.addstr(h - 2, 2, "Tab: cambiar campo  ↑↓ navegar  Enter: confirmar  Esc: salir")
        except curses.error:
            pass
        stdscr.refresh()

        key = stdscr.getch()

        if key == 9:
            if not in_buttons:
                if current_field < len(fields) - 1:
                    current_field += 1
                else:
                    in_buttons = True
                    button_idx = 0
            else:
                if button_idx < len(buttons) - 1:
                    button_idx += 1
                else:
                    in_buttons = False
                    current_field = 0
        elif key == curses.KEY_UP:
            if in_buttons:
                in_buttons = False
                current_field = len(fields) - 1
            elif current_field > 0:
                current_field -= 1
        elif key == curses.KEY_DOWN:
            if not in_buttons:
                if current_field < len(fields) - 1:
                    current_field += 1
                else:
                    in_buttons = True
                    button_idx = 0
        elif key == 10:
            if in_buttons:
                if button_idx == 0:
                    if all(f[1] for f in fields):
                        os.makedirs(CONFIG_DIR, exist_ok=True)
                        with open(CONFIG_FILE, 'w') as f:
                            for label, value, _ in fields:
                                f.write(f"{label}={value}\n")
                        _load_env_file()
                        _set_config()
                        curses.curs_set(0)
                        return True
                else:
                    curses.curs_set(0)
                    return False
        elif key == 27:
            curses.curs_set(0)
            return False
        elif not in_buttons and current_field < len(fields):
            label, value, masked = fields[current_field]
            if key in (127, curses.KEY_BACKSPACE):
                value = value[:-1]
            elif 32 <= key <= 126:
                if len(value) < 128:
                    value += chr(key)
            fields[current_field] = [label, value, masked]

def main(stdscr):
    curses.curs_set(0)

    if not BB_TOKEN:
        if not config_screen(stdscr):
            return

    print("Cargando repositorios de Bitbucket...")
    repos = get_repos()
    
    if not repos:
        print("No se pudieron obtener los repositorios.")
        return
    
    cloned_status = [is_cloned(r['name']) for r in repos]
    selected = 0
    search_query = ""
    filtered_repos = repos
    filtered_cloned = cloned_status
    
    while True:
        draw_menu(stdscr, filtered_repos, selected, filtered_cloned, search_query)
        key = stdscr.getch()
        
        if key == ord('q') or key == ord('Q'):
            break
        elif key == ord('/'):
            query = search_repos(stdscr, repos)
            if query:
                search_query = query.lower()
                filtered_repos = [r for r in repos if search_query in r['name'].lower()]
                filtered_cloned = [is_cloned(r['name']) for r in filtered_repos]
            else:
                search_query = ""
                filtered_repos = repos
                filtered_cloned = cloned_status
            selected = 0
        elif key == 27:
            search_query = ""
            filtered_repos = repos
            filtered_cloned = cloned_status
            selected = 0
        elif key == ord('r') or key == ord('R'):
            print("\nRefrescando...")
            repos = get_repos()
            cloned_status = [is_cloned(r['name']) for r in repos]
            if search_query:
                filtered_repos = [r for r in repos if search_query in r['name'].lower()]
                filtered_cloned = [is_cloned(r['name']) for r in filtered_repos]
            else:
                filtered_repos = repos
                filtered_cloned = cloned_status
            selected = 0
        elif key == ord('\n'):
            repo = filtered_repos[selected]
            if filtered_cloned[selected]:
                draw_menu(stdscr, filtered_repos, selected, filtered_cloned, search_query)
                msg = f"El repositorio ya está clonado en: {os.path.join(DEV_DIR, repo['name'])}"
                stdscr.addstr(curses.LINES - 1, 0, msg)
                stdscr.getch()
            else:
                draw_menu(stdscr, filtered_repos, selected, filtered_cloned, search_query)
                stdscr.addstr(curses.LINES - 1, 0, f"Clonando {repo['name']}...")
                stdscr.refresh()
                ok, msg = clone_repo(repo['name'], repo.get('ws_slug'))
                filtered_cloned[selected] = True
                original_idx = repos.index(repo)
                cloned_status[original_idx] = True
                draw_menu(stdscr, filtered_repos, selected, filtered_cloned, search_query)
                if ok:
                    stdscr.addstr(curses.LINES - 1, 0, f"✓ {msg}")
                else:
                    stdscr.addstr(curses.LINES - 1, 0, f"✗ Error: {msg}")
                stdscr.getch()
        elif key == curses.KEY_UP:
            selected = max(0, selected - 1)
        elif key == curses.KEY_DOWN:
            selected = min(len(filtered_repos) - 1, selected + 1)
        elif key == ord('j'):
            selected = min(len(filtered_repos) - 1, selected + 1)
        elif key == ord('k'):
            selected = max(0, selected - 1)
    
def cli():
    os.environ.setdefault('TERM', 'xterm-256color')
    try:
        curses.wrapper(main)
    except curses.error:
        print("\nError: No se puede inicializar curses en este entorno.")
        print("Ejecuta el script en una terminal interactiva.")
        sys.exit(1)

if __name__ == "__main__":
    cli()