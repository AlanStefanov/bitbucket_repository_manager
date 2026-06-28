import os
import curses

from bbm.api import get_repos, clone_repo
from bbm.config import validate_env, load_env_file

load_env_file()

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
            stdscr.addstr(row, 0, " > ", curses.A_REVERSE)
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


def run_tui(stdscr):
    curses.curs_set(0)

    print("Cargando repositorios de Bitbucket...")
    repos = get_repos()

    if not repos:
        print("No se pudieron obtener los repositorios.")
        return

    dev_dir = os.environ.get("DEV_DIR", os.path.join(os.path.expanduser("~"), "bitbucket-repos"))
    cloned_status = [
        os.path.exists(os.path.join(dev_dir, r['name'])) and
        os.path.isdir(os.path.join(dev_dir, r['name'], '.git'))
        for r in repos
    ]
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
                filtered_cloned = [
                    os.path.exists(os.path.join(dev_dir, r['name'])) and
                    os.path.isdir(os.path.join(dev_dir, r['name'], '.git'))
                    for r in filtered_repos
                ]
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
            cloned_status = [
                os.path.exists(os.path.join(dev_dir, r['name'])) and
                os.path.isdir(os.path.join(dev_dir, r['name'], '.git'))
                for r in repos
            ]
            if search_query:
                filtered_repos = [r for r in repos if search_query in r['name'].lower()]
                filtered_cloned = [
                    os.path.exists(os.path.join(dev_dir, r['name'])) and
                    os.path.isdir(os.path.join(dev_dir, r['name'], '.git'))
                    for r in filtered_repos
                ]
            else:
                filtered_repos = repos
                filtered_cloned = cloned_status
            selected = 0
        elif key == ord('\n'):
            repo = filtered_repos[selected]
            if filtered_cloned[selected]:
                draw_menu(stdscr, filtered_repos, selected, filtered_cloned, search_query)
                msg = f"El repositorio ya está clonado en: {os.path.join(dev_dir, repo['name'])}"
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


def main():
    os.environ.setdefault('TERM', 'xterm-256color')
    errors = validate_env()
    if errors:
        for e in errors:
            print(f"Error: {e}")
        return
    try:
        curses.wrapper(run_tui)
    except curses.error:
        print("\nError: No se puede inicializar curses en este entorno.")
        print("Ejecutá el script en una terminal interactiva.")
    except KeyboardInterrupt:
        pass
