import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
import analyze_drive as ad


class TestExtrairePdf:
    def test_success(self):
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Contenu PDF test."
        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = lambda s: s
        mock_pdf.__exit__ = MagicMock(return_value=False)

        with patch("analyze_drive.pdfplumber.open", return_value=mock_pdf):
            result = ad.extraire_pdf("fake.pdf")

        assert result == "Contenu PDF test."

    def test_multiple_pages(self):
        pages = [MagicMock(), MagicMock()]
        pages[0].extract_text.return_value = "Page 1. "
        pages[1].extract_text.return_value = "Page 2."
        mock_pdf = MagicMock()
        mock_pdf.pages = pages
        mock_pdf.__enter__ = lambda s: s
        mock_pdf.__exit__ = MagicMock(return_value=False)

        with patch("analyze_drive.pdfplumber.open", return_value=mock_pdf):
            result = ad.extraire_pdf("fake.pdf")

        assert "Page 1." in result
        assert "Page 2." in result

    def test_empty_pages(self):
        mock_page = MagicMock()
        mock_page.extract_text.return_value = None
        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = lambda s: s
        mock_pdf.__exit__ = MagicMock(return_value=False)

        with patch("analyze_drive.pdfplumber.open", return_value=mock_pdf):
            result = ad.extraire_pdf("fake.pdf")

        assert result == ""

    def test_error_returns_message(self):
        with patch("analyze_drive.pdfplumber.open", side_effect=Exception("fichier corrompu")):
            result = ad.extraire_pdf("bad.pdf")

        assert result.startswith("[Erreur extraction PDF]")


class TestExtraireDocx:
    def test_success(self, sample_docx):
        result = ad.extraire_docx(sample_docx)
        assert "Ceci est un document test." in result
        assert "Deuxieme paragraphe." in result

    def test_error_returns_message(self):
        result = ad.extraire_docx("inexistant.docx")
        assert result.startswith("[Erreur extraction DOCX]")


class TestExtraireTxt:
    def test_success(self, sample_txt):
        result = ad.extraire_txt(sample_txt)
        assert "Contenu texte de test." in result

    def test_error_returns_message(self):
        result = ad.extraire_txt("inexistant.txt")
        assert result.startswith("[Erreur extraction TXT]")


class TestGenererMiniature:
    def test_creates_thumbnail(self, sample_image, tmp_path):
        out = tmp_path / "thumbs"
        result = ad.generer_miniature(sample_image, out)

        assert result != ""
        thumb = Path(result)
        assert thumb.exists()

    def test_thumbnail_dimensions(self, sample_image, tmp_path):
        out = tmp_path / "thumbs"
        result = ad.generer_miniature(sample_image, out)

        from PIL import Image
        with Image.open(result) as img:
            assert img.width <= 260
            assert img.height <= 180

    def test_error_returns_empty(self, tmp_path):
        result = ad.generer_miniature("inexistant.png", tmp_path / "thumbs")
        assert result == ""
