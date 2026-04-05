# Bitbucket Repository Manager

<div align="center">

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Linux-yellow.svg)

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

- Python 3.8+
- Git
- Acceso a Internet (para conectar con la API de Bitbucket)

### Configuración

1. **Clona o descarga este repositorio**

2. **Configura el token de Bitbucket:**

```bash
# Exporta el token (añade esto a tu ~/.bashrc o ~/.zshrc para persistencia)
export BB_TOKEN="tu_token_de_bitbucket"

# O ejecuta directamente antes de correr el programa
BB_TOKEN="tu_token_de_bitbucket" python3 repository_manager.py
```

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
├── run.sh                 # Script de ejecución
├── README.md              # Este archivo
└── .gitignore             # Ignora archivos sensibles
```

---

## 🔧 Configuración Adicional

### Personalizar el directorio de desarrollo

Por defecto, los repositorios se clonan en `/home/stefanov/farmu`. Para cambiar esto:

```bash
export DEV_DIR="/tu/directorio/aqui"
python3 repository_manager.py
```

### Cambiar el workspace de Bitbucket

Edita la variable `USERNAME` en `repository_manager.py` para apuntar a otro workspace:

```python
USERNAME = "otro_workspace"
```

---

## 🐛 Solución de Problemas

### Error: "BB_TOKEN no está configurado"

Asegúrate de haber exportado la variable de entorno:
```bash
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

Este proyecto está bajo la Licencia MIT - ve el archivo `LICENSE` para más detalles.

---

## 🙏 Agradecimientos

- [Atlassian](https://www.atlassian.com/) por Bitbucket Cloud
- [Python](https://www.python.org/) por el lenguaje
- [curses](https://docs.python.org/3/library/curses.html) por la interfaz de terminal

---

<div align="center">

Hecho con ❤️ por [Alan Stefanov](https://www.linkedin.com/in/alanstefanov/)

</div>