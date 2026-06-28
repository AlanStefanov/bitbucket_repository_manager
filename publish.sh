#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# Bitbucket Repository Manager — Publish Script
# =============================================================================
# Publica en: PyPI, Docker Hub, Homebrew (tap)
# Uso:        ./publish.sh [--dry-run]
# Requiere:   ~/.pypirc, docker logged in, GITHUB_TOKEN
# =============================================================================

DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN=true
fi

VERSION=$(python3 -c "import sys; sys.path.insert(0,'src'); from bbm import __version__; print(__version__)")
echo "==> Publicando bbm v$VERSION"

# ---- PyPI ----
echo ""
echo "==> [PyPI] Build & upload..."
if $DRY_RUN; then
    echo "  (dry-run) python3 -m build"
    echo "  (dry-run) twine upload dist/*"
else
    python3 -m build
    twine upload dist/*
    echo "  ✓ Publicado en PyPI: https://pypi.org/project/bbm/"
fi

# ---- Docker Hub ----
echo ""
echo "==> [Docker Hub] Build & push..."
IMAGE="alanstefanov/bbm:$VERSION"
IMAGE_LATEST="alanstefanov/bbm:latest"
if $DRY_RUN; then
    echo "  (dry-run) docker build -t $IMAGE -t $IMAGE_LATEST ."
    echo "  (dry-run) docker push $IMAGE"
    echo "  (dry-run) docker push $IMAGE_LATEST"
else
    docker build -t "$IMAGE" -t "$IMAGE_LATEST" .
    docker push "$IMAGE"
    docker push "$IMAGE_LATEST"
    echo "  ✓ Publicado en Docker Hub: https://hub.docker.com/r/alanstefanov/bbm"
fi

# ---- Homebrew ----
echo ""
echo "==> [Homebrew] Update formula..."
REPO_URL="https://github.com/AlanStefanov/bitbucket_repository_manager"
TAR_URL="$REPO_URL/archive/refs/tags/v$VERSION.tar.gz"
if $DRY_RUN; then
    echo "  (dry-run) SHA: curl -sL $TAR_URL | shasum -a 256"
    echo "  (dry-run) Actualizar formula en homebrew-tap"
else
    if command -v brew &>/dev/null; then
        SHA=$(curl -sL "$TAR_URL" | shasum -a 256 | cut -d' ' -f1)
        FORMULA_PATH="$HOME/repos/homebrew-tap/Formula/bbm.rb"
        if [[ -f "$FORMULA_PATH" ]]; then
            sed -i "s/version \".*\"/version \"$VERSION\"/" "$FORMULA_PATH"
            sed -i "s/sha256 \".*\"/sha256 \"$SHA\"/" "$FORMULA_PATH"
            echo "  ✓ Formula actualizada en $FORMULA_PATH"
            echo "  ! No olvides commitear y pushear homebrew-tap"
        else
            echo "  ! Formula no encontrada en $FORMULA_PATH"
            echo "    Creala manualmente o configura el tap primero"
        fi
    else
        echo "  ! Homebrew no instalado en este entorno"
    fi
fi

echo ""
echo "==> Publicación completada para bbm v$VERSION"
echo ""
echo "    Instalación desde PyPI:"
echo "      pipx install bbm"
echo ""
echo "    Instalación desde Docker:"
echo "      docker run --rm -it -v \$PWD/.env:/app/.env alanstefanov/bbm"
echo ""
echo "    Instalación desde Homebrew (futuro):"
echo "      brew install alanstefanov/tap/bbm"
