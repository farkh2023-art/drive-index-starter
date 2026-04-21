# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A Python script that recursively scans a local directory, extracts content from PDFs/DOCX/images, generates AI summaries via OpenAI, and outputs an interactive HTML catalog (`index_interactif.html`) with a dark-themed sidebar, search, and export features.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the indexer
python analyze_drive.py

# Outputs:
# - index_interactif.html   (browsable catalog)
# - miniatures/             (image thumbnails, 260x180px)
```

No test suite, linter config, or build step exists.

## Configuration (top of `analyze_drive.py`)

```python
DOSSIER_BASE = Path("...")    # Directory to scan
OPENAI_KEY = os.environ.get("OPENAI_KEY", "")  # Read from env, never hardcode
UTILISER_OPENAI = bool(OPENAI_KEY)
NOTION_TOKEN = ""             # Optional Notion integration
DATABASE_ID = ""
HTML_TEMPLATE = "index_template.html"
HTML_FINAL = "index_interactif.html"
SIGNATURE = "Maitre Jordan"
```

**Critical**: The current `analyze_drive.py` has a real `OPENAI_KEY` hardcoded at line 14. It must be moved to an environment variable before any commit.

## Architecture

**Single-script pipeline** (`analyze_drive.py`):

1. `walk_and_extract(base_path, racine)` — recursive `os.scandir` over `DOSSIER_BASE`; returns `(tree, stats)` where `tree` is a nested list of file/folder dicts and `stats` counts pdf/docx/images/autres/fichiers/poids_total
2. Per file type:
   - PDF → `extraire_pdf()` via `pdfplumber`; first 800 chars stored as `extrait`
   - DOCX → `extraire_docx()` via `python-docx`; first 800 chars stored as `extrait`
   - Images (jpg/jpeg/png/bmp/gif) → `generer_miniature()` via Pillow → `miniatures/<stem>_thumb.jpg` (260×180px)
3. `resume_texte_ia(texte)` — sends first 5 000 chars to `gpt-3.5-turbo`, max 220 tokens; skipped when `UTILISER_OPENAI` is false
4. Python injects `folderTree` and `dossierStats` as inline JS variables into `index_template.html`, producing `index_interactif.html`

**Template injection** (`index_template.html`):
- The template contains two JS variable declarations that Python replaces via string substitution: `const folderTree = ...` and `const dossierStats = ...`
- The frontend reads these globals in `window.onload` to render the sidebar tree and stats panel

**Frontend** (`index_template.html`):
- Dark theme (blue/gold), French UI with FR↔EN toggle (`setLang()`)
- Sidebar: collapsible folder tree (`createTree()`), live search on file/folder names, stats panel
- Main panel: `showFilePreview(item)` renders thumbnail, text extract, and AI summary on click
- Action buttons: Download ZIP, Export JSON/CSV, Export to Notion (ZIP button is non-functional — `make_zip()` is incomplete)
- Responsive breakpoints at 900px and 600px (`static/style.css`)

## Known Issues

- `make_zip()` body is truncated — the function starts but never finishes writing files into the archive
- `openai.ChatCompletion.create` (used in `resume_texte_ia`) is the legacy API removed in `openai>=1.0.0`; either pin `openai<1.0.0` in requirements or migrate to `openai.chat.completions.create`
- `OPENAI_KEY` is currently hardcoded with a real key — rotate it and move to env before any commit
