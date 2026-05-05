"""
WikiState — the single typed-dict that flows through every LangGraph node.

All keys are optional (total=False) so nodes can return partial updates.
LangGraph merges each node's return dict into the accumulated state.
"""
from typing import TypedDict


class WikiState(TypedDict, total=False):

    # ── Identity ──────────────────────────────────────────────────────────────
    mcat_id:   str               # e.g. "68865"
    mcat_name: str               # e.g. "AAC Block"
    item_name: str               # display name (= mcat_name)

    # ── Raw sources ───────────────────────────────────────────────────────────
    raw_sources:    list          # list of source dicts from preprocessor
    source_index:   int           # current position in the source loop
    current_source: str           # formatted text of the current source

    # ── Change tracking ───────────────────────────────────────────────────────
    new_sources:     list         # source dicts that are NEW (not yet processed)
    removed_sources: list         # filenames that were removed since last run
    all_sources:     list         # all source dicts (new + already processed)

    # ── Wiki content ──────────────────────────────────────────────────────────
    category:      str            # LLM-detected category
    existing_wiki: str            # pre-existing wiki content (if any)
    updated_wiki:  str            # current wiki draft (built iteratively)

    # ── Evaluator / Agentic Loop ──────────────────────────────────────────────
    eval_score:     float         # current evaluation score (0-10)
    eval_feedback:  str           # evaluator's improvement prompt
    eval_iteration: int           # which evaluation iteration we're on
    eval_section_scores: list     # per-section scores from evaluator
    eval_top_gaps:  list          # top gap descriptions from evaluator
    eval_data_needs: str          # what type of data the evaluator says is needed

    eval_data_request: dict       # {"calls": X, "pdfs": Y, "web_search": bool, "done": bool}
    
    evaluator_results_log: list   # Stores evaluator feedback per iteration for evaluator_result.md

    # ── Source pools (Agentic Picking) ────────────────────────────────────────
    pool_calls_available: int     # How many calls left in the pool
    pool_pdfs_available: int      # How many PDFs left in the pool

    # ── Source URL mapping (for clickable citations) ──────────────────────────
    source_url_map: dict          # { "call 1.json": "https://...", ... }

    # ── Logs, references & doubts (accumulated during run) ─────────────────────
    logs:       list              # list of log entry strings
    references: list              # list of reference dicts
    doubts:     list              # list of doubt dicts (parsed from LLM output)

    # ── Pipeline control ──────────────────────────────────────────────────────
    wiki_exists: bool             # whether wiki file pre-existed
    status:      str              # human-readable pipeline status
    _manifest:   dict             # hidden state for tracker
    _step_tokens: list            # per-step token usage snapshots
    _confidence:  list            # per-section confidence scores