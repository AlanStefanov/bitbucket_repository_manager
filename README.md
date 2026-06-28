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

### Configuración

1. **Clona o descarga este repositorio**

2. **Instala dependencias Python:**

```bash
pip install requests
```

3. **Configura las credenciales de Bitbucket:**

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
BB_TOKEN="tu_token_de_bitbucket" python3 repository_manager.py
```

> ⚠️ **Nota:** El archivo `.env` contiene información sensible y está excluido del repositorio (`gitignore`). Nunca compartas este archivo.

#### Variables de Entorno

| Variable | Obligatorio | Descripción |
|----------|-------------|-------------|
| `BB_TOKEN` | ✅ Sí | Token de acceso personal de Bitbucket |
| `BB_USERNAME` | ✅ Sí | Email o username de Bitbucket para autenticación |
| `BB_WORKSPACE` | ✅ Sí | Workspace de Bitbucket (ej: `mi-empresa`) |
| `DEV_DIR` | ❌ No | Directorio donde clonar repos (defecto: `~/bitbucket-repos`) |
| `GIT_USER_NAME` | ❌ No | Nombre para git config en clones (defecto: `Your Name`) |
| `GIT_USER_EMAIL` | ❌ No | Email para git config en clones (defecto: `your-email@example.com`) |

#### ¿Cómo obtener tu token de Bitbucket?

1. Ve a **Bitbucket Settings** → **Personal access tokens**
2. Crea un nuevo token con los siguientes permisos:
   - `repo:read` - Lectura de repositorios
   - `workspace:read` - Lectura de workspaces
   - `read:user` - Lectura de información de usuario

---

## 📖 Uso

### Ejecutar el programa

```bash
./run.sh
# O directamente
python3 repository_manager.py
```

### Atajos de Teclado

| Tecla | Acción |
|-------|--------|
| `↑` / `↓` | Navegar entre repositorios |
| `k` / `j` | Navegar (vi-style) |
| `Enter` | Ver detalles / Clonar repositorio |
| `/` | Activar buscador |
| `ESC` | Limpiar filtro de búsqueda |
| `r` | Refrescar lista de repositorios |
| `q` | Salir |

---

## 🏗️ Estructura del Proyecto

```
bitbucket-repo-manager/
├── repository_manager.py   # Código principal de la aplicación
├── run.sh                  # Script de ejecución
├── .env                    # Tu configuración (NO subir a git)
├── .env.example            # Ejemplo de configuración
├── README.md               # Este archivo
└── .gitignore              # Ignora archivos sensibles
```

---

## 🔧 Configuración Adicional

### Personalizar el directorio de desarrollo

Por defecto, los repositorios se clonan en `~/bitbucket-repos`. Para cambiar esto:

```bash
export DEV_DIR="/tu/directorio/de/proyectos"
python3 repository_manager.py
```

### Cambiar el workspace de Bitbucket

Define el workspace via variable de entorno:

```bash
export BB_WORKSPACE="tu-workspace"
python3 repository_manager.py
```

---

## 🐛 Solución de Problemas

### Error: "BB_TOKEN no está configurado"

Asegúrate de tener el token configurado:
```bash
# Opción 1: Verifica que el archivo .env existe
cat .env

# Opción 2: O exporta la variable manualmente
export BB_TOKEN="tu_token"
./run.sh
```

### Error: 401 - Unauthorized

Tu token puede haber expirado. Genera uno nuevo en Bitbucket y actualiza la variable `BB_TOKEN`.

### Error: 403 - Forbidden

El token necesita permisos de lectura. Verifica que tenga los scopes `repo:read` y `workspace:read`.

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