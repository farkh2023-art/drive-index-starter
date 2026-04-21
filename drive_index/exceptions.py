"""Custom exceptions for Drive Index."""


class DriveIndexError(Exception):
    """Base exception for drive-index errors."""
    pass


class PDFExtractionError(DriveIndexError):
    """Raised when PDF extraction fails."""
    pass


class DOCXExtractionError(DriveIndexError):
    """Raised when DOCX extraction fails."""
    pass


class ThumbnailGenerationError(DriveIndexError):
    """Raised when thumbnail generation fails."""
    pass


class AIServiceError(DriveIndexError):
    """Raised when AI service fails."""
    pass


class FileScanningError(DriveIndexError):
    """Raised when file scanning fails."""
    pass


class HTMLGenerationError(DriveIndexError):
    """Raised when HTML generation fails."""
    pass
