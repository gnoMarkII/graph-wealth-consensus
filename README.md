# Graph-Wealth-Consensus 📈🤖

An AI-driven Investment Analysis Pipeline that automatically fetches YouTube transcripts, summarizes financial insights using Google Gemini, and organizes them into a searchable **Knowledge Graph** within **Obsidian**.

This tool is designed for value investors and financial content creators who want to find a "Consensus" among various market analysts without spending hours watching every single video.

---

## ✨ Features

- **Automated Transcription**: Fetches subtitles from YouTube videos to bypass manual note-taking.
- **AI-Powered Summarization**: Uses **Google Gemini 3.1 Flash-Lite** to extract key insights (Market View, Key Numbers, Recommended Assets, and Risks).
- **Auto-Linking Knowledge Graph**: Automatically wraps Stock tickers, Assets, and Macro terms in `[[ ]]` for seamless integration with Obsidian's Graph View.
- **Smart Rate-Limit Handling**: Built-in "Smart Retry" mechanism to handle API quotas (Error 429) automatically.
- **Timezone-Aware Organization**: Automatically sorts summaries into folders by `Year > Week > Analyst` based on Thailand's timezone (ICT).

---

## 🛠️ Tech Stack

- **Language**: Python 3.11+
- **AI Engine**: Google Generative AI (Gemini)
- **Database/Notes**: Obsidian (Markdown-based Second Brain)
- **Data Fetching**: YouTube Transcript API

---

## 🚀 Getting Started

### 1. Prerequisites
- Python installed on your machine.
- An **Obsidian** Vault set up.
- A **Google AI Studio API Key** (Get it for free [here](https://aistudio.google.com/)).

### 2. Installation
Clone this repository to your local machine:
```bash
git clone [https://github.com/YOUR_USERNAME/graph-wealth-consensus.git](https://github.com/YOUR_USERNAME/graph-wealth-consensus.git)
cd graph-wealth-consensus
```

Install dependencies:
```bash
pip install google-genai llama-index-llms-google python-dotenv youtube-transcript-api
```

### 3. Configuration
Create a .env file in the root directory and add your API key:
```bash
GOOGLE_API_KEY=your_api_key_here
```

### 4. Usage
Run the main script to start processing videos:
```bash
python main.py
```
---

🌌 Obsidian Integration
Knowledge Graph
The AI is instructed to identify and link key entities. When you view your Graph View in Obsidian, you will see how different analysts' views intersect on specific assets like [[NVIDIA]], [[Gold]], or [[Interest Rates]].

Weekly Dashboard (Dataview)
To see the "Top Mentioned Assets" of the week, install the Dataview plugin in Obsidian and use the following query in your notes:
```bash
TABLE length(rows) AS "Mentions"
FLATTEN file.outlinks AS Keywords
WHERE week = "Week_15" AND year = 2026
GROUP BY Keywords
SORT length(rows) DESC
```
---

📺 Credits
Developed by Money ReRoute. This project aims to bridge the gap between AI technology and Value Investing strategies.

---
⚠️ Disclaimer
This tool is for educational and informational purposes only. It does not constitute financial advice. Always perform your own due diligence before making any investment decisions.
