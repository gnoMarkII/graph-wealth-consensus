import json
from pathlib import Path
from typing import Iterable


class HistoryManager:
    """Simple history manager for tracking processed video URLs."""

    def __init__(self, history_path: Path):
        self.history_path = history_path
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        self._history = self._load_history()

    def _load_history(self) -> set[str]:
        """Load history from the JSON file and return a set of processed URLs."""
        if not self.history_path.exists():
            return set()

        try:
            raw_text = self.history_path.read_text(encoding="utf-8")
            data = json.loads(raw_text)
            if isinstance(data, list):
                return set(str(item) for item in data)
            return set()
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"History file is corrupted: {self.history_path}. Remove or fix it before continuing."
            ) from exc

    def contains(self, url: str) -> bool:
        return url in self._history

    def add(self, url: str) -> None:
        if url not in self._history:
            self._history.add(url)
            self._save_history()

    def extend(self, urls: Iterable[str]) -> None:
        for url in urls:
            self._history.add(url)
        self._save_history()

    def _save_history(self) -> None:
        self.history_path.write_text(
            json.dumps(sorted(self._history), indent=4, ensure_ascii=False),
            encoding="utf-8",
        )
