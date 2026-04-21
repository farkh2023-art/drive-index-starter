"""Setup configuration for Drive Index package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README_REFACTORED.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="drive-index",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A tool for indexing and organizing document collections",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/drive-index",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pdfplumber",
        "python-docx",
        "Pillow",
        "openai",
        "tqdm",
        "notion-client",
        "python-dotenv",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.11.1",
        ],
    },
    entry_points={
        "console_scripts": [
            "drive-index=drive_index.app:main",
        ],
    },
)
