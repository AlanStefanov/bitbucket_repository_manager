import os
import subprocess
import requests
from datetime import datetime, timezone

from bitbucket_manager.config import get_auth, load_env_file

load_env_file()

BASE_URL = "https://api.bitbucket.org/2.0"


def _http_auth():
    token, username, _ = get_auth()
    if not token or not username:
        return None
    return (username, token)

def get_repos(workspace=None):
    auth = _http_auth()
    if not auth:
        print("Error: credenciales no configuradas")
        return []

    _, _, ws = get_auth()
    workspace = workspace or ws
    if not workspace:
        print("Error: BB_WORKSPACE no está configurado")
        return []

    dev_dir = os.environ.get("DEV_DIR", os.path.join(os.path.expanduser("~"), "bitbucket-repos"))
    try:
        all_repos = []
        repos_url = f"{BASE_URL}/repositories/{workspace}?pagelen=100&role=member"

        while repos_url:
            response = requests.get(repos_url, auth=auth, timeout=10)
            if response.status_code != 200:
                print(f"Error: {response.status_code}")
                break
            data = response.json()
            for repo in data.get('values', []):
                updated = repo.get('updated_on', '')
                try:
                    updated_dt = datetime.fromisoformat(updated.replace('Z', '+00:00'))
                except Exception:
                    updated_dt = datetime.min.replace(tzinfo=timezone.utc)
                all_repos.append({
                    'name': repo['name'],
                    'url': repo['links']['html']['href'],
                    'workspace': workspace,
                    'ws_slug': workspace,
                    'updated': updated_dt,
                    'updated_str': updated[:10] if updated else 'N/A',
                    'cloned': _is_cloned(repo['name'], dev_dir),
                })
            repos_url = data.get('next')

        all_repos.sort(key=lambda x: x['updated'], reverse=True)
        return all_repos
    except Exception as e:
        print(f"Error de conexión: {e}")
        return []

def _is_cloned(repo_name, dev_dir):
    target = os.path.join(dev_dir, repo_name)
    return os.path.exists(target) and os.path.isdir(os.path.join(target, '.git'))

def clone_repo(repo_name, workspace=None):
    _, _, ws = get_auth()
    workspace = workspace or ws
    dev_dir = os.environ.get("DEV_DIR", os.path.join(os.path.expanduser("~"), "bitbucket-repos"))
    repo_url = f"git@bitbucket.org:{workspace}/{repo_name}.git"
    target_dir = os.path.join(dev_dir, repo_name)

    if os.path.exists(target_dir):
        return False, f"El directorio {target_dir} ya existe"

    try:
        os.makedirs(dev_dir, exist_ok=True)
        result = subprocess.run(['git', 'clone', repo_url, target_dir],
                                capture_output=True, text=True)
        if result.returncode == 0:
            subprocess.run(['git', 'config', 'user.name',
                           os.environ.get('GIT_USER_NAME', 'Your Name')], cwd=target_dir)
            subprocess.run(['git', 'config', 'user.email',
                           os.environ.get('GIT_USER_EMAIL', 'your-email@example.com')], cwd=target_dir)
            return True, f"Repositorio clonado en: {target_dir}"
        return False, result.stderr
    except Exception as e:
        return False, str(e)


def pull_repo(repo_name, workspace=None):
    _, _, ws = get_auth()
    workspace = workspace or ws
    dev_dir = os.environ.get("DEV_DIR", os.path.join(os.path.expanduser("~"), "bitbucket-repos"))
    target_dir = os.path.join(dev_dir, repo_name)

    if not os.path.isdir(os.path.join(target_dir, '.git')):
        return False, f"{repo_name} no está clonado en {target_dir}"

    try:
        result = subprocess.run(['git', '-C', target_dir, 'pull'],
                                capture_output=True, text=True)
        if result.returncode == 0:
            return True, result.stdout.strip() or "Pull exitoso"
        return False, result.stderr
    except Exception as e:
        return False, str(e)


