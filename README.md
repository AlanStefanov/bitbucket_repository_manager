<div align="center">

[![CI](https://github.com/AlanStefanov/bitbucket-manager/actions/workflows/ci.yml/badge.svg)](https://github.com/AlanStefanov/bitbucket-manager/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Version](https://img.shields.io/badge/version-0.1.0--alpha-orange.svg)

</div>

# Bitbucket Manager

Suite **TUI** para administración de Bitbucket Cloud desde la terminal. Navegación 100% por teclado, multiplataforma, instalable vía `pipx`, `pip` o Homebrew.

Inspirado en [opencode](https://opencode.ai) — interfaz de terminal moderna, reactiva y productiva.

---

## Tabla de Contenidos

- [Visión](#visión)
- [Stack](#stack)
- [Features](#features)
- [Atajos de Teclado](#atajos-de-teclado)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Publicación y Versionado](#publicación-y-versionado)
- [Licencia](#licencia)

---

## Visión

Administrar Bitbucket Cloud desde la terminal, sin tocar el navegador:

| Feature | Estado |
|---------|--------|
| Dashboard de workspace | ✅ Listo |
| Explorador + clonado de repos | ✅ Listo |
| Gestión masiva de permisos | ✅ Listo |
| Gestión de grupos y miembros | ✅ Listo |
| Miembros del workspace | ✅ Listo |
| Auto-aprobación de PRs | 🚧 En desarrollo |
| Migración entre proyectos | 🚧 En desarrollo |
| Archivado inteligente | 🚧 En desarrollo |
| Análisis de dependencias | 🚧 En desarrollo |
| Publicación (PyPI, Homebrew) | 🚧 En desarrollo |

---

## Stack

| Capa | Librería |
|------|----------|
| **TUI Framework** | [Textual](https://textual.textualize.io/) 8.x — async, CSS-like styling, 24-bit color |
| **HTTP / API** | `requests` — cliente REST para Bitbucket Cloud API v2.0 |
| **YAML** | `pyyaml` — reglas de PR, archivado, dependencias |
| **Terminal enhancements** | `rich` — logging, tablas, progreso |
| **Distribución** | `pyproject.toml` → PyPI / `pipx` / Homebrew |

---

## Features

### 👥 Grupos
- Listar todos los grupos del workspace
- Crear y eliminar grupos
- Agregar o remover miembros de un grupo

### 👤 Miembros
- Listar todos los miembros del workspace
- Ver display name, nickname y account ID

### 📊 Dashboard
- Métricas del workspace: total de repos, PRs abiertos, activida reciente

### 📦 Repos
- Explorar repositorios del workspace
- Clonar, pull y checkout desde la TUI

### 🔐 Permisos
- Listar permisos de usuarios y grupos por repositorio
- Otorgar y revocar permisos

### ✅ PRs
- Listar PRs abiertos
- Auto-aprobar PRs

### 📋 Migración
- Migrar repositorios entre workspaces manteniendo historial git

### 🗄️ Archive
- Archivar repositorios inactivos según reglas configurables

### 🔗 Deps
- Analizar dependencias entre repos del workspace

---

## Atajos de Teclado

### Pantalla de inicio (Home)

| Tecla | Acción |
|-------|--------|
| `↑` / `↓` | Navegar entre cards |
| `←` / `→` | Navegar entre cards |
| `Tab` / `Shift+Tab` | Navegar entre cards |
| `Enter` / `Space` | Abrir pantalla seleccionada |
| `D` | Dashboard |
| `R` | Repos |
| `G` | Grupos |
| `I` | Miembros |
| `P` | Permisos |
| `U` | PRs |
| `M` | Migración |
| `A` | Archive |
| `S` | Dependencias |
| `Q` / `Esc` / `Ctrl+Q` | Salir |

### Pantallas de feature

| Tecla | Acción |
|-------|--------|
| `H` / `Esc` | Volver al menú principal |
| `Ctrl+Q` | Salir de la app |

---

## Instalación

### pipx (recomendado)

```bash
pipx install bitbucket-manager
bitbucket-manager
```

### pip

```bash
pip install bitbucket-manager
bitbucket-manager
```

### Homebrew (futuro)

```bash
brew install alanstefanov/tap/bitbucket-manager
```

### One-liner (curses ligero)

```bash
bash <(curl -fsSL https://github.com/AlanStefanov/bitbucket-manager/raw/main/install.sh)
```

---

## Configuración

La primera vez que ejecutes la app, te mostrará una pantalla interactiva para ingresar las credenciales.

O podés crear un archivo `~/.config/bitbucket-manager/env`:

```bash
BB_USERNAME=tu-email@example.com
BB_TOKEN=tu_api_token
BB_WORKSPACE=mi-workspace
DEV_DIR=/home/tu/Documents/bitbucket-repos
```

Variables requeridas:

| Variable | Descripción |
|----------|-------------|
| `BB_USERNAME` | Email de Atlassian |
| `BB_TOKEN` | API Token desde https://id.atlassian.com/manage-profile/security/api-tokens |
| `BB_WORKSPACE` | Workspace de Bitbucket (ej: `mi-empresa`) |
| `DEV_DIR` | Directorio para clones (defecto: `~/Documents/bitbucket-repos`) |

### Ejecución desde el repo

```bash
./run.sh
```

---

## Publicación y Versionado

### Versionado Semántico

`bitbucket-manager` sigue [SemVer](https://semver.org/): `MAJOR.MINOR.PATCH`.

La versión se define en `src/bitbucket_manager/__init__.py` y se refleja en `pyproject.toml`.

### Release

Al hacer merge de un PR a `main`:

1. **CI** corre lint + verifica que el paquete importe correctamente
2. Ejecutar `bash publish.sh` para publicar a PyPI y Homebrew

---

## Licencia

MIT — Alan Stefanov, 2026.
