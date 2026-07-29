# Universal AI Document Extractor

Professional desktop application for extracting data from documents (PDFs, invoices, receipts, images) using AI and OCR, with intelligent Excel automation.

## Features

- **Document Extraction** - PDF, PNG, JPG, TIFF, BMP, DOCX, CSV, TXT
- **AI-Powered** - OpenAI, Claude, Gemini, OpenRouter, Ollama support
- **OCR Engines** - Tesseract, EasyOCR, OCRmyPDF
- **Excel Integration** - Style-preserving writes, append-only, validation, backups
- **Dashboard** - Analytics, charts, activity timeline
- **Review Center** - Edit/approve/reject extracted fields with confidence scoring
- **AI Chat Assistant** - Natural language queries, journal entries, summaries
- **Global Search** - Search invoices, documents, workbooks, logs
- **Themes** - Professional dark/light modes
- **Security** - AES-256 encrypted API keys, local-only storage

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## Build .exe (Windows)

```bash
# With PyInstaller
pyinstaller --onefile --windowed --name "Universal AI Document Extractor" main.py
```

Or use GitHub Actions: push a tag `v*` to trigger automated build.

## Run Tests

```bash
python -m pytest tests/ -v
```

## Requirements

- Python 3.10+
- Windows 10/11 (for .exe build)
- Tesseract OCR (optional, for OCR features)
- API key for AI providers (optional for local Ollama)

## Project Structure

```
config/          - Settings, constants, logging
database/        - SQLite connection, migrations, repositories
models/          - Data classes, enums
services/        - Document, OCR, PDF, Excel, AI, Encryption
ai/              - OpenAI, Claude, Gemini, OpenRouter, Ollama clients
ocr/             - OCR engine abstractions
excel/           - Excel utilities
themes/          - Dark/light QSS theme engine
ui/              - MainWindow, sidebar, pages, widgets, dialogs
utils/           - Helpers, decorators
tests/           - Unit and integration tests
build/           - PyInstaller spec and build script
```

## License

Copyright 2024 AI Document Solutions. All rights reserved.
