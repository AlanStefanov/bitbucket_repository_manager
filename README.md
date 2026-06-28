<div align="center">

[![CI](https://github.com/AlanStefanov/bitbucket_repository_manager/actions/workflows/ci.yml/badge.svg)](https://github.com/AlanStefanov/bitbucket_repository_manager/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Version](https://img.shields.io/badge/version-0.1.0--alpha-orange.svg)

</div>

# Bitbucket Repository Manager — `bbm`

Suite **TUI** para administración masiva de repositorios Bitbucket Cloud. Navegación 100% por teclado, multiplataforma, instalable vía `pipx`, Docker o Homebrew.

Inspirado en [opencode](https://opencode.ai) — interfaz de terminal moderna, reactiva y productiva.

---

## Tabla de Contenidos

- [Visión](#visión)
- [Stack](#stack)
- [Roadmap — User Stories](#roadmap--user-stories)
- [Atajos de Teclado](#atajos-de-teclado)
- [Instalación](#instalación)
- [Publicación y Versionado](#publicación-y-versionado)
- [Licencia](#licencia)

---

## Visión

De un explorador TUI simple a una **suite completa** para administrar Bitbucket Cloud desde la terminal:

| Feature | Estado |
|---------|--------|
| Dashboard de workspace | ✅ Listo |
| Explorador + clonado de repos | ✅ Listo |
| Gestión masiva de permisos | 🚧 En desarrollo |
| Auto-aprobación de PRs | 🚧 En desarrollo |
| Migración entre proyectos | 🚧 En desarrollo |
| Archivado inteligente | 🚧 En desarrollo |
| Análisis de dependencias | 🚧 En desarrollo |
| Publicación (PyPI, Docker, Brew) | 🚧 En desarrollo |

Cada feature se despliega como una **pantalla TUI** accesible desde el menú principal, con operaciones masivas, dry-run y confirmación explícita.

---

## Stack

| Capa | Librería |
|------|----------|
| **TUI Framework** | [Textual](https://textual.textualize.io/) 8.x — async, CSS-like styling, 24-bit color |
| **HTTP / API** | `requests` — cliente REST para Bitbucket Cloud API v2.0 |
| **YAML** | `pyyaml` — reglas de PR, archivado, dependencias |
| **Terminal enhancements** | `rich` — logging, tablas, progreso |
| **Distribución** | `pyproject.toml` → PyPI / `pipx` / Docker / Homebrew |

### Por qué Textual

- Async nativo (`asyncio`)
- Estilos con TCSS (simil CSS, no curses)
- Widgets modernos: `DataTable`, `Select`, `Input`, `Tree`
- Hot-reload en desarrollo
- Soporte para mouse + teclado
- 24-bit color, emojis, renderizado rápido

---

## Roadmap — User Stories

### US1: Gestión Masiva de Permisos

Agregar, remover y sincronizar permisos de usuarios/grupos en N repositorios simultáneamente.

- Listar permisos actuales de uno o varios repos
- Grant/revoke con rol (READ, WRITE, ADMIN)
- Copiar permisos de un repo origen a N destinos
- Sincronizar desde CSV/YAML
- Modo dry-run en todas las operaciones

### US2: Auto-aprobación de PRs

Reglas configurables en YAML para aprobar PRs automáticamente según branch, autor, etiquetas, archivos tocados.

- Reglas por branch origen/destino, autor, labels, file pattern
- Modo supervisado: agrupa candidatos y muestra antes de aprobar
- Reporte de PRs aprobados/rechazados por regla
- Config persistente en `pr_rules.yaml`

### US3: Migración entre Proyectos

Migrar repos entre workspaces preservando historial git, branches, tags y PRs abiertos.

- Plan de migración preview
- Push mirror con git
- Re-creación de branch protections y webhooks
- Rollback ante fallo parcial

### US4: Archivado Inteligente

Archivar repositorios inactivos según reglas configurables (último commit, PRs abandonados, N meses sin actividad).

- Escaneo de candidatos por antigüedad
- Archivado batch con confirmación
- Preservación de config para restauración
- Restaurar repos archivados

### US5: Análisis de Dependencias Cruzadas

Escanear dependencias entre repos del workspace mediante patrones de import en código fuente.

- Grafo de dependencias (árbol / lista)
- Detección de repos huérfanos (sin deps in/out)
- Detección de ciclos
- Reporte de impacto ante migración/archivado

### US6: Publicación

Distribuir `bbm` en los 3 canales principales para que cualquier admin lo instale en segundos.

| Canal | Comando |
|-------|---------|
| PyPI / pipx | `pipx install bbm` |
| Docker Hub | `docker pull alanstefanov/bbm` |
| Homebrew | `brew install alanstefanov/tap/bbm` |

---

## Atajos de Teclado

La app está diseñada para uso 100% con teclado. Sin mouse requerido.

### Pantalla de inicio (Home)

| Tecla | Acción |
|-------|--------|
| `↑` / `↓` | Navegar entre cards |
| `←` / `→` | Navegar entre cards |
| `Tab` / `Shift+Tab` | Navegar entre cards |
| `Enter` | Abrir pantalla seleccionada |
| `F1` | Dashboard |
| `F2` | Repos |
| `F3` | Permisos |
| `F4` | PRs |
| `F5` | Migración |
| `F6` | Archive |
| `F7` | Dependencias |
| `Q` | Salir de la app |
| `Esc` | Salir de la app |
| `Ctrl+Q` | Salir de la app |

### Pantallas de feature

| Tecla | Acción |
|-------|--------|
| `H` | Volver al menú principal |
| `Esc` | Volver al menú principal |
| `Ctrl+Q` | Salir de la app |
| `Tab` / `Shift+Tab` | Navegar entre controles |
| `Ctrl+R` | Refrescar (Explorer / Dashboard) |

### Controles comunes

| Widget | Interacción |
|--------|-------------|
| `Input` | Escribir texto, `Enter` para confirmar |
| `Select` | `↑↓` + `Enter` para elegir opción |
| `DataTable` | `↑↓` para navegar filas |
| `Button` | `Enter` o `Space` para accionar |
| `Checkbox` | `Space` para toggle |

---

## Instalación

### pipx (recomendado)

```bash
pipx install bbm
bbm
```

### pip

```bash
pip install bbm
bbm
```

### Docker

```bash
docker run --rm -it \
  -v $PWD/.env:/app/.env \
  alanstefanov/bbm
```

### Homebrew

```bash
brew install alanstefanov/tap/bbm
bbm
```

### Configuración rápida

```bash
cp .env.example .env
# Editar .env con: BB_USERNAME, BB_TOKEN, BB_WORKSPACE
bbm
```

Variables requeridas:

| Variable | Descripción |
|----------|-------------|
| `BB_USERNAME` | Email de Atlassian (NO username de Bitbucket) |
| `BB_TOKEN` | API Token desde https://id.atlassian.com/manage-profile/security/api-tokens |
| `BB_WORKSPACE` | Workspace de Bitbucket (ej: `mi-empresa`) |
| `DEV_DIR` | Directorio para clones (opcional, defecto: `~/bitbucket-repos`) |

### Ejecución desde el repo

```bash
./run.sh
```

---

## Publicación y Versionado

### Versionado Semántico

`bbm` sigue [SemVer](https://semver.org/): `MAJOR.MINOR.PATCH`.

- **MAJOR**: cambios incompatibles en API/UI
- **MINOR**: nuevas features (backward-compatible)
- **PATCH**: bugfixes, performance, docs

La versión se define en `src/bbm/__init__.py` y se refleja en `pyproject.toml`.

### Release automática

Al hacer merge de un PR a `main`:

1. **CI** corre lint + typecheck + tests
2. **GitHub Actions** (o script manual) etiqueta con `v{version}`
3. Se publica automáticamente a:
   - **PyPI** via `twine`
   - **Docker Hub** via `docker buildx + push`
   - **Homebrew** actualizando la fórmula en `homebrew-tap`

### Pipeline actual

```yaml
# .github/workflows/release.yml (futuro)
on:
  push:
    branches: [main]

jobs:
  release:
    - build & publish to PyPI
    - build & push Docker image
    - update Homebrew formula
    - create GitHub Release
```

---

## Licencia

MIT — Alan Stefanov, 2026.