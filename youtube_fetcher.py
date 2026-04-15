import re
from pathlib import Path

import requests
from datetime import datetime, timezone, timedelta
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter


class YouTubeFetcher:
    """Manage YouTube transcript extraction and metadata retrieval."""

    def __init__(self, output_dir: str | Path = "data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.ytt_api = YouTubeTranscriptApi()
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36"
                )
            }
        )

    def extract_video_id(self, url: str) -> str | None:
        patterns = [
            r"(?:v=|\/)([0-9A-Za-z_-]{11})(?:[&?#]|$)",
            r"youtu\.be/([0-9A-Za-z_-]{11})(?:[&?#]|$)",
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def clean_transcript(self, raw_text: str) -> str:
        lines = [line.strip() for line in raw_text.split("\n") if len(line.strip()) > 2]
        paragraphs = []
        chunk_size = 6
        for index in range(0, len(lines), chunk_size):
            paragraph = " ".join(lines[index : index + chunk_size])
            paragraphs.append(paragraph)
        return "\n\n".join(paragraphs)

    def _get_webpage(self, url: str) -> str:
        response = self.session.get(url, timeout=12)
        response.raise_for_status()
        return response.text

    def fetch_and_save(self, url: str) -> Path | None:
        video_id = self.extract_video_id(url)
        if not video_id:
            raise ValueError(f"Invalid YouTube URL: {url}")

        transcript_data = self.ytt_api.fetch(video_id, languages=["th", "en"])
        raw_text = TextFormatter().format_transcript(transcript_data)
        cleaned_text = self.clean_transcript(raw_text)

        file_path = self.output_dir / f"{video_id}.txt"
        file_path.write_text(f"URL อ้างอิง: {url}\n\n{cleaned_text}", encoding="utf-8")
        return file_path

    def get_video_info(self, url: str) -> tuple[str, str]:
        try:
            html = self._get_webpage(url)
            date_match = re.search(r'<meta itemprop="uploadDate" content="([^"]+)">', html)
            title_match = re.search(r'<meta name="title" content="([^"]+)">', html)

            raw_date_str = date_match.group(1) if date_match else ""
            if raw_date_str:
                try:
                    dt_original = datetime.fromisoformat(raw_date_str)
                    thai_tz = timezone(timedelta(hours=7))
                    dt_thai = dt_original.astimezone(thai_tz)
                    date = dt_thai.strftime("%Y-%m-%d %H:%M:%S")
                except ValueError:
                    date = raw_date_str
            else:
                date = "Unknown Date"

            title = title_match.group(1) if title_match else "Unknown Title"
            title = title.replace("&amp;", "&").replace("&#39;", "'").replace("&quot;", '"')
            return date, title
        except Exception:
            return "Unknown Date", "Unknown Title"
