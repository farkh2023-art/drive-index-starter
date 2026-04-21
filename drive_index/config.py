"""Configuration management for Drive Index."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Config:
    """Configuration settings for Drive Index."""

    base_path: Path
    openai_key: str
    use_openai: bool
    notion_token: str
    database_id: str
    html_template: str
    html_final: str
    signature: str

    @classmethod
    def from_env(cls, base_path: Optional[Path] = None) -> 'Config':
        """Create configuration from environment variables.

        Args:
            base_path: Optional base path override. If not provided,
                      uses BASE_PATH env var or current directory.

        Returns:
            Config instance with values from environment
        """
        openai_key = os.environ.get("OPENAI_KEY", "")
        return cls(
            base_path=base_path or Path(os.environ.get("BASE_PATH", ".")),
            openai_key=openai_key,
            use_openai=bool(openai_key),
            notion_token=os.environ.get("NOTION_TOKEN", ""),
            database_id=os.environ.get("DATABASE_ID", ""),
            html_template=os.environ.get("HTML_TEMPLATE", "index_template.html"),
            html_final=os.environ.get("HTML_FINAL", "index_interactif.html"),
            signature=os.environ.get("SIGNATURE", "Default Signature")
        )

    @classmethod
    def from_dict(cls, config_dict: dict) -> 'Config':
        """Create configuration from dictionary.

        Args:
            config_dict: Dictionary containing configuration values

        Returns:
            Config instance with values from dictionary
        """
        openai_key = config_dict.get("openai_key", "")
        return cls(
            base_path=Path(config_dict.get("base_path", ".")),
            openai_key=openai_key,
            use_openai=bool(openai_key),
            notion_token=config_dict.get("notion_token", ""),
            database_id=config_dict.get("database_id", ""),
            html_template=config_dict.get("html_template", "index_template.html"),
            html_final=config_dict.get("html_final", "index_interactif.html"),
            signature=config_dict.get("signature", "Default Signature")
        )

    def to_dict(self) -> dict:
        """Convert configuration to dictionary.

        Returns:
            Dictionary representation of configuration
        """
        return {
            "base_path": str(self.base_path),
            "openai_key": self.openai_key,
            "use_openai": self.use_openai,
            "notion_token": self.notion_token,
            "database_id": self.database_id,
            "html_template": self.html_template,
            "html_final": self.html_final,
            "signature": self.signature
        }
