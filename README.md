# Graph-Wealth-Consensus

ระบบ pipeline อัตโนมัติที่ดึง transcript จากคลิป YouTube ของนักวิเคราะห์การลงทุน สรุปเนื้อหาด้วย Google Gemini AI และจัดเก็บเป็น **Knowledge Graph** ใน Obsidian

เครื่องมือนี้ออกแบบมาสำหรับนักลงทุนที่ต้องการหา "Consensus" จากนักวิเคราะห์หลายคน โดยไม่ต้องเสียเวลานั่งดูทุกคลิปด้วยตนเอง

---

## คุณสมบัติหลัก

- **ดึง Transcript อัตโนมัติ** — ดึงซับไตเติ้ลจากคลิป YouTube แทนการจดด้วยมือ
- **สรุปด้วย AI** — ใช้ Google Gemini แยกแยะข้อมูลสำคัญ (มุมมองตลาด, ตัวเลขสำคัญ, สินทรัพย์แนะนำ, และความเสี่ยง)
- **Knowledge Graph อัตโนมัติ** — ห่อชื่อหุ้น สินทรัพย์ และ Macro terms ด้วย `[[ ]]` เพื่อสร้าง backlinks ใน Obsidian Graph View
- **Retry อัจฉริยะ** — จัดการ Rate Limit ของ API (Error 429/503) ด้วย exponential backoff โดยอัตโนมัติ
- **จัดโฟลเดอร์ตาม Timezone ไทย** — เรียงบันทึกตาม `ปี > สัปดาห์ > นักวิเคราะห์` โดยอิง ICT (UTC+7)
- **ป้องกันซ้ำซ้อน** — บันทึกประวัติ URL ที่ผ่านมาแล้ว ข้ามการประมวลผลซ้ำในรันถัดไป

---

## ภาพรวม Pipeline

```
inputs/videos.json
       │
       ▼
YouTubeFetcher        — ดึง transcript + ชื่อ/วันที่วิดีโอ
       │
       ▼
Gemini LLM            — สรุปเนื้อหา พร้อมใส่ [[Knowledge Graph]] links
       │
       ▼
ObsidianManager       — บันทึก .md ลง vault/ จัดโฟลเดอร์ตามปี/สัปดาห์
       │
       ▼
HistoryManager        — บันทึก URL ที่ทำแล้วใน processed_history.json
```

แต่ละ note ที่สร้างจะมีโครงสร้างเสมอ:

- 📌 ภาพรวมและมุมมองตลาด
- 📊 ตัวเลขสำคัญและสถิติ
- 🎯 สินทรัพย์ที่แนะนำ (พร้อมเหตุผล)
- ⚠️ ความเสี่ยงและคำเตือน

---

## Tech Stack

| Layer | เครื่องมือ |
|---|---|
| LLM | Google Gemini (`gemini-2.5-flash` หรือ `gemini-3-flash-preview`) |
| Embeddings | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (HuggingFace) |
| Vector Store | ChromaDB (persistent local) |
| Framework | LlamaIndex |
| Transcript | `youtube-transcript-api` |
| Note output | Obsidian Markdown |
| ภาษา | Python 3.11+ |

---

## โครงสร้างโปรเจกต์

