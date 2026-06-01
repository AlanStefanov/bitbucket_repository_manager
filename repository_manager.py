#!/usr/bin/env python3
import subprocess
import os
import requests
import sys
import curses
import time
from datetime import datetime

def load_env_file():
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip())

load_env_file()

USERNAME = os.environ.get("BB_WORKSPACE", "your-workspace")
DEV_DIR = os.environ.get("DEV_DIR", os.path.join(os.path.expanduser("~"), "bitbucket-repos"))
BB_TOKEN = os.environ.get("BB_TOKEN")
BB_AUTH = (os.environ.get("BB_USERNAME"), BB_TOKEN) if BB_TOKEN else (None, None)

def get_repos():
    if not BB_AUTH[1]:
        print("Error: BB_TOKEN no está configurado")
        print("Exporta el token: export BB_TOKEN='tu_token_aqui'")
        return []
    try:
        all_repos = []
        
        repos_url = f"https://api.bitbucket.org/2.0/repositories/{USERNAME}?pagelen=100"
        
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
                    'workspace': USERNAME,
                    'ws_slug': USERNAME,
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
    repo_url = f"git@bitbucket.org:{ws_slug or USERNAME}/{repo_name}.git"
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

def main(stdscr):
    curses.curs_set(0)
    
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
    
if __name__ == "__main__":
    os.environ.setdefault('TERM', 'xterm-256color')
    try:
        curses.wrapper(main)
    except curses.error:
        print("\nError: No se puede inicializar curses en este entorno.")
        print("Ejecuta el script en una terminal interactiva.")
        sys.exit(1)