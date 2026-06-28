#!/bin/bash
cd "$(dirname "$0")"

# Cargar .env siempre (las env vars ya exportadas toman prioridad)
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

if [ -z "$BB_TOKEN" ]; then
    echo "Error: BB_TOKEN no está configurado"
    echo "Configuralo con: export BB_TOKEN='tu_token'"
    echo "O crea un archivo .env con el contenido: BB_TOKEN='tu_token'"
    exit 1
fi

python3 repository_manager.py