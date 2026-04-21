# Drive Index - Refactored Version

A refactored, more maintainable version of the Drive Index tool with improved testability, modularity, and error handling.

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Testing](#testing)
- [Migration Guide](#migration-guide)

## ✨ Features

- **Modular Architecture**: Clear separation of concerns with isolated components
- **Flexible Configuration**: Environment-based configuration with multiple sources
- **Better Error Handling**: Custom exceptions with clear error messages
- **Testable Design**: Dependency injection and mockable components
- **Type Hints**: Full type annotations for better IDE support
- **Well-Documented**: Comprehensive docstrings for all components

## 🏗️ Architecture

The project follows a layered architecture with clear interfaces between components:

```
┌─────────────────────────────────────┐
│         DriveIndexApp              │
│   (Application Orchestration)      │
└──────────────┬──────────────────────┘
               │
       ┌───────┴────────┐
       │                │
┌──────▼──────┐  ┌─────▼──────┐
│ FileScanner │  │HTMLGenerator│
└──────┬──────┘  └────────────┘
       │
  ┌────┴────┬──────────┬──────────┐
  ▼         ▼          ▼          ▼
Extractors  AIModel  Thumbnail  Config
```

### Key Components

1. **Config**: Centralized configuration management
2. **Extractors**: File text extraction (PDF, DOCX)
3. **AIModel**: Text summarization using AI
4. **ThumbnailGenerator**: Image thumbnail creation
5. **FileScanner**: Directory traversal and file processing
6. **HTMLGenerator**: HTML index file generation
7. **DriveIndexApp**: Main application orchestrator

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone or download the repository:
```bash
git clone <repository-url>
cd drive-index-starter
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

Configuration can be provided through environment variables:

```bash
# Required for AI features
export OPENAI_KEY="your-openai-api-key"

# Optional settings
export BASE_PATH="/path/to/your/documents"
export HTML_TEMPLATE="index_template.html"
export HTML_FINAL="index_interactif.html"
export SIGNATURE="Your Name"
```

### Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `BASE_PATH` | Root directory to scan | Current directory |
| `OPENAI_KEY` | OpenAI API key for summarization | Empty (AI disabled) |
| `NOTION_TOKEN` | Notion integration token | Empty |
| `DATABASE_ID` | Notion database ID | Empty |
| `HTML_TEMPLATE` | Path to HTML template | index_template.html |
| `HTML_FINAL` | Output HTML file path | index_interactif.html |
| `SIGNATURE` | Signature for generated content | Default Signature |

## 🚀 Usage

### Basic Usage

```python
from drive_index import DriveIndexApp

# Create and run the application
app = DriveIndexApp()
html_path = app.run()
print(f"Generated index at: {html_path}")
```

### Command Line Usage

```bash
# Using environment variables
python -m drive_index.app

# Or with a .env file
python -m drive_index.app
```

### Advanced Usage with Custom Configuration

```python
from drive_index import DriveIndexApp, Config
from pathlib import Path

# Create custom configuration
config = Config.from_dict({
    "base_path": "/path/to/documents",
    "openai_key": "your-api-key",
    "use_openai": True,
    "html_template": "custom_template.html",
    "html_final": "custom_output.html",
    "signature": "Your Name"
})

# Run with custom configuration
app = DriveIndexApp(config)
html_path = app.run()
```

### Using Individual Components

```python
from drive_index import (
    PDFExtractor,
    DOCXExtractor,
    OpenAIModel,
    ThumbnailGenerator,
    FileScanner,
    HTMLGenerator
)

# Extract text from files
pdf_extractor = PDFExtractor()
text = pdf_extractor.extract("document.pdf")

# Summarize text with AI
ai_model = OpenAIModel(api_key="your-api-key")
summary = ai_model.summarize(text)

# Generate thumbnail
thumb_gen = ThumbnailGenerator()
thumb_path = thumb_gen.generate("image.jpg", Path("thumbnails"))
```

## 📁 Project Structure

```
drive-index-starter/
├── drive_index/              # Main package
│   ├── __init__.py          # Package initialization
│   ├── app.py               # Main application
│   ├── config.py            # Configuration management
│   ├── exceptions.py        # Custom exceptions
│   ├── interfaces.py        # Component interfaces
│   ├── extractors.py        # File extractors
│   ├── ai_service.py        # AI services
│   ├── thumbnail_generator.py # Thumbnail generation
│   ├── file_scanner.py      # File system scanning
│   └── html_generator.py    # HTML generation
├── tests/                   # Test suite (to be created)
├── requirements.txt         # Python dependencies
├── README.md               # This file
└── setup.py                # Package setup (optional)
```

## 🧪 Testing

The refactored codebase is designed with testability in mind:

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=drive_index --cov-report=html

# Run specific test file
pytest tests/test_extractors.py

# Run with verbose output
pytest -v
```

### Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── test_config.py          # Configuration tests
├── test_extractors.py      # Extractor tests
├── test_ai_service.py      # AI service tests
├── test_thumbnail_generator.py
├── test_file_scanner.py    # Scanner tests
├── test_html_generator.py  # HTML generator tests
└── test_integration.py     # Integration tests
```

### Writing Tests

Example test for PDF extractor:

```python
import pytest
from drive_index import PDFExtractor
from drive_index.exceptions import PDFExtractionError

def test_pdf_extractor_success(tmp_path):
    """Test successful PDF extraction."""
    extractor = PDFExtractor()
    # Create test PDF...
    result = extractor.extract("test.pdf")
    assert result == "expected text"

def test_pdf_extractor_failure():
    """Test PDF extraction failure handling."""
    extractor = PDFExtractor()
    with pytest.raises(PDFExtractionError):
        extractor.extract("nonexistent.pdf")
```

## 🔄 Migration Guide

### From Original Version

If you're migrating from the original `analyze_drive.py`:

1. **Install new dependencies**:
```bash
pip install -r requirements.txt
```

2. **Set up environment variables**:
```bash
export OPENAI_KEY="your-api-key"
export BASE_PATH="/path/to/documents"
```

3. **Update your code**:
```python
# Old way
from analyze_drive import walk_and_extract, generer_html
tree, stats = walk_and_extract(DOSSIER_BASE, DOSSIER_BASE)
generer_html(tree, stats)

# New way
from drive_index import DriveIndexApp
app = DriveIndexApp()
app.run()
```

4. **Configuration migration**:
```python
# Old way (hardcoded)
DOSSIER_BASE = Path(r"D:\drive-index-starter")
OPENAI_KEY = os.environ.get("OPENAI_KEY", "")

# New way (environment-based)
export BASE_PATH="D:\drive-index-starter"
export OPENAI_KEY="your-key"
```

## 🤝 Contributing

Contributions are welcome! Please ensure:

1. All tests pass: `pytest`
2. Code follows PEP 8 style guidelines
3. New features include tests
4. Documentation is updated

## 📝 License

[Add your license information here]

## 🙏 Acknowledgments

Original version and inspiration for this refactored implementation.
