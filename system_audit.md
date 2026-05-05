# 🔍 Category Wiki Agent — Full System Audit

> **Date:** 2026-04-17  
> **Scope:** Complete review of wiki_structure.md alignment, template.md adoption, doubts system, token tracking, prompt generality

---

## ✅ Current System Status — What's Working

| Component | Status | Notes |
|-----------|--------|-------|
| **Wiki Structure** | ✅ Aligned | `wiki_builder.md` now matches all 11 sections from `wiki_structure.md` |
| **Category-Agnostic Prompts** | ✅ Fixed | All AAC-specific examples removed from both `wiki_builder.md` and `enricher.md` |
| **Doubt Logging** | ✅ Live | XML parsing, per-step accumulation, resolution tracking, human-readable reports |
| **Token Tracking** | ✅ Live | Per-step + total usage, saved to `token_usage/` at project root |
| **Web Search** | ✅ Live | `[WEB_SEARCH]` tags parsed, searches executed, results re-injected |
| **Conflict Handling** | ✅ Live | `[CONFLICT: ...]` markers + `⚠️ Data Variance` in enricher |
| **Import Chain** | ✅ Clean | All files compile and import correctly |

---

## 📋 Template.md Analysis — What to Adopt vs Skip

After comparing your `template.md` (extraction-focused template) with our current `wiki_builder.md` (generation-focused prompt), here's my recommendation:

### ✅ ADOPT — These will genuinely improve quality

| Feature from Template | Why It Helps | Implementation Effort |
|----------------------|-------------|----------------------|
| **1. Extraction Summary** at end of each LLM pass | Lets us track what was found vs missing per source — feeds into doubts system | Medium — add `<extraction_summary>` to prompt instructions |
| **2. Confidence Level per Section** | Agent rates its own confidence (High/Med/Low) per section — directly powers doubt severity | Medium — extend doubt protocol |
| **3. "NOT FOUND IN SOURCE" markers** | Instead of leaving sections thin silently, agent explicitly marks gaps — way better for auditing | Low — add to prompt rules |
| **4. Specification Interdependency + Calculation Methods** | Your structure doc has this (§2.3) and template has detailed tables — our prompt mentions it but could be richer | Low — already in prompt, just needs emphasis |
| **5. Data Quality Notes** | Template's "Conflicting information found in", "Ambiguous information in" — maps perfectly to our doubts system | Already done via doubts ✅ |

### ❌ SKIP — Would hurt our approach

| Feature from Template | Why We Skip It |
|----------------------|---------------|
| **"DO NOT use general knowledge"** | We WANT the agent to use web search + reasoning. This rule kills that. |
| **`[SOURCE: doc, page]` after every line** | Would bloat wiki 3-4x, make it unreadable. Our refs system handles provenance separately. |
| **`[Extract]` placeholder style** | Template is fill-in-the-blank. Our agent writes prose. Fundamentally different paradigm. |
| **Rigid repeated structures** (Product Type 1, Product Type 2...) | Agent should dynamically create as many as needed, not follow a fixed count. |

### 🔄 MERGE — Adopt the concept, adapt the implementation

| Concept | Our Implementation |
|---------|-------------------|
| Template's "Recommended Follow-up Questions" | → Feed into doubt's `suggested_resolution` field (already there ✅) |
| Template's "Documents Processed" summary | → Already in our logs system with source tracking ✅ |
| Template's per-section confidence table | → **NEW: Add `<CONFIDENCE>` tag** — agent rates each section |

---

## 🎯 My Recommendations — 3 High-Impact Changes

### 1. Add Section Confidence Scoring (from template.md)

Have the agent emit a confidence block at the end of each pass:

```xml
<CONFIDENCE>
section=Category Overview|level=high|reason=Multiple sources confirm definition and scope
section=Pricing Intelligence|level=low|reason=Only 1 source with prices, no cross-validation
section=Technical Specifications|level=medium|reason=Specs from catalog, but no IS standard cross-check
</CONFIDENCE>
```

This feeds directly into the doubts report — low-confidence sections automatically get flagged.

**Impact:** High — you immediately see which sections need more data sources  
**Effort:** Medium — add parsing in `_parse_doubts`, extend `save_doubts` report

### 2. Add "NOT FOUND IN SOURCE" Explicit Gap Markers

Add this rule to `wiki_builder.md`:

> If a standard section (from the Required Structure) has NO data from any source, do NOT leave it empty or omit it. Instead write: `> 📭 **No data found in current sources.** This section requires additional source documents covering [specific data needed].`

**Impact:** High — you instantly see which sections need more data across 5000 categories  
**Effort:** Low — just a prompt change

### 3. Source Attribution Tags (lightweight version)

Instead of template's heavy `[SOURCE: doc, page]` on every line, add lightweight inline source hints:

> When stating a specific fact (price, spec value, brand claim), note the source type inline: `"₹3,500-4,200/m³ (from manufacturer catalog)"` or `"IS 2185 compliance required (from regulatory docs)"`

**Impact:** Medium — helps readers trust data without bloating  
**Effort:** Low — prompt instruction only

---

## ⚠️ Potential Issues to Watch

### 1. Web Search Timing
Currently web searches happen in ALL nodes (CREATE, UPDATE, ENRICH). For 5000 categories at scale, this could get expensive. Consider:
- **Rate limiting** web searches to max 3 per full pipeline run
- **Caching** search results per category so re-runs don't re-search

### 2. Token Usage at Scale
With Gemini 2.5 Pro at ~16K max_tokens output, a typical 6-source category run could use ~100K+ tokens. At 5000 categories:
- **Estimated total:** 500M+ tokens
- Consider batching and monitoring cost via the token reports

### 3. Doubt Volume
If the agent logs too many trivial doubts (e.g., "minor formatting difference between sources"), it'll create noise. The prompt says "Better to have 50 doubts than 1 wrong fact" — but at scale, you may need to tune this to focus on `high` severity only in reports.

---

## 📁 Final Directory Structure

```
Category_wiki/
├── config.py
├── main.py
├── data/inputs/           # Raw source files per mcat_id
├── skills/
│   ├── wiki_builder.md    # ✅ Generic, structure-aligned
│   └── enricher.md        # ✅ Generic, doubt-aware
├── graph/
│   ├── state.py           # ✅ doubts + _step_tokens fields
│   ├── nodes.py           # ✅ 5-tuple returns, token tracking
│   └── edges.py
├── utils/
│   ├── llm.py             # ✅ Token tracking per call
│   ├── wiki_manager.py    # ✅ save_doubts + save_token_usage
│   ├── web_search.py
│   ├── file_handler.py
│   └── preprocessor.py
├── wiki/
│   ├── index.md           # Master dashboard with doubts column
│   ├── items/             # Generated wiki articles
│   ├── logs/              # Execution logs per category
│   ├── references/        # Source references per category
│   └── doubts/            # Doubt reports per category
├── token_usage/           # ✅ Root-level token reports
├── wiki_structure.md      # Your reference structure doc
└── template.md            # Your extraction template reference
```

---

## 🏁 Ready to Test?

The system is fully wired. To verify everything end-to-end:

```bash
python main.py
```

Pick a category with multiple source files. After the run, check:
1. `wiki/items/[name].md` — does it follow the 11-section structure?
2. `wiki/doubts/[name]_doubts.md` — are doubts meaningful, not trivial?
3. `token_usage/[name]_tokens.md` — per-step breakdown present?
4. `wiki/index.md` — doubts column populated?

If you want me to implement **Recommendation #1 (Confidence Scoring)** or **#2 (Gap Markers)**, say the word and I'll wire them in.
