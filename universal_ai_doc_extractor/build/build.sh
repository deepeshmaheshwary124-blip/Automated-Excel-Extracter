#!/usr/bin/env bash
# Build script for Universal AI Document Extractor.
# Packages the application into a single-file Windows .exe using PyInstaller.
#
# Usage (from the project root):
#   cd universal_ai_doc_extractor && bash build/build.sh
#
# For the authoritative Windows .exe, use the GitHub Actions workflow
# (.github/workflows/build.yml) which runs on windows-latest.

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SPEC_FILE="$PROJECT_DIR/universal_ai_doc_extractor.spec"
DIST_DIR="$PROJECT_DIR/dist"
BUILD_WORK_DIR="$PROJECT_DIR/build/_work"

echo "=== Building Universal AI Document Extractor ==="
echo "Project dir : $PROJECT_DIR"
echo "Spec file   : $SPEC_FILE"

cd "$PROJECT_DIR"

# ── Install / update dependencies ──────────────────────────────────────────
echo ""
echo "[1/4] Installing Python dependencies..."
pip install --break-system-packages -r requirements.txt 2>&1 | tail -10

# ── Clean previous build artefacts ─────────────────────────────────────────
echo ""
echo "[2/4] Cleaning old build artefacts..."
rm -rf "$DIST_DIR" "$BUILD_WORK_DIR"

# ── Run PyInstaller ─────────────────────────────────────────────────────────
echo ""
echo "[3/4] Running PyInstaller (this may take several minutes)..."
pyinstaller \
    --noconfirm \
    --clean \
    --distpath "$DIST_DIR" \
    --workpath "$BUILD_WORK_DIR" \
    "$SPEC_FILE"

# ── Report ──────────────────────────────────────────────────────────────────
echo ""
echo "[4/4] Build complete."
echo ""
echo "Output directory: $DIST_DIR"
ls -lh "$DIST_DIR/" 2>/dev/null || echo "(no files found — check build output above)"
