# Migration Guide: From Original to Refactored Version

This guide helps you migrate from the original `analyze_drive.py` script to the new refactored architecture.

## Overview of Changes

### 1. Architecture Improvements

**Before:**
- Single monolithic script with all logic in one file
- Hard-coded configuration values
- Tight coupling between components
- Difficult to test individual components

**After:**
- Modular architecture with clear separation of concerns
- Flexible environment-based configuration
- Loose coupling through dependency injection
- Highly testable components

### 2. New Module Structure

```
drive_index/
├── __init__.py          # Package exports
├── app.py               # Main application orchestrator
├── config.py            # Configuration management
├── exceptions.py        # Custom exceptions
├── interfaces.py        # Component interfaces
├── extractors.py        # File text extraction
├── ai_service.py        # AI summarization
├── thumbnail_generator.py # Image thumbnails
├── file_scanner.py      # Directory scanning
└── html_generator.py    # HTML generation
```

## Step-by-Step Migration

### Step 1: Install Dependencies

The refactored version requires the same core dependencies plus testing tools:

```bash
pip install -r requirements.txt
```

### Step 2: Set Up Configuration

**Old Way (Hardcoded):**
```python
# In analyze_drive.py
DOSSIER_BASE = Path(r"D:\drive-index-starter")
OPENAI_KEY = os.environ.get("OPENAI_KEY", "")
HTML_TEMPLATE = "index_template.html"
HTML_FINAL = "index_interactif.html"
SIGNATURE = "Maitre Jordan"
```

**New Way (Environment-based):**
```bash
# Set environment variables
export BASE_PATH="D:\drive-index-starter"
export OPENAI_KEY="your-api-key"
export HTML_TEMPLATE="index_template.html"
export HTML_FINAL="index_interactif.html"
export SIGNATURE="Maitre Jordan"
```

Or create a `.env` file:
```
BASE_PATH=D:\drive-index-starter
OPENAI_KEY=your-api-key
HTML_TEMPLATE=index_template.html
HTML_FINAL=index_interactif.html
SIGNATURE=Maitre Jordan
```

### Step 3: Update Your Code

**Simple Usage:**

**Before:**
```python
from analyze_drive import walk_and_extract, generer_html

tree, stats = walk_and_extract(DOSSIER_BASE, DOSSIER_BASE)
generer_html(tree, stats)
```

**After:**
```python
from drive_index import DriveIndexApp

app = DriveIndexApp()
html_path = app.run()
print(f"Generated index at: {html_path}")
```

**Advanced Usage with Custom Configuration:**

**Before:**
```python
# Had to modify analyze_drive.py directly
DOSSIER_BASE = Path(r"custom\path")
# ... other changes
```

**After:**
```python
from drive_index import DriveIndexApp, Config

config = Config.from_dict({
    "base_path": "custom\path",
    "openai_key": "your-key",
    "use_openai": True,
    "html_template": "custom_template.html",
    "html_final": "custom_output.html",
    "signature": "Your Name"
})

app = DriveIndexApp(config)
html_path = app.run()
```

### Step 4: Using Individual Components

The refactored version allows using components independently:

**PDF Extraction:**

**Before:**
```python
from analyze_drive import extraire_pdf
text = extraire_pdf("document.pdf")
```

**After:**
```python
from drive_index import PDFExtractor
from drive_index.exceptions import PDFExtractionError

extractor = PDFExtractor()
try:
    text = extractor.extract("document.pdf")
except PDFExtractionError as e:
    print(f"Error: {e}")
```

**AI Summarization:**

**Before:**
```python
from analyze_drive import resume_texte_ia
summary = resume_texte_ia(text)
```

**After:**
```python
from drive_index import OpenAIModel
from drive_index.exceptions import AIServiceError

ai_model = OpenAIModel(api_key="your-key")
try:
    summary = ai_model.summarize(text)
except AIServiceError as e:
    print(f"Error: {e}")
```

**Thumbnail Generation:**

**Before:**
```python
from analyze_drive import generer_miniature
thumb = generer_miniature("image.jpg", "miniatures")
```

**After:**
```python
from drive_index import ThumbnailGenerator
from drive_index.exceptions import ThumbnailGenerationError
from pathlib import Path

thumb_gen = ThumbnailGenerator()
try:
    thumb = thumb_gen.generate("image.jpg", Path("miniatures"))
except ThumbnailGenerationError as e:
    print(f"Error: {e}")
```

### Step 5: Error Handling

**Before:**
```python
# Functions returned error strings
text = extraire_pdf("file.pdf")
if text.startswith("[Erreur extraction PDF]"):
    print("Error occurred")
```

**After:**
```python
# Functions raise exceptions
from drive_index import PDFExtractor
from drive_index.exceptions import PDFExtractionError

extractor = PDFExtractor()
try:
    text = extractor.extract("file.pdf")
except PDFExtractionError as e:
    print(f"Error: {e}")
```

## Feature Mapping

| Original Function | New Equivalent | Notes |
|------------------|----------------|-------|
| `extraire_pdf()` | `PDFExtractor.extract()` | Now raises exceptions |
| `extraire_docx()` | `DOCXExtractor.extract()` | Now raises exceptions |
| `resume_texte_ia()` | `OpenAIModel.summarize()` | More configurable |
| `generer_miniature()` | `ThumbnailGenerator.generate()` | Now raises exceptions |
| `walk_and_extract()` | `FileScanner.scan()` | More modular |
| `generer_html()` | `HTMLGenerator.generate()` | Now raises exceptions |
| `make_zip()` | (Not yet implemented) | Can be added as needed |

## Testing Your Migration

After migrating, verify everything works:

1. **Basic functionality:**
```python
from drive_index import DriveIndexApp

app = DriveIndexApp()
html_path = app.run()
assert Path(html_path).exists()
```

2. **Component testing:**
```python
from drive_index import PDFExtractor

extractor = PDFExtractor()
text = extractor.extract("test.pdf")
assert isinstance(text, str)
```

## Common Issues and Solutions

### Issue 1: Configuration Not Loading

**Problem:** Application uses default configuration instead of environment variables.

**Solution:** Ensure environment variables are set before importing:
```bash
export BASE_PATH="/your/path"
python -m drive_index.app
```

### Issue 2: AI Features Not Working

**Problem:** Summaries are not generated even with OpenAI key.

**Solution:** Verify configuration:
```python
from drive_index import Config

config = Config.from_env()
print(f"OpenAI enabled: {config.use_openai}")
print(f"API Key present: {bool(config.openai_key)}")
```

### Issue 3: Import Errors

**Problem:** Cannot import from drive_index.

**Solution:** Install the package in development mode:
```bash
pip install -e .
```

## Rollback Plan

If you need to rollback to the original version:

1. Keep your original `analyze_drive.py` file
2. Restore original dependencies:
```bash
pip uninstall drive-index
pip install pdfplumber python-docx Pillow openai tqdm notion-client
```
3. Use original script directly:
```python
python analyze_drive.py
```

## Getting Help

If you encounter issues during migration:

1. Check the main README for detailed documentation
2. Review the example usages in each module
3. Examine the type hints and docstrings
4. Consider creating a minimal reproduction case

## Next Steps

After successful migration:

1. Explore individual components for more advanced usage
2. Set up testing for your specific use cases
3. Consider contributing improvements
4. Share feedback on the refactored architecture
