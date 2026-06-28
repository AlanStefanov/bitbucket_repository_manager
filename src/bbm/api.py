import os
import subprocess
import requests
from datetime import datetime

from bbm.config import get_auth, load_env_file

load_env_file()

BASE_URL = "https://api.bitbucket.org/2.0"

def _auth():
    token, username, _ = get_auth()
    if not token or not username:
        return None
    return (username, token)

def get_repos(workspace=None):
    auth = _auth()
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
        repos_url = f"{BASE_URL}/repositories/{workspace}?pagelen=100"

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
                    updated_dt = datetime.min
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

def get_permissions_users(workspace, repo):
    auth = _auth()
    if not auth:
        return None
    url = f"{BASE_URL}/repositories/{workspace}/{repo}/permissions-config/users"
    try:
        r = requests.get(url, auth=auth, timeout=10)
        if r.status_code == 200:
            return r.json().get('values', [])
        print(f"  Error al obtener permisos de usuarios: {r.status_code}")
        return None
    except Exception as e:
        print(f"  Error de conexión: {e}")
        return None

def get_permissions_groups(workspace, repo):
    auth = _auth()
    if not auth:
        return None
    url = f"{BASE_URL}/repositories/{workspace}/{repo}/permissions-config/groups"
    try:
        r = requests.get(url, auth=auth, timeout=10)
        if r.status_code == 200:
            return r.json().get('values', [])
        print(f"  Error al obtener permisos de grupos: {r.status_code}")
        return None
    except Exception as e:
        print(f"  Error de conexión: {e}")
        return None

def set_user_permission(workspace, repo, user, permission):
    auth = _auth()
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
    auth = _auth()
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
    auth = _auth()
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
    auth = _auth()
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
