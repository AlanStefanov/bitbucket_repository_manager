import os

def load_env_file():
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '.env')
    alt_path = os.path.join(os.path.expanduser("~"), ".bbm", ".env")
    for path in [env_path, alt_path]:
        if os.path.exists(path):
            with open(path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ.setdefault(key.strip(), value.strip())

def get_auth():
    token = os.environ.get("BB_TOKEN")
    username = os.environ.get("BB_USERNAME")
    workspace = os.environ.get("BB_WORKSPACE")
    auth_type = os.environ.get("BB_AUTH_TYPE", "auto")
    return token, username, workspace, auth_type

def validate_env():
    token, username, workspace, auth_type = get_auth()
    errors = []
    if not token:
        errors.append("BB_TOKEN no está configurado. Exportalo o creá un .env")
    if auth_type == "basic" and not username:
        errors.append("BB_USERNAME requerido para auth basic. Configuralo o usá un API Token (sin BB_USERNAME)")
    if not workspace:
        errors.append("BB_WORKSPACE no está configurado")
    return errors
