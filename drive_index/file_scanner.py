"""File system scanning implementation."""

import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from tqdm import tqdm
from .exceptions import FileScanningError
from .interfaces import FileExtractor, AIModel, ThumbnailGenerator


class FileScanner:
    """Scanner for traversing directories and extracting file information."""

    def __init__(
        self,
        pdf_extractor: Optional[FileExtractor] = None,
        docx_extractor: Optional[FileExtractor] = None,
        ai_model: Optional[AIModel] = None,
        thumbnail_generator: Optional[ThumbnailGenerator] = None,
        use_ai: bool = False
    ):
        """Initialize file scanner.

        Args:
            pdf_extractor: Extractor for PDF files
            docx_extractor: Extractor for DOCX files
            ai_model: AI model for text summarization
            thumbnail_generator: Generator for image thumbnails
            use_ai: Whether to use AI for summarization
        """
        self.pdf_extractor = pdf_extractor
        self.docx_extractor = docx_extractor
        self.ai_model = ai_model
        self.thumbnail_generator = thumbnail_generator
        self.use_ai = use_ai and ai_model is not None

    def scan(self, base_path: Path) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Scan directory structure and extract file information.

        Args:
            base_path: Root directory to scan

        Returns:
            Tuple of (tree structure, statistics)

        Raises:
            FileScanningError: If scanning fails
        """
        try:
            if not base_path.exists():
                raise FileScanningError(f"Base path does not exist: {base_path}")

            if not base_path.is_dir():
                raise FileScanningError(f"Base path is not a directory: {base_path}")

            return self._walk_and_extract(base_path, base_path)
        except FileScanningError:
            raise
        except Exception as e:
            raise FileScanningError(f"Failed to scan directory {base_path}: {e}")

    def _walk_and_extract(self, current_path: Path, root_path: Path) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Recursively walk directory tree and extract file information.

        Args:
            current_path: Current directory being processed
            root_path: Root directory of the scan

        Returns:
            Tuple of (tree structure, statistics)
        """
        tree = []
        stats = {
            "pdf": 0,
            "docx": 0,
            "images": 0,
            "autres": 0,
            "poids_total": 0,
            "fichiers": 0
        }
        miniatures_folder = root_path / "miniatures"

        try:
            entries = sorted(
                os.scandir(current_path),
                key=lambda e: (not e.is_dir(), e.name.lower())
            )

            for entry in tqdm(entries, desc=f"Scanning {current_path.name}"):
                if entry.is_dir() and entry.name != "miniatures":
                    children, sub_stats = self._walk_and_extract(
                        Path(entry.path), root_path
                    )
                    tree.append({
                        "type": "folder",
                        "name": entry.name,
                        "children": children
                    })
                    for k in stats:
                        stats[k] += sub_stats.get(k, 0)

                elif entry.is_file():
                    file_info = self._process_file(entry, root_path, miniatures_folder)
                    if file_info:
                        tree.append(file_info)
                        self._update_stats(stats, file_info)

            return tree, stats

        except Exception as e:
            raise FileScanningError(f"Error processing directory {current_path}: {e}")

    def _process_file(self, entry, root_path: Path, miniatures_folder: Path) -> Optional[Dict[str, Any]]:
        """Process a single file and extract its information.

        Args:
            entry: DirEntry object for the file
            root_path: Root directory of the scan
            miniatures_folder: Folder for storing thumbnails

        Returns:
            Dictionary with file information or None if processing fails
        """
        try:
            ext = entry.name.lower().split(".")[-1]
            file_info = {
                "type": "file",
                "name": entry.name,
                "size": os.path.getsize(entry.path),
                "ext": ext,
                "path": str(Path(entry.path).relative_to(root_path))
            }

            # Process based on file type
            if ext == "pdf" and self.pdf_extractor:
                file_info.update(self._process_pdf(entry.path))
            elif ext == "docx" and self.docx_extractor:
                file_info.update(self._process_docx(entry.path))
            elif ext in ["jpg", "jpeg", "png", "bmp", "gif"] and self.thumbnail_generator:
                file_info.update(self._process_image(entry.path, miniatures_folder))

            return file_info

        except Exception as e:
            print(f"Warning: Failed to process file {entry.name}: {e}")
            return None

    def _process_pdf(self, file_path: str) -> Dict[str, Any]:
        """Process a PDF file.

        Args:
            file_path: Path to the PDF file

        Returns:
            Dictionary with extracted information
        """
        texte = self.pdf_extractor.extract(file_path)
        result = {"extrait": texte[:800]}

        if self.use_ai:
            result["resume"] = self.ai_model.summarize(texte)

        return result

    def _process_docx(self, file_path: str) -> Dict[str, Any]:
        """Process a DOCX file.

        Args:
            file_path: Path to the DOCX file

        Returns:
            Dictionary with extracted information
        """
        texte = self.docx_extractor.extract(file_path)
        result = {"extrait": texte[:800]}

        if self.use_ai:
            result["resume"] = self.ai_model.summarize(texte)

        return result

    def _process_image(self, image_path: str, miniatures_folder: Path) -> Dict[str, Any]:
        """Process an image file.

        Args:
            image_path: Path to the image file
            miniatures_folder: Folder for storing thumbnails

        Returns:
            Dictionary with extracted information
        """
        thumb = self.thumbnail_generator.generate(image_path, miniatures_folder)
        return {"miniature": thumb} if thumb else {}

    def _update_stats(self, stats: Dict[str, Any], file_info: Dict[str, Any]) -> None:
        """Update statistics based on file information.

        Args:
            stats: Statistics dictionary to update
            file_info: File information dictionary
        """
        stats["poids_total"] += file_info["size"]
        stats["fichiers"] += 1

        ext = file_info["ext"]
        if ext == "pdf":
            stats["pdf"] += 1
        elif ext == "docx":
            stats["docx"] += 1
        elif ext in ["jpg", "jpeg", "png", "bmp", "gif"]:
            stats["images"] += 1
        else:
            stats["autres"] += 1
