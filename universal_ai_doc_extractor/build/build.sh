#!/bin/bash
"""
Build script for Universal AI Document Extractor.
Packages the application using PyInstaller.
"""

set -e

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BUILD_DIR="$PROJECT_DIR/build"
DIST_DIR="$BUILD_DIR/dist"

echo "=== Building Universal AI Document Extractor ==="
echo "Project dir: $PROJECT_DIR"

cd "$PROJECT_DIR"

echo "Installing dependencies..."
pip install --break-system-packages -r requirements.txt 2>&1 | tail -5

echo "Cleaning old builds..."
rm -rf "$BUILD_DIR/dist" "$BUILD_DIR/build" "$PROJECT_DIR/*.spec"

echo "Running PyInstaller..."
pyinstaller \
    --name "Universal AI Document Extractor" \
    --onefile \
    --windowed \
    --noconfirm \
    --clean \
    --add-data "assets:assets" \
    --hidden-import "PySide6.QtCore" \
    --hidden-import "PySide6.QtWidgets" \
    --hidden-import "PySide6.QtGui" \
    --hidden-import "pytesseract" \
    --hidden-import "easyocr" \
    --hidden-import "openpyxl" \
    --hidden-import "pandas" \
    --hidden-import "PIL" \
    --hidden-import "PIL.Image" \
    --hidden-import "cryptography" \
    --hidden-import "cryptography.fernet" \
    --hidden-import "pypdf2" \
    --hidden-import "pypdfium2" \
    --hidden-import "matplotlib" \
    --hidden-import "matplotlib.backends.backend_qtagg" \
    --hidden-import "requests" \
    --hidden-import "pydantic" \
    --collect-all "PySide6" \
    main.py

echo ""
echo "=== Build Complete ==="
echo "Output: $DIST_DIR/Universal AI Document Extractor.exe"
ls -lh "$DIST_DIR/" 2>/dev/null || ls -lh "$PROJECT_DIR/dist/"