```
graph-wealth-consensus/
├── main.py                  # จุดเริ่มต้น CLI — ควบคุม pipeline ทั้งหมด
├── config.py                # โหลด .env และ videos.json
├── youtube_fetcher.py       # ดึง transcript + metadata จาก YouTube
├── rag_agent_gemini.py      # Gemini LLM wrapper + ChromaDB RAG index
├── history_manager.py       # ติดตาม URL ที่ process แล้ว (JSON-based)
├── obsidian_manager.py      # สร้างไฟล์ Markdown สำหรับ Obsidian
├── check_models.py          # Utility: ดูรายชื่อ Gemini model ที่ใช้ได้
├── inputs/
│   ├── videos.json          # กำหนด speaker และ YouTube URL ที่ต้องการสรุป
│   └── processed_history.json  # ประวัติ URL ที่ทำแล้ว (auto-generated)
├── data/                    # transcript .txt files (auto-generated, ไม่ commit)
├── chroma_db_gemini/        # ChromaDB vector store (auto-generated, ไม่ commit)
├── vault/                   # Obsidian vault output (ไม่ commit)
│   └── Invest_analyst/
│       └── {year}/
│           └── Week_{nn}/
│               └── {speaker}/
│                   └── Summary_{speaker}_{timestamp}.md
├── archive/
│   └── rag_agent.py         # เวอร์ชันเก่าที่ใช้ Ollama (local AI) แทน Gemini
├── .env                     # API keys — ห้าม commit
├── .env.example             # ตัวอย่าง .env สำหรับผู้ใช้ใหม่
└── .gitignore
```

---

## การติดตั้ง

### 1. Clone repository

```bash
git clone https://github.com/gnoMarkII/graph-wealth-consensus.git
cd graph-wealth-consensus
```

### 2. สร้าง virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. ติดตั้ง dependencies

```bash
pip install \
  google-genai \
  llama-index-core \
  llama-index-llms-google-genai \
  llama-index-embeddings-huggingface \
  llama-index-vector-stores-chroma \
  chromadb \
  sentence-transformers \
  youtube-transcript-api \
  python-dotenv \
  requests
```

### 4. ตั้งค่า API Key

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

เปิดไฟล์ `.env` และใส่ Google AI API key:

```env
GOOGLE_API_KEY=your_api_key_here
```

