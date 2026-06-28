<div align="center">

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Alan_Stefanov-blue?style=flat-square&logo=linkedin)](https://www.linkedin.com/in/alanstefanov/)
[![Email](https://img.shields.io/badge/Email-alan.emanuel.stefanov@gmail.com-red?style=flat-square&logo=gmail)](mailto:alan.emanuel.stefanov@gmail.com)
[![GitHub](https://img.shields.io/badge/GitHub-AlanStefanov-black?style=flat-square&logo=github)](https://github.com/AlanStefanov)
[![Web](https://img.shields.io/badge/Web-astefanov.com-10b981?style=flat-square&logo=vercel)](https://astefanov.com)
[![CI](https://github.com/AlanStefanov/bitbucket_repository_manager/actions/workflows/ci.yml/badge.svg)](https://github.com/AlanStefanov/bitbucket_repository_manager/actions/workflows/ci.yml)

**Alan Stefanov** — Engineering Manager · DevOps Engineer · Software Developer · _La Plata, Argentina_

---

</div>

# Bitbucket Repository Manager

<div align="center">

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20WSL-blue.svg)

**Una herramienta CLI elegante para gestionar repositorios de Bitbucket Cloud**

</div>

---

## ✨ Características

- 📋 **Explorador de Repositorios** - Navega por todos tus repositorios de Bitbucket en una interfaz TUI intuitiva
- 🔍 **Búsqueda en Tiempo Real** - Filtra repositorios al instante con el buscador integrado
- 📦 **Clonado con Un Clic** - Clona repositorios directamente desde la interfaz
- 🎯 **Indicador de Estado** - Visualiza rápidamente qué repositorios ya están clonados localmente
- ⌨️ **Navegación por Teclado** - Control total con atajos de teclado eficientes
- 🔐 **Autenticación Segura** - Token pasado por variable de entorno (nunca expuesto en código)

---

## 🚀 Instalación

### Prerrequisitos

- **[Python 3.8+](https://www.python.org/downloads/)** — Lenguaje de programación
- **[Git](https://git-scm.com/downloads)** — Control de versiones (para clonar repos)
- **[pip](https://pip.pypa.io/en/stable/installation/)** — Gestor de paquetes de Python
- **Acceso a Internet** — Para conectar con la API de Bitbucket

#### Instalación por sistema operativo

<details>
<summary><b>🐧 Linux (Debian/Ubuntu)</b></summary>

```bash
sudo apt update
sudo apt install python3 python3-pip git -y
```
</details>

<details>
<summary><b>🍎 macOS</b></summary>

```bash
# Con Homebrew
brew install python git
```
</details>

<details>
<summary><b>🪟 Windows (WSL)</b></summary>

```bash
# Instala WSL primero, luego en tu terminal Linux:
sudo apt update && sudo apt install python3 python3-pip git -y
```
</details>

### Instalación Global (recomendado)

```bash
# Con pipx (recomendado)
pipx install bbm

# Con pip
pip install bbm

# Con Docker
docker pull alanstefanov/bbm

# Con Homebrew (futuro)
# brew install alanstefanov/tap/bbm
```

### Configuración

1. **Clona o descarga este repositorio** (o usa la instalación global)

2. **Configura las credenciales de Bitbucket:**

Hay dos formas de configurar el token:

#### Opción A: Archivo `.env` (Recomendado)

```bash
# Copia el ejemplo y configura tu token
cp .env.example .env
# Edita el archivo .env y reemplaza tu_token_aqui con tu token real
```

El contenido de `.env` debe tener al menos estas variables (usa `.env.example` como guía):

```
BB_TOKEN=tu_token_de_bitbucket
BB_USERNAME=tu-email@example.com
BB_WORKSPACE=tu-workspace
```

#### Opción B: Variable de entorno

```bash
# Exporta el token (añade esto a tu ~/.bashrc o ~/.zshrc para persistencia)
export BB_TOKEN="tu_token_de_bitbucket"

# O ejecuta directamente antes de correr el programa
BB_TOKEN="tu_token_de_bitbucket" bbm
```

> ⚠️ **Nota:** El archivo `.env` contiene información sensible y está excluido del repositorio (`gitignore`). Nunca compartas este archivo.

#### Variables de Entorno

| Variable | Obligatorio | Descripción |
|----------|-------------|-------------|
| `BB_TOKEN` | ✅ Sí | API Token de Bitbucket (desde id.atlassian.com) |
| `BB_USERNAME` | ✅ Sí | Email o username de Bitbucket |
| `BB_WORKSPACE` | ✅ Sí | Workspace de Bitbucket (ej: `mi-empresa`) |
| `DEV_DIR` | ❌ No | Directorio donde clonar repos (defecto: `~/bitbucket-repos`) |
| `GIT_USER_NAME` | ❌ No | Nombre para git config en clones |
| `GIT_USER_EMAIL` | ❌ No | Email para git config en clones |

> 💡 ¿No tenés token? [Mirá el FAQ →](#-faq--preguntas-frecuentes) — Crealo en https://id.atlassian.com/manage-profile/security/api-tokens (máx. 1 año de expiración)

#### Ejecución desde el repositorio (sin instalar)

```bash
./run.sh                  # Lanza la TUI
./run.sh permissions list --repo repo-a   # Comando directo

# O directamente con PYTHONPATH
PYTHONPATH=src python3 -m bbm
PYTHONPATH=src python3 -m bbm permissions list --repo repo-a
```

---

## 📖 Uso

### TUI — Explorador de Repositorios

```bash
bbm
# o desde el repo:
./run.sh
```

Navegá por tus repositorios, clonalos con un clic, filtrá por nombre.

#### Atajos de Teclado

| Tecla | Acción |
|-------|--------|
| `↑` / `↓` | Navegar entre repositorios |
| `k` / `j` | Navegar (vi-style) |
| `Enter` | Ver detalles / Clonar repositorio |
| `/` | Activar buscador |
| `ESC` | Limpiar filtro de búsqueda |
| `r` | Refrescar lista de repositorios |
| `q` | Salir |

### CLI — Gestión Masiva de Permisos

```bash
# Listar permisos actuales de repos
bbm permissions list --repo repo-a --repo repo-b

# Otorgar permiso a un usuario en múltiples repos
bbm permissions grant --user juan.perez --role WRITE --repo repo-a --repo repo-b

# Revocar permiso
bbm permissions revoke --user juan.perez --repo repo-a

# Copiar permisos de un repo a otros
bbm permissions copy --from repo-base --to repo-b --to repo-c

# Sincronizar desde archivo CSV
bbm permissions sync --file permisos.csv

# Todas las operaciones soportan --dry-run
bbm permissions grant --user juan.perez --role ADMIN --repo repo-a --dry-run
```

Formato del CSV para `sync`:

```csv
action,type,user,group,role,repos
grant,user,juan.perez,,write,repo-a,repo-b
grant,group,,developers,admin,repo-c
revoke,user,maria,,,repo-a
```

### Docker

```bash
docker run --rm -it -v $PWD/.env:/app/.env alanstefanov/bbm
docker run --rm -it -v $PWD/.env:/app/.env alanstefanov/bbm permissions list --repo repo-a
```

---

## 🏗️ Estructura del Proyecto

```
bbm/
├── src/bbm/
│   ├── __init__.py       # Versión del paquete
│   ├── __main__.py       # python -m bbm
│   ├── cli.py            # Entry point CLI (argparse)
│   ├── config.py         # Carga de .env y validación
│   ├── api.py            # Cliente API Bitbucket
│   ├── tui.py            # Interfaz TUI (curses)
│   └── permissions.py    # Feature: gestión masiva de permisos
├── pyproject.toml         # Build config
├── Dockerfile             # Imagen Docker
├── publish.sh             # Publicación a PyPI / Docker / Brew
├── run.sh                 # Ejecución desde el repo sin instalar
├── .env.example           # Template de configuración
├── repository_manager.py  # Script legacy (deprecated)
└── docs/                  # Roadmap y user stories (local)
```

---

## 🔧 Configuración Adicional

### Personalizar el directorio de desarrollo

Por defecto, los repositorios se clonan en `~/bitbucket-repos`. Para cambiar esto:

```bash
export DEV_DIR="/tu/directorio/de/proyectos"
bbm
```

### Cambiar el workspace de Bitbucket

```bash
export BB_WORKSPACE="tu-workspace"
bbm
```

---

## ❓ FAQ — Preguntas Frecuentes

### ¿Cómo obtengo un API Token de Bitbucket?

1. Andá a **https://id.atlassian.com/manage-profile/security/api-tokens**
2. Creá un nuevo token con estos alcances mínimos:
   - `repository:read` — Listar y clonar repos
   - `workspace:management` — Leer workspaces
   - `account:read` — Información de usuario
3. **Importante:** la expiración máxima es **1 año**
4. Copiá el token generado y ponelo en tu `.env`
5. Si también configurás `BB_USERNAME`, se usará autenticación Basic (compatible con tokens viejos). Si solo configurás `BB_TOKEN`, se usará autenticación Bearer (recomendado).

### ¿Cómo uso el archivo `.env`?

```bash
cp .env.example .env
# Editá .env y reemplazá las variables con tus datos
./run.sh
```

El `run.sh` lo carga automáticamente.

### ¿Y si prefiero variables de entorno?

```bash
export BB_TOKEN="tu_token"
export BB_USERNAME="tu-email@example.com"
export BB_WORKSPACE="tu-workspace"
./run.sh
```

Agregá los `export` a tu `~/.bashrc` o `~/.zshrc` para persistencia.

### ¿Por qué `.env` no está en el repositorio?

El `.env` contiene tokens y credenciales personales. Está en `.gitignore` para evitar subirlo por accidente. Siempre usá `.env.example` como template.

### Error: "BB_TOKEN no está configurado"

No encontró el token. Verificá:
```bash
cat .env                          # ¿Existe y tiene el token?
source .env && echo $BB_TOKEN     # ¿Se carga bien?
export BB_TOKEN="tu_token"        # O pasalo directo
./run.sh
```

### Error: 401 Unauthorized

El token es inválido o expiró. Generá uno nuevo en Bitbucket y actualizá `BB_TOKEN`.

### Error: 403 Forbidden

El token no tiene los permisos necesarios. Verificá que tenga `repository:read` y `workspace:management`.

### Error: "No such file or directory: .env"

Ejecutá primero `cp .env.example .env` y completá los valores.

### ¿Funciona con Bitbucket Server (self-hosted)?

No, esta herramienta usa la API de **Bitbucket Cloud** (api.bitbucket.org). Para Bitbucket Server necesitarías modificar la URL base de la API.

### ¿Cómo uso la imagen de Docker?

```bash
# Montá tu .env y ejecutá
docker run --rm -it -v $PWD/.env:/app/.env alanstefanov/bbm

# Para comandos CLI
docker run --rm -it -v $PWD/.env:/app/.env alanstefanov/bbm permissions list --repo mi-repo
```

### ¿Cómo instalo con pipx?

```bash
pipx install bbm
bbm
```

### ¿Qué alcances necesita el API Token?

Dependiendo de las operaciones que quieras hacer:

| Operación | Alcances necesarios |
|-----------|---------------------|
| Explorar repos + clonar | `repository:read`, `workspace:management`, `account:read` |
| Gestionar permisos | + `repository:admin` |
| Auto-aprobar PRs | + `pullrequest:write` |
| Migrar repos | + `repository:admin` (en origen y destino) |
| Archivar repos | + `repository:admin` |

> ⚠️ Si usás un API Token de id.atlassian.com, **no necesitás** `BB_USERNAME`. Solo `BB_TOKEN` es suficiente.

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Por favor, abre un issue o PR en el repositorio.

---

## 📝 Licencia

Este proyecto está bajo la Licencia MIT — ve el archivo `LICENSE` para más detalles.

---

## 🙏 Agradecimientos

- [Atlassian](https://www.atlassian.com/) por Bitbucket Cloud
- [Python](https://www.python.org/) por el lenguaje
- [curses](https://docs.python.org/3/library/curses.html) por la interfaz de terminal

---

*¿Te gusta este proyecto? ¡Échale un vistazo a mis otros trabajos en [GitHub](https://github.com/AlanStefanov)!*