def get_repo_branches(repo_name):
    dev_dir = os.environ.get("DEV_DIR", os.path.join(os.path.expanduser("~"), "bitbucket-repos"))
    target_dir = os.path.join(dev_dir, repo_name)

    if not os.path.isdir(os.path.join(target_dir, '.git')):
        return None

    try:
        result = subprocess.run(['git', '-C', target_dir, 'branch', '-a'],
                                capture_output=True, text=True)
        if result.returncode != 0:
            return None
        branches = []
        for line in result.stdout.strip().split("\n"):
            line = line.strip()
            if not line or line.startswith("HEAD") or "HEAD ->" in line:
                continue
            if line.startswith("* "):
                branches.append(line[2:].strip())
            elif line.startswith("remotes/origin/"):
                b = line.replace("remotes/origin/", "").strip()
                if b and b not in branches and b != "HEAD":
                    branches.append(b)
            else:
                b = line.strip()
                if b and b not in branches:
                    branches.append(b)
        return branches
    except Exception:
        return None


def checkout_repo(repo_name, branch):
    dev_dir = os.environ.get("DEV_DIR", os.path.join(os.path.expanduser("~"), "bitbucket-repos"))
    target_dir = os.path.join(dev_dir, repo_name)

    if not os.path.isdir(os.path.join(target_dir, '.git')):
        return False, f"{repo_name} no está clonado"

    try:
        result = subprocess.run(['git', '-C', target_dir, 'checkout', branch],
                                capture_output=True, text=True)
        if result.returncode == 0:
            return True, f"Checkout a '{branch}' exitoso"
        return False, result.stderr
    except Exception as e:
        return False, str(e)

def get_permissions_users(workspace, repo):
    auth = _http_auth()
    if not auth:
        return None
    url = f"{BASE_URL}/repositories/{workspace}/{repo}/permissions-config/users"
    try:
        r = requests.get(url, auth=auth, timeout=10)
        if r.status_code == 200:
            return r.json().get('values', [])
        if r.status_code in (401, 403):
            return []  # No tenemos permiso de admin en este repo; no es un error fatal
        print(f"  Error al obtener permisos de usuarios: {r.status_code}")
        return None
    except Exception as e:
        print(f"  Error de conexión: {e}")
        return None

def get_permissions_groups(workspace, repo):
    auth = _http_auth()
    if not auth:
        return None
    url = f"{BASE_URL}/repositories/{workspace}/{repo}/permissions-config/groups"
    try:
        r = requests.get(url, auth=auth, timeout=10)
        if r.status_code == 200:
            return r.json().get('values', [])
        if r.status_code in (401, 403):
            return []  # No tenemos permiso de admin en este repo
        print(f"  Error al obtener permisos de grupos: {r.status_code}")
        return None
    except Exception as e:
        print(f"  Error de conexión: {e}")
        return None

def set_user_permission(workspace, repo, user, permission):
    auth = _http_auth()
    if not auth:
        return False, "Credenciales no configuradas"
    url = f"{BASE_URL}/repositories/{workspace}/{repo}/permissions-config/users/{user}"
    try:
        r = requests.put(url, auth=auth, json={"permission": permission.lower()}, timeout=10)
        if r.status_code in (200, 201, 204):
            return True, None
        return False, f"HTTP {r.status_code}: {r.text[:200]}"
    except Exception as e:
        return False, str(e)

def delete_user_permission(workspace, repo, user):
    auth = _http_auth()
    if not auth:
        return False, "Credenciales no configuradas"
    url = f"{BASE_URL}/repositories/{workspace}/{repo}/permissions-config/users/{user}"
    try:
        r = requests.delete(url, auth=auth, timeout=10)
        if r.status_code in (200, 204):
            return True, None
        return False, f"HTTP {r.status_code}: {r.text[:200]}"
    except Exception as e:
        return False, str(e)

def set_group_permission(workspace, repo, group, permission):
    auth = _http_auth()
    if not auth:
        return False, "Credenciales no configuradas"
    url = f"{BASE_URL}/repositories/{workspace}/{repo}/permissions-config/groups/{group}"
    try:
        r = requests.put(url, auth=auth, json={"permission": permission.lower()}, timeout=10)
        if r.status_code in (200, 201, 204):
            return True, None
        return False, f"HTTP {r.status_code}: {r.text[:200]}"
    except Exception as e:
        return False, str(e)

