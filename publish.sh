#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# Bitbucket Manager — Publish Script
# =============================================================================
# Publica en: PyPI, Homebrew (tap)
# Uso:        ./publish.sh [--dry-run]
# Requiere:   ~/.pypirc, GITHUB_TOKEN
# =============================================================================

DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN=true
fi

VERSION=$(python3 -c "import sys; sys.path.insert(0,'src'); from bitbucket_manager import __version__; print(__version__)")
echo "==> Publicando bitbucket-manager v$VERSION"

# ---- PyPI ----
echo ""
echo "==> [PyPI] Build & upload..."
if $DRY_RUN; then
    echo "  (dry-run) python3 -m build"
    echo "  (dry-run) twine upload dist/*"
else
    python3 -m build
    twine upload dist/*
    echo "  ✓ Publicado en PyPI: https://pypi.org/project/bitbucket-manager/"
fi

# ---- Homebrew ----
echo ""
echo "==> [Homebrew] Update formula..."
REPO_URL="https://github.com/AlanStefanov/bitbucket-manager"
TAR_URL="$REPO_URL/archive/refs/tags/v$VERSION.tar.gz"
if $DRY_RUN; then
    echo "  (dry-run) SHA: curl -sL $TAR_URL | shasum -a 256"
    echo "  (dry-run) Actualizar formula en homebrew-tap"
else
    if command -v brew &>/dev/null; then
        SHA=$(curl -sL "$TAR_URL" | shasum -a 256 | cut -d' ' -f1)
        FORMULA_PATH="$HOME/repos/homebrew-tap/Formula/bitbucket-manager.rb"
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
echo "==> Publicación completada para bitbucket-manager v$VERSION"
echo ""
echo "    Instalación desde PyPI:"
echo "      pipx install bitbucket-manager"
echo ""
echo "    O con pip:"
echo "      pip install bitbucket-manager"
echo ""
echo "    Instalación desde Homebrew:"
echo "      brew install alanstefanov/tap/bitbucket-manager"
