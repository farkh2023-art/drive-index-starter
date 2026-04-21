import os
import json
import logging
import zipfile
from pathlib import Path
import pdfplumber
from docx import Document
from PIL import Image
from tqdm import tqdm
from notion_client import Client
from dotenv import load_dotenv
import openai

load_dotenv()

DOSSIER_BASE = Path(os.environ.get("DOSSIER_BASE", r"D:\drive-index-starter"))
OPENAI_KEY = os.environ.get("OPENAI_KEY", "")
UTILISER_OPENAI = bool(OPENAI_KEY)
NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "")
DATABASE_ID = os.environ.get("DATABASE_ID", "")
HTML_TEMPLATE = "index_template.html"
HTML_FINAL = "index_interactif.html"
SIGNATURE = os.environ.get("SIGNATURE", "Maitre Jordan")
CACHE_FILE = "cache.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler("analyze.log", encoding="utf-8"), logging.StreamHandler()],
)
log = logging.getLogger(__name__)


# --- Cache ---

def charger_cache():
    if Path(CACHE_FILE).exists():
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def sauvegarder_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


# --- Extraction ---

def resume_texte_ia(texte, prompt="Resume ce document en 4 lignes :"):
    if not OPENAI_KEY:
        return ""
    try:
        client = openai.OpenAI(api_key=OPENAI_KEY)
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": prompt},
                      {"role": "user", "content": texte[:5000]}],
            max_tokens=220,
            temperature=0.5,
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        log.warning("Erreur IA : %s", e)
        return f"[Erreur IA] {e}"

def extraire_pdf(pdf_path):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            txt = "".join(page.extract_text() or "" for page in pdf.pages)
        return txt.strip()
    except Exception as e:
        log.warning("Erreur extraction PDF %s : %s", pdf_path, e)
        return f"[Erreur extraction PDF] {e}"

def extraire_docx(docx_path):
    try:
        doc = Document(docx_path)
        txt = "\n".join(p.text for p in doc.paragraphs)
        return txt.strip()
    except Exception as e:
        log.warning("Erreur extraction DOCX %s : %s", docx_path, e)
        return f"[Erreur extraction DOCX] {e}"

def extraire_txt(txt_path):
    try:
        with open(txt_path, "r", encoding="utf-8", errors="replace") as f:
            return f.read().strip()
    except Exception as e:
        log.warning("Erreur extraction TXT %s : %s", txt_path, e)
        return f"[Erreur extraction TXT] {e}"

def generer_miniature(image_path, out_folder):
    try:
        out_folder.mkdir(exist_ok=True)
        with Image.open(image_path) as img:
            img.thumbnail((260, 180))
            thumb_path = out_folder / (Path(image_path).stem + "_thumb.jpg")
            img.save(thumb_path, "JPEG")
        return str(thumb_path)
    except Exception as e:
        log.warning("Erreur miniature %s : %s", image_path, e)
        return ""


# --- Pipeline ---

def walk_and_extract(base_path, racine, cache=None):
    if cache is None:
        cache = {}
    tree = []
    stats = {"pdf": 0, "docx": 0, "txt": 0, "images": 0, "autres": 0, "poids_total": 0, "fichiers": 0}
    miniatures_folder = racine / "miniatures"

    entries = sorted(os.scandir(base_path), key=lambda e: (not e.is_dir(), e.name.lower()))
    for entry in tqdm(entries, leave=False):
        if entry.is_dir() and entry.name not in ("miniatures", "__pycache__", ".mypy_cache"):
            children, sub_stats = walk_and_extract(Path(entry.path), racine, cache)
            tree.append({"type": "folder", "name": entry.name, "children": children})
            for k in stats:
                stats[k] += sub_stats.get(k, 0)
        elif entry.is_file():
            ext = entry.name.lower().rsplit(".", 1)[-1]
            stat = entry.stat()
            cache_key = str(Path(entry.path).relative_to(racine))
            file_info = {
                "type": "file",
                "name": entry.name,
                "size": stat.st_size,
                "ext": ext,
                "path": cache_key,
            }
            stats["poids_total"] += stat.st_size
            stats["fichiers"] += 1

            cached = cache.get(cache_key, {})
            cache_hit = (
                cached.get("mtime") == stat.st_mtime
                and cached.get("size") == stat.st_size
            )

            if ext == "pdf":
                stats["pdf"] += 1
                if cache_hit:
                    file_info["extrait"] = cached.get("extrait", "")
                    file_info["resume"] = cached.get("resume", "")
                else:
                    texte = extraire_pdf(entry.path)
                    file_info["extrait"] = texte[:800]
                    file_info["resume"] = resume_texte_ia(texte) if UTILISER_OPENAI else ""
                    cache[cache_key] = {"mtime": stat.st_mtime, "size": stat.st_size,
                                        "extrait": file_info["extrait"], "resume": file_info["resume"]}
            elif ext == "docx":
                stats["docx"] += 1
                if cache_hit:
                    file_info["extrait"] = cached.get("extrait", "")
                    file_info["resume"] = cached.get("resume", "")
                else:
                    texte = extraire_docx(entry.path)
                    file_info["extrait"] = texte[:800]
                    file_info["resume"] = resume_texte_ia(texte) if UTILISER_OPENAI else ""
                    cache[cache_key] = {"mtime": stat.st_mtime, "size": stat.st_size,
                                        "extrait": file_info["extrait"], "resume": file_info["resume"]}
            elif ext == "txt":
                stats["txt"] += 1
                if cache_hit:
                    file_info["extrait"] = cached.get("extrait", "")
                    file_info["resume"] = cached.get("resume", "")
                else:
                    texte = extraire_txt(entry.path)
                    file_info["extrait"] = texte[:800]
                    file_info["resume"] = resume_texte_ia(texte) if UTILISER_OPENAI else ""
                    cache[cache_key] = {"mtime": stat.st_mtime, "size": stat.st_size,
                                        "extrait": file_info["extrait"], "resume": file_info["resume"]}
            elif ext in ("jpg", "jpeg", "png", "bmp", "gif"):
                stats["images"] += 1
                thumb = generer_miniature(Path(entry.path), miniatures_folder)
                file_info["miniature"] = thumb
            else:
                stats["autres"] += 1

            tree.append(file_info)
    return tree, stats

def make_zip(src_folder, zip_name="dossier_archive.zip"):
    with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as archive:
        for foldername, subfolders, filenames in os.walk(src_folder):
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                arcname = os.path.relpath(file_path, src_folder)
                archive.write(file_path, arcname)
    return zip_name

def generer_html(tree, stats, template=None, output=None):
    template = template or HTML_TEMPLATE
    output = output or HTML_FINAL
    with open(template, "r", encoding="utf-8") as f:
        html = f.read()
    html = html.replace(
        "// Cette partie sera remplie automatiquement par le script Python\n    // ... (ne rien changer ici)",
        f"const folderTree = {json.dumps(tree, ensure_ascii=False)};\n    const dossierStats = {json.dumps(stats, ensure_ascii=False)};",
    )
    with open(output, "w", encoding="utf-8") as f:
        f.write(html)
    log.info("HTML genere : %s (%d fichiers, %.1f Mo)", output, stats["fichiers"], stats["poids_total"] / 1024 / 1024)


if __name__ == "__main__":
    log.info("Scan de : %s", DOSSIER_BASE)
    cache = charger_cache()
    tree, stats = walk_and_extract(DOSSIER_BASE, DOSSIER_BASE, cache)
    sauvegarder_cache(cache)
    generer_html(tree, stats)
