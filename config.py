import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

DEFAULT_CONFIG_PATH = Path("inputs/videos.json")
DEFAULT_HISTORY_PATH = Path("inputs/processed_history.json")
DEFAULT_ENV_PATH = Path(".env")


def load_env(env_path: Path = DEFAULT_ENV_PATH) -> dict[str, Any]:
    """Load environment variables from .env and return important keys."""
    load_dotenv(env_path)
    return {
        "google_api_key": os.getenv("GOOGLE_API_KEY"),
    }


def load_video_config(config_path: Path = DEFAULT_CONFIG_PATH) -> list[dict[str, Any]]:
    """Load and validate the playlist config file."""
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    try:
        text = config_path.read_text(encoding="utf-8")
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in config file: {config_path}") from exc

    if not isinstance(data, list):
        raise ValueError(f"Expected a list of video groups in {config_path}")

    return data


def validate_video_group(group: dict[str, Any]) -> dict[str, Any]:
    speaker = group.get("speaker", "Unknown")
    urls = group.get("urls", [])
    if not isinstance(urls, list):
        raise ValueError("Each video group must include a list of urls")

    return {
        "speaker": speaker,
        "urls": [str(url).strip() for url in urls if str(url).strip()],
    }
