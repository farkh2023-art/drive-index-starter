"""HTML generation implementation."""

import json
from pathlib import Path
from typing import Dict, Any, List
from .exceptions import HTMLGenerationError


class HTMLGenerator:
    """Generator for creating HTML index files."""

    def __init__(self, template_path: str = "index_template.html", 
                 output_path: str = "index_interactif.html"):
        """Initialize HTML generator.

        Args:
            template_path: Path to HTML template file
            output_path: Path for generated HTML file
        """
        self.template_path = Path(template_path)
        self.output_path = Path(output_path)

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
        try:
            # Read template
            if not self.template_path.exists():
                raise HTMLGenerationError(f"Template file not found: {self.template_path}")

            with open(self.template_path, "r", encoding="utf-8") as f:
                html = f.read()

            # Replace placeholder with actual data
            data_js = (
                f"const folderTree = {json.dumps(tree, ensure_ascii=False)};\n"
                f"    const dossierStats = {json.dumps(stats, ensure_ascii=False)};"
            )

            html = html.replace(
                "// Cette partie sera remplie automatiquement par le script Python\n    // ... (ne rien changer ici)",
                data_js
            )

            # Write output
            self.output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.output_path, "w", encoding="utf-8") as f:
                f.write(html)

            print(
                f"[OK] {self.output_path} generated "
                f"({stats['fichiers']} files, "
                f"{round(stats['poids_total']/1024/1024, 1)} MB)"
            )

            return str(self.output_path)

        except HTMLGenerationError:
            raise
        except Exception as e:
            raise HTMLGenerationError(f"Failed to generate HTML: {e}")
