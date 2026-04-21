"""File text extraction implementations."""

from typing import Optional
from .exceptions import PDFExtractionError, DOCXExtractionError


class FileExtractor:
    """Base class for file extractors."""

    def extract(self, file_path: str) -> str:
        """Extract text from a file.

        Args:
            file_path: Path to the file to extract text from

        Returns:
            Extracted text content

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement extract()")


class PDFExtractor(FileExtractor):
    """Extractor for PDF files."""

    def extract(self, file_path: str) -> str:
        """Extract text from a PDF file.

        Args:
            file_path: Path to the PDF file

        Returns:
            Extracted text content

        Raises:
            PDFExtractionError: If extraction fails
        """
        try:
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                text = "".join(page.extract_text() or "" for page in pdf.pages)
            return text.strip()
        except Exception as e:
            raise PDFExtractionError(f"Failed to extract PDF from {file_path}: {e}")


class DOCXExtractor(FileExtractor):
    """Extractor for DOCX files."""

    def extract(self, file_path: str) -> str:
        """Extract text from a DOCX file.

        Args:
            file_path: Path to the DOCX file

        Returns:
            Extracted text content

        Raises:
            DOCXExtractionError: If extraction fails
        """
        try:
            from docx import Document
            doc = Document(file_path)
            text = "\n".join([p.text for p in doc.paragraphs])
            return text.strip()
        except Exception as e:
            raise DOCXExtractionError(f"Failed to extract DOCX from {file_path}: {e}")


class ExtractorFactory:
    """Factory for creating appropriate extractors."""

    _extractors = {
        'pdf': PDFExtractor,
        'docx': DOCXExtractor,
    }

    @classmethod
    def get_extractor(cls, file_extension: str) -> Optional[FileExtractor]:
        """Get an extractor for a given file extension.

        Args:
            file_extension: File extension (e.g., 'pdf', 'docx')

        Returns:
            Extractor instance or None if no extractor available
        """
        extractor_class = cls._extractors.get(file_extension.lower())
        return extractor_class() if extractor_class else None
