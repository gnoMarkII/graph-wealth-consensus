"""Main CLI entrypoint for the investment summarizer pipeline."""

import argparse
import logging
import sys
import time
from pathlib import Path

from config import (
    DEFAULT_CONFIG_PATH,
    DEFAULT_HISTORY_PATH,
    load_env,
    load_video_config,
    validate_video_group,
)
from history_manager import HistoryManager
from obsidian_manager import ObsidianManager
from rag_agent_gemini import GeminiRAGAgent
from youtube_fetcher import YouTubeFetcher

LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"


def configure_logging(verbose: bool = False) -> None:
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO, format=LOG_FORMAT)

    # ปิด log ของไลบรารีภายนอกที่ป้อน HTTP/DEBUG เยอะ
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("google").setLevel(logging.WARNING)
    logging.getLogger("llama_index").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    logging.getLogger("youtube_transcript_api").setLevel(logging.WARNING)
    logging.getLogger("huggingface_hub").setLevel(logging.WARNING)
    logging.getLogger("huggingface_hub.utils").setLevel(logging.WARNING)
    logging.getLogger("huggingface_hub.file_download").setLevel(logging.WARNING)
    logging.getLogger("hf_hub").setLevel(logging.WARNING)
    logging.getLogger("transformers").setLevel(logging.WARNING)
    logging.getLogger("transformers.utils").setLevel(logging.WARNING)
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Investment video summarizer and Obsidian exporter"
    )
    parser.add_argument(
        "--config",
        "-c",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="Path to videos.json",
    )
    parser.add_argument(
        "--vault",
        "-v",
        type=Path,
        default=Path("vault"),
        help="Obsidian vault folder",
    )
    parser.add_argument(
        "--data-dir",
        "-d",
        type=Path,
        default=Path("data"),
        help="Directory for transcript files",
    )
    parser.add_argument(
        "--history",
        "-H",
        type=Path,
        default=DEFAULT_HISTORY_PATH,
        help="Processed history file",
    )
    parser.add_argument(
        "--sleep",
        "-s",
        type=int,
        default=10,
        help="Cooldown seconds between video summarizations",
    )
    parser.add_argument(
        "--verbose",
        "-V",
        action="store_true",
        help="Enable debug logging",
    )
    return parser.parse_args()


def build_prompt(speaker: str, transcript: str) -> str:
    """Build the summarization prompt for the Gemini model.

    The prompt includes a fixed structure, speaker context, and the transcript text.
    It also instructs the model to mark named investment entities with wiki-style links.
    """
    return f"""
จงทำหน้าที่เป็นผู้ช่วยสรุปข้อมูลการลงทุน สรุปเนื้อหาของ {speaker} อย่างซื่อสัตย์ที่สุด

โครงสร้างการสรุป:
- 📌 ภาพรวมและมุมมอง: (สรุปทิศทางตลาดที่เขามอง)
- 📊 ตัวเลขสำคัญ: (ตัวเลขเศรษฐกิจ หรือสถิติที่อ้างถึง)
- 🎯 สินทรัพย์ที่แนะนำ: (หุ้น/กองทุน/สินทรัพย์ และเหตุผล)
- ⚠️ ความเสี่ยง: (คำเตือนที่ระบุ)

เนื้อหาที่ต้องสรุป: {transcript}

⚠️ **กฎเหล็กการทำ Knowledge Graph (ต้องทำตามอย่างเคร่งครัด):**
ในเนื้อหาที่คุณสรุปออกมา หากมีคำศัพท์ที่ตรงกับ 4 หมวดหมู่ด้านล่างนี้ คุณ **ต้อง** ใส่เครื่องหมาย [[ ]] คร่อมคำศัพท์นั้นเสมอ เพื่อสร้างจุดเชื่อมโยงในระบบ:
1. ชื่อหุ้น / ชื่อบริษัท (เช่น [[NVIDIA]], [[CPALL]])
2. ประเภทสินทรัพย์ (เช่น [[ทองคำ]], [[Bitcoin]], [[กองทุนตราสารหนี้]])
3. ชื่อประเทศ หรือ ภูมิภาค (เช่น [[จีน]], [[สหรัฐอเมริกา]], [[ยุโรป]])
"""


def main() -> int:
    args = parse_args()
    configure_logging(args.verbose)
    logger = logging.getLogger(__name__)

    logger.info("=== 🚀 Money ReRoute: Investment Agent ===")

    try:
        env = load_env()
    except Exception as exc:
        logger.error("Cannot load environment variables: %s", exc)
        return 1

    if not env.get("google_api_key"):
        logger.error("Missing GOOGLE_API_KEY in environment. Please update .env.")
        return 1

    fetcher = YouTubeFetcher(output_dir=args.data_dir)
    agent = GeminiRAGAgent()
    obsidian = ObsidianManager(vault_path=args.vault)
    history = HistoryManager(args.history)

    try:
        video_groups = load_video_config(args.config)
    except Exception as exc:
        logger.error("Cannot load video config: %s", exc)
        return 1

    if not video_groups:
        logger.warning("No video groups found in config. Exiting.")
        return 0

    for group in video_groups:
        group_data = validate_video_group(group)
        speaker = group_data["speaker"]

        for url in group_data["urls"]:
            if history.contains(url):
                logger.info("⏩ Skip already processed: %s", url)
                continue

            logger.info("🎬 Processing video: %s", url)

            try:
                raw_date, video_title = fetcher.get_video_info(url)
                transcript_path = fetcher.fetch_and_save(url)
                if transcript_path is None:
                    logger.warning("Transcript not available for %s", url)
                    continue

                transcript = transcript_path.read_text(encoding="utf-8")
                prompt = build_prompt(speaker, transcript)
                logger.info("🤖 Sending transcript to Gemini for summarization")

                summary = agent.summarize_transcript(prompt)

                final_path = obsidian.save_summary(
                    speaker=speaker,
                    raw_date=raw_date,
                    video_title=video_title,
                    url=url,
                    summary_text=summary,
                )

                logger.info("✅ Saved note: %s", final_path)
                history.add(url)
                time.sleep(args.sleep)

            except Exception:
                logger.exception("❌ Failed to process video %s", url)

    logger.info("✨ Completed processing all new videos.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
