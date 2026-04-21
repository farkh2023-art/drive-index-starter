"""
Integration test: full pipeline on a temp directory without OpenAI.
"""
import json
import pytest
from pathlib import Path
from docx import Document
from PIL import Image
import analyze_drive as ad


@pytest.fixture
def full_dir(tmp_path):
    doc = Document()
    doc.add_paragraph("Document Word de test.")
    doc.save(tmp_path / "rapport.docx")

    img = Image.new("RGB", (400, 300), color=(0, 128, 255))
    img.save(tmp_path / "photo.png")

    (tmp_path / "notes.txt").write_text("Notes importantes.", encoding="utf-8")
    (tmp_path / "archive.zip").write_bytes(b"PK")

    sub = tmp_path / "sous_dossier"
    sub.mkdir()
    (sub / "fiche.txt").write_text("Fiche dans sous-dossier.", encoding="utf-8")

    return tmp_path


@pytest.fixture
def template(tmp_path):
    path = tmp_path / "tmpl.html"
    path.write_text(
        "<html><script>\n"
        "// Cette partie sera remplie automatiquement par le script Python\n"
        "    // ... (ne rien changer ici)\n"
        "</script></html>",
        encoding="utf-8",
    )
    return path


def test_full_pipeline(full_dir, template, monkeypatch):
    monkeypatch.setattr(ad, "UTILISER_OPENAI", False)
    output = full_dir / "index.html"

    cache = {}
    tree, stats = ad.walk_and_extract(full_dir, full_dir, cache)
    ad.generer_html(tree, stats, template=str(template), output=str(output))

    assert stats["docx"] == 1
    assert stats["images"] == 1
    assert stats["txt"] >= 2
    assert stats["autres"] >= 1
    assert stats["fichiers"] >= 5
    assert output.exists()

    html = output.read_text(encoding="utf-8")
    assert "rapport.docx" in html
    assert "photo.png" in html
    assert "folderTree" in html


def test_second_run_uses_cache(full_dir, monkeypatch):
    monkeypatch.setattr(ad, "UTILISER_OPENAI", False)

    cache = {}
    tree1, stats1 = ad.walk_and_extract(full_dir, full_dir, cache)

    cache2 = dict(cache)
    tree2, stats2 = ad.walk_and_extract(full_dir, full_dir, cache2)

    assert stats1["fichiers"] == stats2["fichiers"]
    names1 = {e["name"] for e in tree1 if e["type"] == "file"}
    names2 = {e["name"] for e in tree2 if e["type"] == "file"}
    assert names1 == names2