รับ API key ได้ฟรีที่ [Google AI Studio](https://aistudio.google.com/app/apikey)

---

## วิธีใช้งาน

### รันพื้นฐาน

```bash
python main.py
```

โปรแกรมจะอ่าน `inputs/videos.json` และประมวลผล URL ทุกอันที่ยังไม่เคยทำ

### ตัวเลือก CLI ทั้งหมด

```
python main.py [OPTIONS]

Options:
  -c, --config PATH     path ของ videos.json              (default: inputs/videos.json)
  -v, --vault PATH      Obsidian vault folder              (default: vault)
  -d, --data-dir PATH   โฟลเดอร์สำหรับเก็บ transcript files (default: data)
  -H, --history PATH    ไฟล์ประวัติ processed URLs          (default: inputs/processed_history.json)
  -s, --sleep INT       หน่วงเวลา (วินาที) ระหว่างแต่ละวิดีโอ (default: 10)
  -V, --verbose         เปิด debug logging
```

**ตัวอย่าง:**

```bash
# ชี้ vault ไปที่โฟลเดอร์ Obsidian จริง
python main.py --vault "C:/Users/me/Documents/MyVault"

# ใช้ไฟล์ config คนละชุด และเปิด debug log
python main.py --config my_channels.json --verbose --sleep 5
```

### ดูรายชื่อ Gemini model ที่ใช้ได้

```bash
python check_models.py
```

แสดงรายการ model ทั้งหมดที่ API key ของคุณมีสิทธิ์ใช้งาน จากนั้นเลือก model ใน `rag_agent_gemini.py`:

```python
agent = GeminiRAGAgent(model_name="gemini-2.5-flash")
```

---

## กำหนดช่องที่ต้องการติดตาม (`inputs/videos.json`)

แก้ไขไฟล์นี้เพื่อเพิ่ม/เปลี่ยนช่อง YouTube ที่ต้องการสรุป:

```json
[
    {
        "speaker": "ชื่อนักวิเคราะห์หรือช่อง",
        "urls": [
            "https://www.youtube.com/watch?v=VIDEO_ID_1",
            "https://www.youtube.com/watch?v=VIDEO_ID_2"
        ]
    },
    {
        "speaker": "อีกช่องหนึ่ง",
        "urls": [
            "https://youtu.be/VIDEO_ID_3"
        ]
    }
]
```

> รองรับทั้ง `youtube.com/watch?v=` และ `youtu.be/` และต้องเป็นคลิปที่เปิด transcript (ซับไตเติ้ล) ภาษาไทยหรืออังกฤษไว้

---

## การเชื่อมกับ Obsidian

### Knowledge Graph

AI ถูกสั่งให้ระบุและเชื่อมโยงชื่อสำคัญทุกชนิด เมื่อเปิด **Graph View** ใน Obsidian จะเห็นว่านักวิเคราะห์หลายคนมองตรงกันที่สินทรัพย์ไหนบ้าง เช่น `[[NVIDIA]]`, `[[ทองคำ]]`, `[[อัตราดอกเบี้ย]]`

### Weekly Dashboard (Dataview Plugin)

ติดตั้ง plugin [Dataview](https://github.com/blacksmithgu/obsidian-dataview) ใน Obsidian แล้วใช้ query นี้เพื่อดูสินทรัพย์ที่ถูกพูดถึงมากที่สุดในแต่ละสัปดาห์:

```dataview
TABLE length(rows) AS "จำนวนครั้งที่กล่าวถึง"
FLATTEN file.outlinks AS Keywords
WHERE week = "Week_15" AND year = 2026
GROUP BY Keywords
SORT length(rows) DESC
```

### โครงสร้าง Note ที่ได้

แต่ละไฟล์มี YAML frontmatter สำหรับใช้ query กับ Dataview:

```markdown
---
name: "ชื่อคลิป"
speaker: "ชื่อช่อง"
week: "Week_15"
year: "2026"
upload_date: "2026-04-07"
source_url: "https://www.youtube.com/watch?v=..."
created: "2026-04-07 10:04"
tags: [investment, summary]
---

# ชื่อคลิป
> **วิเคราะห์โดย:** [[ชื่อช่อง]]
> **ช่วงเวลา:** [[ภาพรวมการลงทุนปี 2026]] > [[Week_15_2026]]
> **ลิงก์:** [ดูคลิปต้นฉบับ](URL)

📌 **ภาพรวมและมุมมอง:** ...
📊 **ตัวเลขสำคัญ:** ...
🎯 **สินทรัพย์ที่แนะนำ:** [[NVDA]], [[ทองคำ]], [[กองทุนตราสารหนี้]] ...
⚠️ **ความเสี่ยง:** ...

---
**🔗 จุดเชื่อมโยง (Knowledge Hub):**
- นักวิเคราะห์: [[ชื่อช่อง]]
- บทวิเคราะห์ประจำปี: [[ภาพรวมการลงทุนปี 2026]]
```

---

## ข้อกำหนดเบื้องต้น

- Python 3.11 ขึ้นไป
- Google AI API key (สร้างได้ฟรีที่ Google AI Studio)
- คลิป YouTube ต้องเปิด transcript/subtitle ภาษาไทยหรืออังกฤษไว้
- Obsidian (ไม่บังคับ — output เป็น Markdown ธรรมดา ใช้กับโปรแกรมอื่นได้)

---

## Contributing

ยินดีต้อนรับ Pull requests และ Issues ทุกรูปแบบ สามารถ fork และปรับแต่งช่อง YouTube หรือโครงสร้าง prompt ให้เหมาะกับ workflow การวิจัยการลงทุนของตัวเองได้เลย

---

## ข้อจำกัดความรับผิดชอบ

เครื่องมือนี้มีไว้เพื่อการศึกษาและให้ข้อมูลเท่านั้น ไม่ถือเป็นคำแนะนำทางการเงิน โปรดศึกษาข้อมูลด้วยตนเองก่อนตัดสินใจลงทุนทุกครั้ง

---

## เครดิต

พัฒนาโดย [Money ReRoute](https://github.com/gnoMarkII) — โปรเจกต์นี้มุ่งเชื่อม AI technology เข้ากับกลยุทธ์การลงทุนแบบ Value Investing