def delete_group_permission(workspace, repo, group):
    auth = _http_auth()
    if not auth:
        return False, "Credenciales no configuradas"
    url = f"{BASE_URL}/repositories/{workspace}/{repo}/permissions-config/groups/{group}"
    try:
        r = requests.delete(url, auth=auth, timeout=10)
        if r.status_code in (200, 204):
            return True, None
        return False, f"HTTP {r.status_code}: {r.text[:200]}"
    except Exception as e:
        return False, str(e)


# ─── PRs ────────────────────────────────────────────────────────────────────

def get_pullrequests(workspace, repo, state='OPEN', limit=50):
    auth = _http_auth()
    if not auth:
        return None
    url = f"{BASE_URL}/repositories/{workspace}/{repo}/pullrequests?state={state}&pagelen={limit}"
    try:
        r = requests.get(url, auth=auth, timeout=10)
        if r.status_code == 200:
            return r.json().get('values', [])
        if r.status_code == 403:
            print(f"  PRs 403 en {repo}: verificá que el token tenga scope 'pullrequest'")
            return None
        print(f"  Error al obtener PRs: {r.status_code}")
        return None
    except Exception as e:
        print(f"  Error de conexión: {e}")
        return None


def approve_pullrequest(workspace, repo, pr_id):
    auth = _http_auth()
    if not auth:
        return False, "Credenciales no configuradas"
    url = f"{BASE_URL}/repositories/{workspace}/{repo}/pullrequests/{pr_id}/approve"
    try:
        r = requests.post(url, auth=auth, timeout=10)
        if r.status_code in (200, 201, 204):
            return True, None
        return False, f"HTTP {r.status_code}: {r.text[:200]}"
    except Exception as e:
        return False, str(e)


def unapprove_pullrequest(workspace, repo, pr_id):
    auth = _http_auth()
    if not auth:
        return False, "Credenciales no configuradas"
    url = f"{BASE_URL}/repositories/{workspace}/{repo}/pullrequests/{pr_id}/approve"
    try:
        r = requests.delete(url, auth=auth, timeout=10)
        if r.status_code in (200, 204):
            return True, None
        return False, f"HTTP {r.status_code}: {r.text[:200]}"
    except Exception as e:
        return False, str(e)


def get_branches(workspace, repo, limit=100):
    auth = _http_auth()
    if not auth:
        return None
    url = f"{BASE_URL}/repositories/{workspace}/{repo}/refs/branches?pagelen={limit}"
    try:
        r = requests.get(url, auth=auth, timeout=10)
        if r.status_code == 200:
            return r.json().get('values', [])
        print(f"  Error al obtener branches: {r.status_code}")
        return None
    except Exception as e:
        print(f"  Error de conexión: {e}")
        return None


def create_repository(workspace, repo_name, is_private=True):
    auth = _http_auth()
    if not auth:
        return False, "Credenciales no configuradas"
    url = f"{BASE_URL}/repositories/{workspace}/{repo_name}"
    try:
        r = requests.post(url, auth=auth,
                          json={"scm": "git", "is_private": is_private}, timeout=15)
        if r.status_code in (200, 201):
            return True, r.json()
        return False, f"HTTP {r.status_code}: {r.text[:200]}"
    except Exception as e:
        return False, str(e)


def update_repository(workspace, repo, data):
    auth = _http_auth()
    if not auth:
        return False, "Credenciales no configuradas"
    url = f"{BASE_URL}/repositories/{workspace}/{repo}"
    try:
        r = requests.put(url, auth=auth, json=data, timeout=10)
        if r.status_code == 200:
            return True, None
        return False, f"HTTP {r.status_code}: {r.text[:200]}"
    except Exception as e:
        return False, str(e)


def get_workspace_projects(workspace):
    auth = _http_auth()
    if not auth:
        return None
    url = f"{BASE_URL}/workspaces/{workspace}/projects"
    try:
        r = requests.get(url, auth=auth, timeout=10)
        if r.status_code == 200:
            return r.json().get('values', [])
        print(f"  Error al obtener proyectos: {r.status_code}")
        return None
    except Exception as e:
        print(f"  Error de conexión: {e}")
        return None


