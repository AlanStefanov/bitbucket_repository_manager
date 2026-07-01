#!/usr/bin/env bash
# install.sh — Instalador rápido de BBM
# Baja el script y lo ejecuta directamente con python, sin pip/pipx
#
# Uso:
#   bash <(curl -fsSL https://github.com/AlanStefanov/bitbucket_repository_manager/raw/main/install.sh)
#   # O localmente:
#   bash install.sh

set -euo pipefail

REPO_URL="https://github.com/AlanStefanov/bitbucket_repository_manager"
SCRIPT="repository_manager.py"

echo "==> BBM — Bitbucket Repository Manager"
echo ""

# 1. Verificar python
if ! command -v python3 &>/dev/null; then
  echo "ERROR: python3 no está instalado."
  echo "  Linux:  sudo apt install python3 python3-pip"
  echo "  macOS:  brew install python"
  exit 1
fi
echo "[✓] python3 $(python3 --version 2>&1 | cut -d' ' -f2)"

# 2. Verificar / instalar requests
if ! python3 -c "import requests" &>/dev/null; then
  echo "--> Instalando requests (dependencia única)..."
  python3 -m pip install requests --quiet
fi
echo "[✓] requests"

# 3. Descargar el script
echo "--> Descargando ${SCRIPT}..."
TMPFILE=$(mktemp)
trap "rm -f ${TMPFILE}" EXIT

if curl -fsSL "${REPO_URL}/raw/main/${SCRIPT}" -o "${TMPFILE}"; then
  chmod +x "${TMPFILE}"
  echo "[✓] Descargado"
else
  echo "ERROR: no se pudo descargar ${SCRIPT}"
  echo "       Asegurate de tener internet y probá de nuevo."
  exit 1
fi

# 4. Ejecutar
echo ""
echo "==> Iniciando BBM..."
exec python3 "${TMPFILE}"
