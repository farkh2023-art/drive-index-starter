"""Main application module for Drive Index."""

from pathlib import Path
from typing import Optional
from .config import Config
from .extractors import PDFExtractor, DOCXExtractor, ExtractorFactory
from .ai_service import OpenAIModel, MockAIModel, AIModelFactory
from .thumbnail_generator import ThumbnailGenerator
from .file_scanner import FileScanner
from .html_generator import HTMLGenerator
from .exceptions import DriveIndexError


class DriveIndexApp:
    """Main application class for Drive Index."""

    def __init__(self, config: Optional[Config] = None):
        """Initialize Drive Index application.

        Args:
            config: Configuration object. If None, loads from environment.
        """
        self.config = config or Config.from_env()
        self._setup_components()

    def _setup_components(self):
        """Set up application components based on configuration."""
        # Initialize extractors
        self.pdf_extractor = PDFExtractor()
        self.docx_extractor = DOCXExtractor()

        # Initialize AI model if enabled
        if self.config.use_openai:
            self.ai_model = OpenAIModel(api_key=self.config.openai_key)
        else:
            self.ai_model = None

        # Initialize thumbnail generator
        self.thumbnail_generator = ThumbnailGenerator()

        # Initialize file scanner
        self.file_scanner = FileScanner(
            pdf_extractor=self.pdf_extractor,
            docx_extractor=self.docx_extractor,
            ai_model=self.ai_model,
            thumbnail_generator=self.thumbnail_generator,
            use_ai=self.config.use_openai
        )

        # Initialize HTML generator
        self.html_generator = HTMLGenerator(
            template_path=self.config.html_template,
            output_path=self.config.html_final
        )

    def run(self) -> str:
        """Run the Drive Index application.

        Returns:
            Path to generated HTML file

        Raises:
            DriveIndexError: If application fails
        """
        try:
            print(f"Scanning: {self.config.base_path}")

            # Scan directory
            tree, stats = self.file_scanner.scan(self.config.base_path)

            # Generate HTML
            html_path = self.html_generator.generate(tree, stats)

            return html_path

        except DriveIndexError:
            raise
        except Exception as e:
            raise DriveIndexError(f"Application failed: {e}")


def main():
    """Main entry point for the application."""
    try:
        app = DriveIndexApp()
        html_path = app.run()
        print(f"\nSuccess! Generated index at: {html_path}")
    except DriveIndexError as e:
        print(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
