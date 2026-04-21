"""Interface definitions for Drive Index components."""

from typing import Protocol, Dict, Any, List, Optional
from pathlib import Path


class FileExtractor(Protocol):
    """Protocol for file text extraction."""

    def extract(self, file_path: str) -> str:
        """Extract text from a file.

        Args:
            file_path: Path to the file to extract text from

        Returns:
            Extracted text content

        Raises:
            DriveIndexError: If extraction fails
        """
        ...


class AIModel(Protocol):
    """Protocol for AI text summarization."""

    def summarize(self, text: str, prompt: str = "") -> str:
        """Summarize text using AI.

        Args:
            text: Text to summarize
            prompt: Optional prompt to guide summarization

        Returns:
            Summarized text

        Raises:
            AIServiceError: If AI service fails
        """
        ...


class ThumbnailGenerator(Protocol):
    """Protocol for thumbnail generation."""

    def generate(self, image_path: str, output_folder: Path) -> Optional[str]:
        """Generate thumbnail for an image.

        Args:
            image_path: Path to the source image
            output_folder: Directory to save thumbnail in

        Returns:
            Path to generated thumbnail, or None if generation fails

        Raises:
            ThumbnailGenerationError: If thumbnail generation fails
        """
        ...


class FileScanner(Protocol):
    """Protocol for file system scanning."""

    def scan(self, base_path: Path) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Scan directory structure and extract file information.

        Args:
            base_path: Root directory to scan

        Returns:
            Tuple of (tree structure, statistics)

        Raises:
            FileScanningError: If scanning fails
        """
        ...


class HTMLGenerator(Protocol):
    """Protocol for HTML generation."""

    def generate(self, tree: List[Dict[str, Any]], stats: Dict[str, Any]) -> str:
        """Generate HTML from file tree and statistics.

        Args:
            tree: File tree structure
            stats: File statistics

        Returns:
            Path to generated HTML file

        Raises:
            HTMLGenerationError: If HTML generation fails
        """
        ...
