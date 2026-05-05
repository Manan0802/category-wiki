# 📚 Category Wiki Agent

An **LLM-powered knowledge compiler** built with **LangGraph** that transforms raw, multi-format product data into comprehensive **Wikipedia-style markdown articles** for an Indian B2B marketplace.

Inspired by the [LLM Wiki pattern](https://github.com/klntsky/llm-wiki) — knowledge is **compiled once and kept current**, not re-derived on every query.

---

## Architecture

```
START → INPUT → CATEGORY → CHECK_WIKI
                              │
                    ┌─────────┴─────────┐
                    │                   │
                 CREATE              UPDATE
                    │                   │
                    └────┬──────────────┘
                         │
            ┌────────────┤ (more sources?)
            │            │
     LOAD_NEXT_SOURCE    │
            │            │
         UPDATE ─────────┘
                         │
                      ENRICH → SAVE → INDEX → END
```

### How It Works
1. **INPUT**: Scans `data/inputs/input_<mcat_id>/` for all source files (JSON, TXT, CSV, etc.)
2. **Source Tracking**: Compares against `.manifest.json` to find NEW, CHANGED, and REMOVED sources
3. **CATEGORY**: LLM classifies the item category
4. **CHECK**: Looks for existing wiki — decides CREATE vs UPDATE path
5. **Iterative Build**: Processes sources one-by-one, progressively building the wiki
6. **ENRICH**: Final polish — cross-links, market intelligence, metadata
7. **SAVE**: Writes wiki + logs + references + updates manifest
8. **INDEX**: Rebuilds the master index with detailed entries

---

## Input Data Structure

```
data/inputs/
└── input_68865/              ← One folder per category (MCAT ID)
    ├── acc-block pdf 1.json  ← PDF extraction data
    ├── acc-block pdf 2.json
    ├── buyer_call 1.json     ← Buyer call data
    ├── buyer_call 2.json
    ├── notes.txt             ← Free-text notes
    ├── links.txt             ← URL references
    └── .manifest.json        ← Auto-generated tracking file
```

- **Any number of files** per category (1, 5, 25 — doesn't matter)
- **Any format**: JSON, TXT, MD, CSV, HTML, or unknown
- **Source tracking**: `.manifest.json` tracks what's processed

---

## Output Files

```
wiki/
├── index.md                  ← Detailed master index (catalog with summaries)
├── items/
│   └── aac_block.md          ← The wiki article
├── logs_aac_block.md         ← Agent execution logs (mini-Langfuse)
└── references_aac_block.md   ← All source references used
```

### index.md
Wikipedia-style catalog — each page listed with link, summary, size, associated logs/references.

### logs_<cat>.md
Detailed step-by-step execution log — what the agent did, which sources it read, what inferences it made, timing, decisions. Like a mini-Langfuse.

### references_<cat>.md
All source files referenced, grouped by type, with what was extracted from each.

---

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```env
LLM_GATEWAY_URL=https://imllm.intermesh.net/v1/chat/completions
LLM_GATEWAY_API_KEY=your_api_key_here
LLM_MODEL=google/gemini-2.5-pro
LLM_MAX_TOKENS=16000
DEBUG=True
```

### 3. Place Input Data

Create a folder per category in `data/inputs/`:
```
data/inputs/input_68865/
├── source1.json
├── source2.json
└── source3.txt
```

---

## Running

```bash
# With arguments
python main.py --mcat-id 68865 --mcat-name "AAC Block"

# Interactive mode
python main.py
```

### Re-runs with Source Tracking

- **Add 3 new files** to `data/inputs/input_68865/` → re-run → only new files processed
- **Remove 2 files** → re-run → removed info flagged in wiki
- **Change a file** → re-run → changed file re-processed

---

## Skills (Prompts)

All LLM prompts live in `skills/*.md` — never hardcoded in Python:

| File | Used By | Purpose |
|------|---------|---------|
| `agent_prompt.md` | Reference | Master agent identity & philosophy |
| `category_detector.md` | `category_node` | Category classification prompt |
| `wiki_builder.md` | `create_node`, `update_node` | Wiki generation & merge prompt |
| `enricher.md` | `enrich_node` | Final enrichment & polish prompt |

### Customizing Prompts
1. Open the `.md` file in `skills/`
2. Edit the prompt text
3. Run the agent — your prompt loads automatically
4. If a skill file is empty → built-in fallback is used

---

## Tech Stack
- **LangGraph** — agent orchestration with conditional routing
- **Python** — core logic
- **Raw HTTP** (`requests.post`) — LLM calls (no LangChain wrappers)
- **python-dotenv** — environment management
