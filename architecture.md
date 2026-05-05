# 🏛️ Category Wiki Agent — System Architecture & Workflow

## 1. Executive Summary
The Category Wiki Agent is an event-driven, graph-based knowledge compilation system designed for a B2B marketplace environment. Unlike traditional conversational RAG (Retrieval-Augmented Generation) systems that "fetch and forget" transient answers, this agent implements the **Compounding Knowledge Pattern**. It systematically ingests varied streams of raw, unstructured product data and synthesizes them into authoritative, dynamically updating, Wikipedia-grade Markdown articles. 

## 2. Technical Stack
- **Orchestration Framework:** LangGraph (StateGraph implementation)
- **Core Environment:** Python 3.12 (Standard libraries `pathlib`, `logging`, `re`)
- **LLM Integration:** Direct REST HTTP implementation bounding to custom Gateway, bypassing heavy LLM wrapper libraries. Includes strict timeout handlers and auto-restorations.
- **Persistence:** Local File System (JSON Manifests, Markdown outputs)

---

## 3. Architecture Topology & State Flow

The agent utilizes a StateGraph pipeline. A unified typed dictionary (`WikiState`) acts as the memory tape flowing through interconnected agent node boundaries.

```text
START
  │
  ▼
INPUT NODE          ← Scans data/inputs/ for files & compares against .manifest.json
  │                   (Net-New or Changed files pushed into queue)
  ▼
CATEGORY NODE       ← LLM classifies product category (e.g. Building Materials)
  │
  ▼
CHECK WIKI ─────────┐
  │                 │
  │ (No wiki)       │ (Wiki exists)
  ▼                 ▼
CREATE NODE      UPDATE NODE   ← LLM smartly merges source context without losing past facts
  │                 │
  └────────┬────────┘
           │
           ▼ (More sources pending?)
     ┌─────┴──────────┐
     │                │
   (Yes)             (No)
     │                │
     ▼                ▼
 LOAD NEXT ──────► ENRICH NODE ← LLM performs final formatting and inserts cross-references
                      │
                      ▼
                  SAVE NODE    ← File outputs physically committed to disk + tracker saved
                      │
                      ▼
                 INDEX NODE    ← Rebuilds the master Wikipedia catalog page
                      │
                      ▼
                     END
```

---

## 4. Input Pre-Processing & Synchronization

Rather than blasting unstructured bytes to the LLM immediately, the `preprocessor.py` intercepts all incoming formats and structures them uniformly:

```text
data/inputs/
└── input_68865/              
    ├── acc-block pdf 1.json  ← PDF extractions parsed line by line
    ├── buyer_call 1.json     ← Call transripts structurally mapped
    ├── notes.txt             ← Naked text wrapped with identifiers
    └── .manifest.json        ← Cryptographic tracking file
```

**Stateful Synchronization (Delta Updates):**
Generating tokens is computationally expensive. When the graph initiates, it reads local file hashes directly against `.manifest.json`. If 25 files were previously run and only 3 new files were added to the payload folder, only those **3 delta files** are processed. Deleted files are natively detected, and their outdated assertions are scrubbed from the active wiki.

---

## 5. Modular Prompting Engine (Skills)

Instead of monolithic instructions mapping the entire system behavior, operational logic is parsed dynamically into LLM nodes via isolated markdown wrappers:

| Skill Module | Agent Node target | Purpose |
|--------------|------------------|---------|
| `agent_prompt.md` | Background (Global) | Enforces the "Compounding Knowledge" mindset |
| `category_detector.md` | `category_node` | B2B catalog classification rules |
| `wiki_builder.md` | `create` / `update` | Enforces structural Wikipedia guidelines, INR pricing, IS Codes, and explicit rules on resolving metric conflicts. |
| `enricher.md` | `enrich_node` | Generates demand signals overview and seamlessly integrates structural `[[ ]]` internal Cross-Referencing. |

---

## 6. Observability & Telemetry Separation

For absolute executive trust and granular engineering audits, the system cleanly segregates the final outputs into 4 interconnected artifacts:

```text
wiki/
├── index.md                  ← Master Catalog providing a directory graph to all generation metrics
│
├── items/
│   └── aac_block.md          ← The compiled, public-facing Wikipedia entry
│
├── logs/
│   └── logs_aac_block.md     ← Granular diagnostic traces mapping execution loops & token costs
│
└── references/
    └── references_aac_block.md ← Extraction logic summaries validating where data was sourced
```

**Why specific referencing?**
When the `UPDATE NODE` digests a source file, it must emit a sub-summary bounding the exact data metrics pulled (`<extraction_summary>`). This eliminates the "black-box" attribute of AI generation. If the Wiki boasts a price parameter of *₹400*, the references module will mathematically trace that line back to `buyer_call_15.json` so data integrities can be actively audited by stakeholders without reruns.
