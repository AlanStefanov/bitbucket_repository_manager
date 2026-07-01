#!/usr/bin/env bash
cd "$(dirname "$0")"

if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

PYTHONPATH="src:$PYTHONPATH" exec python3 -m bitbucket_manager "$@"