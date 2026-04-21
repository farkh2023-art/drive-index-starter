import json
import zipfile
import pytest
from pathlib import Path
from unittest.mock import patch
import analyze_drive as ad


class TestMakeZip:
    def test_creates_zip(self, tmp_path):
        (tmp_path / "a.txt").write_text("hello")
        (tmp_path / "b.txt").write_text("world")
        zip_path = str(tmp_path / "out.zip")

        result = ad.make_zip(tmp_path, zip_path)

        assert Path(result).exists()
        with zipfile.ZipFile(result) as z:
            names = z.namelist()
        assert "a.txt" in names
        assert "b.txt" in names

    def test_preserves_subdirectory_structure(self, tmp_path):
        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "nested.txt").write_text("nested")
        zip_path = str(tmp_path / "out.zip")

        ad.make_zip(tmp_path, zip_path)

        with zipfile.ZipFile(zip_path) as z:
            names = z.namelist()
        assert any("nested.txt" in n for n in names)


class TestGenererHtml:
    def test_injects_data(self, tmp_path, minimal_template):
        output = tmp_path / "out.html"
        tree = [{"type": "file", "name": "doc.pdf", "ext": "pdf", "size": 100, "path": "doc.pdf"}]
        stats = {"fichiers": 1, "pdf": 1, "docx": 0, "txt": 0, "images": 0, "autres": 0, "poids_total": 100}

        ad.generer_html(tree, stats, template=str(minimal_template), output=str(output))

        html = output.read_text(encoding="utf-8")
        assert "folderTree" in html
        assert "doc.pdf" in html
        assert "dossierStats" in html

    def test_valid_json_injected(self, tmp_path, minimal_template):
        output = tmp_path / "out.html"
        tree = [{"type": "folder", "name": "dossier", "children": []}]
        stats = {"fichiers": 0, "pdf": 0, "docx": 0, "txt": 0, "images": 0, "autres": 0, "poids_total": 0}

        ad.generer_html(tree, stats, template=str(minimal_template), output=str(output))

        html = output.read_text(encoding="utf-8")
        json_start = html.index("const folderTree = ") + len("const folderTree = ")
        json_end = html.index(";", json_start)
        parsed = json.loads(html[json_start:json_end])
        assert parsed[0]["name"] == "dossier"


class TestWalkAndExtract:
    def test_counts_files(self, sample_dir, monkeypatch):
        monkeypatch.setattr(ad, "UTILISER_OPENAI", False)
        tree, stats = ad.walk_and_extract(sample_dir, sample_dir)

        assert stats["fichiers"] > 0
        assert stats["poids_total"] > 0

    def test_counts_images(self, sample_dir, monkeypatch):
        monkeypatch.setattr(ad, "UTILISER_OPENAI", False)
        _, stats = ad.walk_and_extract(sample_dir, sample_dir)

        assert stats["images"] >= 1

    def test_counts_docx(self, sample_dir, monkeypatch):
        monkeypatch.setattr(ad, "UTILISER_OPENAI", False)
        _, stats = ad.walk_and_extract(sample_dir, sample_dir)

        assert stats["docx"] >= 1

    def test_counts_txt(self, sample_dir, monkeypatch):
        monkeypatch.setattr(ad, "UTILISER_OPENAI", False)
        _, stats = ad.walk_and_extract(sample_dir, sample_dir)

        assert stats["txt"] >= 1

    def test_cache_hit_skips_extraction(self, tmp_path, monkeypatch):
        monkeypatch.setattr(ad, "UTILISER_OPENAI", False)
        txt_file = tmp_path / "cached.txt"
        txt_file.write_text("contenu", encoding="utf-8")
        stat = txt_file.stat()

        cache = {
            "cached.txt": {
                "mtime": stat.st_mtime,
                "size": stat.st_size,
                "extrait": "extrait depuis cache",
                "resume": "resume depuis cache",
            }
        }

        with patch.object(ad, "extraire_txt") as mock_extract:
            tree, _ = ad.walk_and_extract(tmp_path, tmp_path, cache)

        mock_extract.assert_not_called()
        file_entry = next(e for e in tree if e["name"] == "cached.txt")
        assert file_entry["extrait"] == "extrait depuis cache"

    def test_cache_miss_calls_extraction(self, tmp_path, monkeypatch):
        monkeypatch.setattr(ad, "UTILISER_OPENAI", False)
        txt_file = tmp_path / "new.txt"
        txt_file.write_text("nouveau contenu", encoding="utf-8")

        cache = {}
        tree, _ = ad.walk_and_extract(tmp_path, tmp_path, cache)

        assert "new.txt" in cache
        file_entry = next(e for e in tree if e["name"] == "new.txt")
        assert "nouveau contenu" in file_entry["extrait"]


class TestCache:
    def test_charger_cache_missing_file(self, tmp_path, monkeypatch):
        monkeypatch.setattr(ad, "CACHE_FILE", str(tmp_path / "absent.json"))
        assert ad.charger_cache() == {}

    def test_sauvegarder_et_charger(self, tmp_path, monkeypatch):
        cache_path = str(tmp_path / "cache.json")
        monkeypatch.setattr(ad, "CACHE_FILE", cache_path)

        data = {"file.pdf": {"mtime": 1.0, "size": 100, "extrait": "x", "resume": "y"}}
        ad.sauvegarder_cache(data)
        loaded = ad.charger_cache()

        assert loaded == data
