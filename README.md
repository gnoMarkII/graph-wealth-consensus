# Graph-Wealth-Consensus

An AI-driven Investment Analysis Pipeline that automatically fetches YouTube transcripts, summarizes financial insights using Google Gemini, and organizes them into a searchable **Knowledge Graph** within **Obsidian**.

This tool is designed for value investors and financial content creators who want to find a "Consensus" among various market analysts without spending hours watching every single video.

---

## Features

- **Automated Transcription** — Fetches subtitles from YouTube videos to bypass manual note-taking
- **AI-Powered Summarization** — Uses Google Gemini to extract key insights (Market View, Key Numbers, Recommended Assets, and Risks)
- **Auto-Linking Knowledge Graph** — Automatically wraps stock tickers, assets, and macro terms in `[[ ]]` for seamless integration with Obsidian's Graph View
- **Smart Rate-Limit Handling** — Built-in retry mechanism to handle API quotas (Error 429) automatically
- **Timezone-Aware Organization** — Automatically sorts summaries into folders by `Year > Week > Analyst` based on Thailand's timezone (ICT)
- **Duplicate Prevention** — History tracking skips already-processed videos across runs

---

## Pipeline Overview

```
inputs/videos.json
       │
       ▼
YouTubeFetcher        — fetch transcript + video title/date
       │
       ▼
Gemini LLM            — summarize with [[Knowledge Graph]] links
       │
       ▼
ObsidianManager       — save .md to vault/ organized by year/week
       │
       ▼
HistoryManager        — record processed URLs to prevent reprocessing
```

Each generated note follows this structure:

- 📌 Market View & Outlook
- 📊 Key Numbers & Statistics
- 🎯 Recommended Assets (with reasons)
- ⚠️ Risks & Warnings

---

## Tech Stack

| Layer | Tool |
|---|---|
| LLM | Google Gemini (`gemini-2.5-flash` or `gemini-3-flash-preview`) |
| Embeddings | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (HuggingFace) |
| Vector Store | ChromaDB (persistent local) |
| Framework | LlamaIndex |
| Transcript | `youtube-transcript-api` |
| Note output | Obsidian Markdown |
| Language | Python 3.11+ |

---

## Project Structure

```
graph-wealth-consensus/
├── main.py                  # CLI entrypoint — orchestrates the full pipeline
├── config.py                # Load .env and videos.json
├── youtube_fetcher.py       # YouTube transcript extraction and metadata
├── rag_agent_gemini.py      # Gemini LLM wrapper + ChromaDB RAG index
├── history_manager.py       # Track processed URLs (JSON-based)
├── obsidian_manager.py      # Build Obsidian Markdown notes
├── check_models.py          # Utility: list available Gemini models
├── inputs/
│   ├── videos.json          # Define speakers and YouTube URLs to process
│   └── processed_history.json  # Auto-generated processed URL log
├── data/                    # Transcript .txt files (auto-generated)
├── chroma_db_gemini/        # ChromaDB vector store (auto-generated)
├── vault/                   # Obsidian vault output
│   └── Invest_analyst/
│       └── {year}/
│           └── Week_{nn}/
│               └── {speaker}/
│                   └── Summary_{speaker}_{timestamp}.md
├── .env                     # API keys — never commit this
└── .env.example             # Example .env template
```

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/gnoMarkII/graph-wealth-consensus.git
cd graph-wealth-consensus
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure your API key

```bash
cp .env.example .env
```

Open `.env` and add your Google AI API key:

```env
GOOGLE_API_KEY=your_api_key_here
```

Get a free API key at [Google AI Studio](https://aistudio.google.com/app/apikey).

---

## Usage

### Basic run

```bash
python main.py
```

Reads `inputs/videos.json` and processes every URL that has not been processed before.

### CLI options

```
python main.py [OPTIONS]

Options:
  -c, --config PATH     Path to videos.json            (default: inputs/videos.json)
  -v, --vault PATH      Obsidian vault folder           (default: vault)
  -d, --data-dir PATH   Directory for transcript files  (default: data)
  -H, --history PATH    Processed URL history file      (default: inputs/processed_history.json)
  -s, --sleep INT       Cooldown seconds between videos (default: 10)
  -V, --verbose         Enable debug logging
```

**Examples:**

```bash
# Use a different config and write to your real Obsidian vault
python main.py --config my_channels.json --vault /path/to/obsidian/vault

# Enable debug logging with a shorter sleep
python main.py --verbose --sleep 5
```

### Check available Gemini models

```bash
python check_models.py
```

Lists all Gemini models available to your API key. Set the model in `rag_agent_gemini.py`:

```python
agent = GeminiRAGAgent(model_name="gemini-2.5-flash")
```

---

## Configuration (`inputs/videos.json`)

Define the analysts and YouTube URLs you want to track:

```json
[
    {
        "speaker": "Analyst Name or Channel",
        "urls": [
            "https://www.youtube.com/watch?v=VIDEO_ID_1",
            "https://www.youtube.com/watch?v=VIDEO_ID_2"
        ]
    },
    {
        "speaker": "Another Channel",
        "urls": [
            "https://youtu.be/VIDEO_ID_3"
        ]
    }
]
```

Both `youtube.com/watch?v=` and `youtu.be/` URL formats are supported. Videos must have Thai or English transcripts/subtitles enabled.

---

## Obsidian Integration

### Knowledge Graph

The AI is instructed to identify and link key entities. When you open **Graph View** in Obsidian, you will see how different analysts' views intersect on the same assets — `[[NVIDIA]]`, `[[Gold]]`, `[[Interest Rates]]`, etc.

### Weekly Dashboard (Dataview Plugin)

Install the [Dataview](https://github.com/blacksmithgu/obsidian-dataview) plugin in Obsidian and use this query to see the most-mentioned assets for any given week:

```dataview
TABLE length(rows) AS "Mentions"
FLATTEN file.outlinks AS Keywords
WHERE week = "Week_15" AND year = 2026
GROUP BY Keywords
SORT length(rows) DESC
```

### Note structure

Each generated note includes YAML frontmatter for querying with Dataview:

```markdown
---
name: "Video Title"
speaker: "Channel Name"
week: "Week_15"
year: "2026"
upload_date: "2026-04-07"
source_url: "https://www.youtube.com/watch?v=..."
created: "2026-04-07 10:04"
tags: [investment, summary]
---

# Video Title
> **Analyst:** [[Channel Name]]
> **Period:** [[Investment Overview 2026]] > [[Week_15_2026]]
> **Source:** [Watch original](URL)

📌 **Market View:** ...
📊 **Key Numbers:** ...
🎯 **Recommended Assets:** [[NVDA]], [[Gold]], [[Bond Fund]] ...
⚠️ **Risks:** ...
```

---

## Requirements

- Python 3.11+
- Google AI API key
- YouTube videos must have transcripts (subtitles) enabled in Thai or English
- Obsidian (optional — the vault output is plain Markdown)

---

## Contributing

Pull requests and issues are welcome. Feel free to fork and customize the YouTube channels or prompt structure for your own investment research workflow.

---

## Disclaimer

This tool is for educational and informational purposes only. It does not constitute financial advice. Always perform your own due diligence before making any investment decisions.

---

## Credits

Developed by [Money ReRoute](https://github.com/gnoMarkII). This project aims to bridge the gap between AI technology and value investing strategies.