def upsert_workspace_project(workspace, project_key, name, description=""):
    auth = _http_auth()
    if not auth:
        return None
    url = f"{BASE_URL}/workspaces/{workspace}/projects/{project_key}"
    try:
        r = requests.put(url, auth=auth,
                         json={"name": name, "key": project_key, "description": description},
                         timeout=10)
        if r.status_code in (200, 201):
            return r.json()
        print(f"  Error al crear/actualizar proyecto: {r.status_code}")
        return None
    except Exception as e:
        print(f"  Error de conexión: {e}")
        return None


# ─── Groups ──────────────────────────────────────────────────────────────────

def get_workspace_groups(workspace):
    auth = _http_auth()
    if not auth:
        return None
    url = f"{BASE_URL}/workspaces/{workspace}/groups"
    try:
        r = requests.get(url, auth=auth, timeout=10)
        if r.status_code == 200:
            return r.json().get('values', [])
        print(f"  Error al obtener grupos: {r.status_code}")
        return None
    except Exception as e:
        print(f"  Error de conexión: {e}")
        return None


def create_workspace_group(workspace, name):
    auth = _http_auth()
    if not auth:
        return False, "Credenciales no configuradas"
    url = f"{BASE_URL}/workspaces/{workspace}/groups"
    try:
        r = requests.post(url, auth=auth, json={"name": name}, timeout=10)
        if r.status_code in (200, 201):
            return True, r.json()
        return False, f"HTTP {r.status_code}: {r.text[:200]}"
    except Exception as e:
        return False, str(e)


def delete_workspace_group(workspace, group_slug):
    auth = _http_auth()
    if not auth:
        return False, "Credenciales no configuradas"
    url = f"{BASE_URL}/workspaces/{workspace}/groups/{group_slug}"
    try:
        r = requests.delete(url, auth=auth, timeout=10)
        if r.status_code in (200, 204):
            return True, None
        return False, f"HTTP {r.status_code}: {r.text[:200]}"
    except Exception as e:
        return False, str(e)


def get_group_members(workspace, group_slug):
    auth = _http_auth()
    if not auth:
        return None
    url = f"{BASE_URL}/workspaces/{workspace}/groups/{group_slug}/members"
    try:
        r = requests.get(url, auth=auth, timeout=10)
        if r.status_code == 200:
            return r.json().get('values', [])
        print(f"  Error al obtener miembros del grupo: {r.status_code}")
        return None
    except Exception as e:
        print(f"  Error de conexión: {e}")
        return None


def add_group_member(workspace, group_slug, member):
    auth = _http_auth()
    if not auth:
        return False, "Credenciales no configuradas"
    url = f"{BASE_URL}/workspaces/{workspace}/groups/{group_slug}/members/{member}"
    try:
        r = requests.put(url, auth=auth, timeout=10)
        if r.status_code in (200, 201, 204):
            return True, None
        return False, f"HTTP {r.status_code}: {r.text[:200]}"
    except Exception as e:
        return False, str(e)


def remove_group_member(workspace, group_slug, member):
    auth = _http_auth()
    if not auth:
        return False, "Credenciales no configuradas"
    url = f"{BASE_URL}/workspaces/{workspace}/groups/{group_slug}/members/{member}"
    try:
        r = requests.delete(url, auth=auth, timeout=10)
        if r.status_code in (200, 204):
            return True, None
        return False, f"HTTP {r.status_code}: {r.text[:200]}"
    except Exception as e:
        return False, str(e)


# ─── Members ─────────────────────────────────────────────────────────────────

def get_workspace_members(workspace):
    auth = _http_auth()
    if not auth:
        return None
    url = f"{BASE_URL}/workspaces/{workspace}/members"
    try:
        r = requests.get(url, auth=auth, timeout=10)
        if r.status_code == 200:
            return r.json().get('values', [])
        print(f"  Error al obtener miembros del workspace: {r.status_code}")
        return None
    except Exception as e:
        print(f"  Error de conexión: {e}")
        return None


def get_repository(workspace, repo):
    auth = _http_auth()
    if not auth:
        return None
    url = f"{BASE_URL}/repositories/{workspace}/{repo}"
    try:
        r = requests.get(url, auth=auth, timeout=10)
        if r.status_code == 200:
            return r.json()
        return None
    except Exception as e:
        print(f"  Error de conexión: {e}")
        return None
