import re
from datetime import datetime
from pathlib import Path


"""Utilities to create and save Obsidian markdown notes from video summaries."""


class ObsidianManager:
    """Create structured Obsidian notes from video summaries."""

    def __init__(self, vault_path: str | Path):
        self.vault_path = Path(vault_path)
        self.base_folder = "Invest_analyst"

    def _get_time_hierarchy(self, date_input: str) -> tuple[str, str]:
        """Convert a raw upload date into year/week folder hierarchy."""
        try:
            clean_date = date_input[:10]
            date_obj = datetime.strptime(clean_date, "%Y-%m-%d")
            year, week, _ = date_obj.isocalendar()
            return str(year), f"Week_{str(week).zfill(2)}"
        except Exception:
            now = datetime.now()
            return now.strftime("%Y"), "Week_Unknown"

    def _slugify(self, value: str) -> str:
        """Create a safe filename slug from text content."""
        cleaned = re.sub(r"[^\w\s-]", "", value, flags=re.U).strip()
        cleaned = re.sub(r"\s+", "_", cleaned)
        return cleaned or "unknown"

    def _quote_yaml(self, value: str) -> str:
        """Escape string content for safe YAML frontmatter output."""
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'

    def _format_filename_timestamp(self, raw_date: str) -> str:
        """Format the file timestamp from the upload date if available."""
        try:
            parsed_date = datetime.strptime(raw_date[:19], "%Y-%m-%d %H:%M:%S")
        except Exception:
            try:
                parsed_date = datetime.fromisoformat(raw_date)
            except Exception:
                parsed_date = datetime.now()
        return parsed_date.strftime("%Y%m%d_%H%M%S")

    def save_summary(
        self,
        speaker: str,
        raw_date: str,
        video_title: str,
        url: str,
        summary_text: str,
    ) -> Path:
        """Save the generated summary as an Obsidian markdown note."""
        year, week = self._get_time_hierarchy(raw_date)
        safe_speaker = self._slugify(speaker)
        safe_title = self._slugify(video_title)

        target_dir = self.vault_path / self.base_folder / year / week / safe_speaker
        target_dir.mkdir(parents=True, exist_ok=True)

        timestamp = self._format_filename_timestamp(raw_date)
        file_name = f"Summary_{safe_speaker}_{timestamp}.md"
        full_path = target_dir / file_name

        counter = 1
        while full_path.exists():
            file_name = f"Summary_{safe_speaker}_{timestamp}_{counter}.md"
            full_path = target_dir / file_name
            counter += 1

        metadata = {
            "title": video_title,
            "speaker": speaker,
            "week": week,
            "year": year,
            "upload_date": raw_date[:10],
            "source_url": url,
            "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }

        markdown_content = f"""---
name: {self._quote_yaml(metadata['title'])}
speaker: {self._quote_yaml(metadata['speaker'])}
week: {self._quote_yaml(metadata['week'])}
year: {self._quote_yaml(metadata['year'])}
upload_date: {self._quote_yaml(metadata['upload_date'])}
source_url: {self._quote_yaml(metadata['source_url'])}
created: {self._quote_yaml(metadata['created'])}
tags: [investment, summary]
---

# 📺 {video_title}
> **วิเคราะห์โดย:** [[{speaker}]]
> **ช่วงเวลา:** [[ภาพรวมการลงทุนปี {year}]] > [[{week}_{year}]]
> **ลิงก์:** [ดูคลิปต้นฉบับ]({url})

---

{summary_text}

---
**🔗 จุดเชื่อมโยง (Knowledge Hub):**
- นักวิเคราะห์: [[{speaker}]]
- บทวิเคราะห์ประจำปี: [[ภาพรวมการลงทุนปี {year}]]
"""

        full_path.write_text(markdown_content, encoding="utf-8")
        return full_path
