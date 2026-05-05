"""
nodes.py — All LangGraph node functions for the Category Wiki pipeline.

Node execution order (full run with N sources):
  INPUT → CATEGORY → CHECK_WIKI
        → CREATE (source 0, no existing wiki)
          OR UPDATE (source 0, wiki exists)
        → [LOOP: LOAD_NEXT_SOURCE → UPDATE] × (N-1 remaining sources)
        → ENRICH → SAVE → INDEX

Source tracking:
  - On first run: all sources are new → all get processed
  - On re-run: only new/changed sources get processed
  - Removed sources trigger a cleanup pass in the wiki

Logging:
  Every node appends structured entries to state["logs"].
  The SAVE node writes these to wiki/logs_<cat>.md.

References:
  Every source processed gets a reference entry.
  The SAVE node writes these to wiki/references_<cat>.md.
"""
import logging
import re
import difflib
from datetime import datetime, timezone

from config import DETAILED_LOGS, MODEL, DYNAMIC_WEB_SEARCH

from graph.state import WikiState
from utils.file_handler import load_skill
from utils.preprocessor import load_sources_with_tracking, save_run_manifest
from utils.wiki_manager import (
    wiki_exists,
    read_existing_wiki,
    save_wiki,
    save_logs,
    save_references,
    save_doubts,
    save_evaluator_results,
    save_token_usage,
    rebuild_index,
    get_index_path,
)
from utils.llm import call_llm, get_token_log, reset_token_log, get_total_usage
from utils.web_search import web_search, format_results_for_llm, extract_search_queries

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _ts() -> str:
    """Current UTC timestamp string for log entries."""
    return datetime.now(timezone.utc).strftime("%H:%M:%S")


def _log(state: dict, node: str, message: str) -> list:
    """Append a log entry and return the updated logs list."""
    logs = list(state.get("logs", []))
    entry = (
        f"**[{_ts()}] {node}**\n\n"
        f"{message}"
    )
    logs.append(entry)
    return logs


# ─── Doubt parsing helpers ───────────────────────────────────────────────────

def _parse_doubts(text: str, step_num: int, node_name: str) -> list:
    """Extract <DOUBT>...</DOUBT> XML blocks from LLM output."""
    import xml.etree.ElementTree as ET
    doubts = []
    pattern = r'<DOUBT>(.*?)</DOUBT>'
    matches = re.findall(pattern, text, re.DOTALL)

    for idx, match in enumerate(matches):
        try:
            xml_str = f"<root>{match}</root>"
            root = ET.fromstring(xml_str)
            doubt = {
                "doubt_id":    step_num * 100 + idx + 1,
                "section":     (root.findtext("section") or "Unknown").strip(),
                "field":       (root.findtext("field") or "Unknown").strip(),
                "type":        (root.findtext("type") or "unknown").strip(),
                "question":    (root.findtext("question") or "").strip(),
                "evidence":    (root.findtext("evidence") or "").strip(),
                "severity":    (root.findtext("severity") or "medium").strip(),
                "action_taken":        (root.findtext("action_taken") or "").strip(),
                "suggested_resolution":(root.findtext("suggested_resolution") or "").strip(),
                "raised_at_step": step_num,
                "raised_at_node": node_name,
                "resolved": False,
            }
            doubts.append(doubt)
        except Exception as e:
            logger.warning("Could not parse doubt block %d: %s", idx, e)
    return doubts


def _parse_resolutions(text: str, existing_doubts: list,
                       step_num: int, node_name: str) -> list:
    """Scan for <RESOLVED doubt_id=NNN>reason</RESOLVED> and mark doubts."""
    pattern = r'<RESOLVED\s+doubt_id=["\']?(\d+)["\']?>(.*?)</RESOLVED>'
    matches = re.findall(pattern, text, re.DOTALL)
    for did_str, reason in matches:
        did = int(did_str)
        for d in existing_doubts:
            if d.get("doubt_id") == did and not d.get("resolved"):
                d["resolved"] = True
                d["resolved_at_step"] = step_num
                d["resolved_at_node"] = node_name
                d["resolution"] = reason.strip()
                logger.info("\u2705  DOUBT-%03d resolved at step %d", did, step_num)
    return existing_doubts


def _clean_doubts_from_text(text: str) -> str:
    """Remove all <DOUBT>, <RESOLVED>, <CONFIDENCE>, and <WEB_SEARCH_REASONING> XML blocks from wiki text."""
    text = re.sub(r'<DOUBT>.*?</DOUBT>', '', text, flags=re.DOTALL)
    text = re.sub(r'<RESOLVED\s+doubt_id=["\']?\d+["\']?>.*?</RESOLVED>', '', text, flags=re.DOTALL)
    text = re.sub(r'<CONFIDENCE>.*?</CONFIDENCE>', '', text, flags=re.DOTALL)
    # Strip <WEB_SEARCH_REASONING> block, handling cases where LLM forgets closing tag
    text = re.sub(r'<WEB_SEARCH_REASONING>.*?(?:</WEB_SEARCH_REASONING>|</updates>\s*)', '', text, flags=re.DOTALL)
    text = re.sub(r'</WEB_SEARCH_REASONING>\s*', '', text)
    return text.strip()


def _parse_confidence(text: str) -> list:
    """Extract <CONFIDENCE>...</CONFIDENCE> block and return section scores."""
    scores = []
    match = re.search(r'<CONFIDENCE>(.*?)</CONFIDENCE>', text, re.DOTALL)
    if not match:
        return scores
    
    for line in match.group(1).strip().split('\n'):
        line = line.strip()
        if not line or '|' not in line:
            continue
        parts = {}
        for segment in line.split('|'):
            if '=' in segment:
                key, val = segment.split('=', 1)
                parts[key.strip()] = val.strip()
        if parts.get('section') and parts.get('level'):
            scores.append({
                "section": parts['section'],
                "level": parts['level'],
                "reason": parts.get('reason', ''),
            })
    return scores


def call_agentic_llm(system_prompt: str, user_prompt: str, step_logger_name: str,
                     state: dict = None, step_num: int = 0,
                     node_name: str = "", allow_search: bool = True) -> tuple[str, list, list, list, dict, list]:
    """Call LLM, execute web searches, parse doubts, track tokens.
    
    Returns: (clean_text, web_refs, queries_found, new_doubts, step_tokens, confidence)
    """
    response = call_llm(system_prompt, user_prompt)
    queries_found = extract_search_queries(response) if allow_search else []
    web_search_refs = []
    
    if queries_found:
        logger.info("%s  │ LLM requested %d web search(es)", step_logger_name, len(queries_found))
        search_context = ""
        for q_obj in queries_found:
            rationale = q_obj["rationale"]
            query = q_obj["query"]
            result = web_search(query)
            search_context += f"\n\n--- SEARCH RATIONALE ---\n{rationale}\n\n{format_results_for_llm(result)}"
            
            # Store FULL URL and FULL query — no trimming
            web_search_refs.append({
                "label": f"WEB: {query}",
                "type": "web_search",
                "path": result.get("results", [{}])[0].get("url", "") if result.get("results") else "",
                "key_extractions": f"Rationale: {rationale}\nQuery: {query}",
                "data_points": f"{result.get('count', 0)} web results fetched",
                "web_results": [
                    {"title": r.get("title", ""), "url": r.get("url", "")}
                    for r in result.get("results", [])
                ],
                "rationale": rationale,
                "query": query
            })
            
        augmented_prompt = (
            f"{user_prompt}\n\n"
            f"ADDITIONAL CONTEXT FROM WEB SEARCH:\n{search_context}\n\n"
            f"Before outputting the final wiki incorporating this data, you MUST emit a brief explanation under the XML tag:\n"
            f"<WEB_SEARCH_REASONING>\n<inferred>What you inferred from the search results</inferred>\n<updates>How you updated the wiki</updates>\n</WEB_SEARCH_REASONING>\n\n"
            f"Now output the COMPLETE final wiki."
        )
        logger.info("%s  │ re-calling LLM with web context", step_logger_name)
        from utils.web_search import extract_search_reasoning
        response = call_llm(system_prompt, augmented_prompt)
        
        reasoning = extract_search_reasoning(response)
        if reasoning:
            for wr in web_search_refs:
                wr["inferred"] = reasoning.get("inferred", "")
                wr["updates"] = reasoning.get("updates", "")
                
    # Parse doubts from response
    new_doubts = _parse_doubts(response, step_num, node_name)
    if new_doubts:
        logger.info("%s  │ %d doubt(s) raised by agent", step_logger_name, len(new_doubts))
    
    # Parse confidence scores
    confidence = _parse_confidence(response)
    if confidence:
        logger.info("%s  │ Confidence scores: %s", step_logger_name,
                    ", ".join(f"{c['section']}={c['level']}" for c in confidence))
    
    # Check for resolved doubts
    if state:
        existing_doubts = list(state.get("doubts", []))
        _parse_resolutions(response, existing_doubts, step_num, node_name)
    
    # Clean XML tags from wiki text
    clean_text = _clean_doubts_from_text(response)
    
    # Capture per-step token snapshot
    step_tokens = {}
    log_entries = get_token_log()
    if log_entries:
        latest = log_entries[-1]
        step_tokens = {
            "step": step_num,
            "node": node_name,
            "prompt_tokens": latest.get("prompt_tokens", 0),
            "completion_tokens": latest.get("completion_tokens", 0),
            "total_tokens": latest.get("total_tokens", 0),
        }
        
    return clean_text, web_search_refs, queries_found, new_doubts, step_tokens, confidence


def _add_ref(state: dict, source: dict, key_extractions: str = "",
             data_points: str = "") -> list:
    """Add a reference entry and return the updated references list."""
    refs = list(state.get("references", []))
    
    if "original_sources" in source:
        for s in source["original_sources"]:
            refs.append({
                "label":           s.get("label", "unknown"),
                "type":            s.get("type", "unknown"),
                "path":            s.get("path", ""),
                "key_extractions": key_extractions,
                "data_points":     data_points,
            })
    else:
        refs.append({
            "label":           source.get("label", "unknown"),
            "type":            source.get("type", "unknown"),
            "path":            source.get("path", ""),
            "key_extractions": key_extractions,
            "data_points":     data_points,
        })
    return refs


def _sources_summary(sources: list) -> str:
    """One-line summary of sources for logging."""
    return ", ".join(f"{s['label']}({s['type']})" for s in sources)


# ─────────────────────────────────────────────────────────────────────────────
# 1. INPUT NODE
# ─────────────────────────────────────────────────────────────────────────────

def _build_source_url_map(sources: list) -> dict:
    """Build a mapping of source label → source_url from JSON metadata."""
    import json as _json
    url_map = {}
    for src in sources:
        label = src.get("label", "")
        path = src.get("path", "")
        if not path:
            continue
        try:
            from pathlib import Path as _P
            p = _P(path)
            if p.suffix.lower() == ".json" and p.exists():
                data = _json.loads(p.read_text(encoding="utf-8-sig"))
                # Call JSONs: metadata.source_url
                url = None
                if isinstance(data, dict):
                    meta = data.get("metadata", {})
                    if isinstance(meta, dict):
                        url = meta.get("source_url", "")
                    # PDF JSONs: extraction_metadata or top-level source_url
                    if not url:
                        emeta = data.get("extraction_metadata", {})
                        if isinstance(emeta, dict):
                            url = emeta.get("source_url", "")
                    if not url:
                        url = data.get("source_url", "")
                if url:
                    url_map[label] = url
        except Exception:
            pass
    return url_map


def pick_sources_node(state: WikiState) -> dict:
    """Agentic picker: fetches data from call and PDF pools.
    
    - First run: picks 10 calls + 5 PDFs to build Version 1.
    - Subsequent runs: picks 5 calls OR 3 PDFs based on evaluator feedback.
    """
    import os
    import shutil
    from pathlib import Path
    from config import PROJECT_ROOT, RAW_DIR

    mcat_id   = str(state.get("mcat_id", "")).strip()
    mcat_name = state.get("mcat_name", "").strip()

    if not mcat_id:
        raise ValueError("mcat_id is required but was empty.")

    import json as _json
    from pdf_pipeline import extract_single_pdf
    
    # Setup directories
    call_pool_dir = PROJECT_ROOT / "call" / f"call_{mcat_id}"
    pdf_pool_dir  = PROJECT_ROOT / "pdfs" / f"pdf_{mcat_id}"  # Raw PDFs folder
    input_dir     = RAW_DIR / f"input_{mcat_id}"
    
    input_dir.mkdir(parents=True, exist_ok=True)
    
    # Identify available files in pools
    available_calls = []
    if call_pool_dir.exists():
        available_calls = [f for f in call_pool_dir.iterdir() if f.is_file() and f.suffix == '.json']
    
    available_pdfs = []
    if pdf_pool_dir.exists():
        available_pdfs = [f for f in pdf_pool_dir.iterdir() if f.is_file() and f.suffix.lower() == '.pdf']

    # Filter out files already copied (Calls)
    existing_in_input = {f.name for f in input_dir.iterdir()}
    calls_to_pick = [f for f in available_calls if f.name not in existing_in_input]
    
    # Filter out files already processed (PDFs)
    pdf_manifest_path = pdf_pool_dir / ".pdf_manifest.json"
    pdf_manifest = {}
    if pdf_manifest_path.exists():
        try:
            pdf_manifest = _json.loads(pdf_manifest_path.read_text(encoding="utf-8"))
        except Exception:
            pdf_manifest = {}
            
    pdfs_to_pick = [f for f in available_pdfs if f.name not in pdf_manifest]

    # Decide how many to pick
    data_req = state.get("eval_data_request", {})
    is_first_run = len(existing_in_input) == 0 or (len(existing_in_input) == 1 and list(existing_in_input)[0] == ".manifest.json")

    picked_calls = []
    picked_pdfs = []
    
    if is_first_run:
        # V1 logic: 10 calls + 5 PDFs
        picked_calls = calls_to_pick[:10]
        picked_pdfs  = pdfs_to_pick[:5]
        logger.info(f"🚀 INITIAL RUN: Picking {len(picked_calls)} calls and {len(picked_pdfs)} PDFs for V1.")
    else:
        # Iteration logic using exact numbers
        req_calls = data_req.get("calls", 0)
        req_pdfs = data_req.get("pdfs", 0)
        req_web = data_req.get("web_search", False)
        
        if req_calls > 0:
            picked_calls = calls_to_pick[:req_calls]
            logger.info(f"🔄 EVAL PICK: Picking {len(picked_calls)} calls.")
            
        if req_pdfs > 0:
            picked_pdfs = pdfs_to_pick[:req_pdfs]
            logger.info(f"🔄 EVAL PICK: Picking {len(picked_pdfs)} PDFs.")
            
        if req_web:
            logger.info(f"🔄 EVAL PICK: Web search requested by evaluator.")
            
        if not picked_calls and not picked_pdfs and not req_web:
            logger.warning("⚠️  EVAL PICK: Evaluator requested 0 new sources. This might lead to an infinite loop if score < 9.0.")

    # Copy picked calls directly
    for f in picked_calls:
        shutil.copy2(f, input_dir / f.name)
        
    # Extract picked PDFs dynamically
    # Get existing PDF count to continue numbering
    existing_pdfs = list(input_dir.glob("pdf *-*.json"))
    pdf_counter = len(existing_pdfs) + 1
    
    for f in picked_pdfs:
        json_name = f"pdf {pdf_counter}-{f.stem}.json"
        out_path = input_dir / json_name
        logger.info(f"📄 Extracting {f.name} to {json_name} via LLM...")
        
        success = extract_single_pdf(f, mcat_name, out_path)
        if success:
            pdf_manifest[f.name] = {"status": "processed", "output_file": json_name}
            pdf_counter += 1
        else:
            pdf_manifest[f.name] = {"status": "failed_read"}
            
    # Save PDF manifest if any were processed
    if picked_pdfs and pdf_pool_dir.exists():
        pdf_manifest_path.write_text(_json.dumps(pdf_manifest, indent=2), encoding="utf-8")

    # Now load the sources using our tracker
    tracking = load_sources_with_tracking(mcat_id)
    all_sources     = tracking["all_sources"]
    new_sources     = tracking["new_sources"]
    removed_sources = tracking["removed_sources"]
    manifest        = tracking["manifest"]

    # CRITICAL FIX: Save the manifest immediately so the next loop knows these are processed!
    if manifest and mcat_id:
        save_run_manifest(mcat_id, manifest)

    # For processing, we ONLY process the new_sources in this turn!
    sources_to_process = new_sources
    
    # If it's a web_search turn with 0 new sources, create a dummy source
    req_web = data_req.get("web_search", False) if not is_first_run else False
    if not sources_to_process and req_web:
        sources_to_process = [{
            "label": "SYSTEM: Web Search Turn",
            "type": "system",
            "hash": "web",
            "content": "No new local data. Evaluator requested Web Search to fill remaining gaps."
        }]

    # Concatenate all new sources into a single mega-source for the prompt
    combined_content = ""
    for idx, s in enumerate(sources_to_process):
        combined_content += f"--- SOURCE {idx + 1} ({s.get('label', 'sys')}) ---\n{s.get('content', '')}\n\n"
        
    source_url_map = _build_source_url_map(all_sources)

    calls_left = len(calls_to_pick) - len([f for f in picked_calls if f in calls_to_pick])
    pdfs_left  = len(pdfs_to_pick) - len([f for f in picked_pdfs if f in pdfs_to_pick])

    log_msg = (
        f"- Action: **PICK SOURCES**\n"
        f"- Picked this turn: {len(picked_calls)} calls, {len(picked_pdfs)} PDFs\n"
        f"- Pools remaining: {calls_left} calls, {pdfs_left} PDFs\n"
        f"- Total ingested so far: {len(all_sources)}\n"
        f"- Source URLs mapped: {len(source_url_map)}\n"
    )

    # Build return dict
    ret = {
        "item_name":        mcat_name,
        "raw_sources":      sources_to_process,
        "all_sources":      all_sources,
        "new_sources":      new_sources,
        "removed_sources":  removed_sources,
        "source_index":     0,
        "current_source":   combined_content,
        "source_url_map":   source_url_map,
        "pool_calls_available": calls_left,
        "pool_pdfs_available":  pdfs_left,
        "logs":             _log(state, "📥 PICK SOURCES", log_msg),
        "status":           "sources_picked",
        "_manifest":        manifest,
    }
    
    if is_first_run:
        from utils.llm import reset_token_log
        reset_token_log()
        ret.update({
            "references":       [],
            "doubts":           [],
            "_step_tokens":     [],
            "_confidence":      [],
            "eval_score":       0.0,
            "eval_feedback":    "",
            "eval_iteration":   0,
            "eval_section_scores": [],
            "eval_top_gaps":    [],
            "eval_data_request": {"calls": 0, "pdfs": 0, "web_search": False, "done": False},
        })
        
    return ret


# ─────────────────────────────────────────────────────────────────────────────
# 2. CATEGORY NODE
# ─────────────────────────────────────────────────────────────────────────────

def category_node(state: WikiState) -> dict:
    """Detect item category using the first source + item name."""
    skill_prompt = load_skill("category_detector.md")

    system_prompt = skill_prompt or (
        "You are a category classification expert for an Indian B2B marketplace. "
        "Given an item name and its data, identify the single most appropriate "
        "primary category. Respond with ONLY the category name in Title Case."
    )

    user_prompt = (
        f"Item Name: {state['item_name']}\n\n"
        f"Source Data:\n{state['current_source']}"
    )

    category = call_llm(system_prompt, user_prompt).strip().strip('"').strip("'")

    raw_sources = state.get('raw_sources', [])
    source_label = raw_sources[0].get('label', '?') if raw_sources else "none (skipped - 0 new files)"

    log_msg = (
        f"- Input: item_name=`{state['item_name']}`, "
        f"source=`{source_label}`\n"
        f"- LLM Inference: **{category}**\n"
        f"- Model used for classification"
    )

    logger.info("🏷️  CATEGORY  │ detected → %s", category)

    return {
        "category": category,
        "logs":     _log(state, "🏷️ CATEGORY", log_msg),
        "status":   "category_detected",
    }


# ─────────────────────────────────────────────────────────────────────────────
# 3. CHECK WIKI NODE
# ─────────────────────────────────────────────────────────────────────────────

def check_wiki_node(state: WikiState) -> dict:
    """Check whether a wiki page already exists for this item."""
    # If we are in an agentic loop, the wiki is already in memory
    if state.get("eval_iteration", 0) > 0:
        existing = state.get("existing_wiki", "")
        log_msg = (
            f"- Agentic Loop Iteration: **{state['eval_iteration']}**\n"
            f"- In-memory wiki size: {len(existing)} chars\n"
            f"- Decision: UPDATE existing wiki"
        )
        logger.info("🔍  CHECK  │ in-memory wiki_exists=True  existing_len=%d", len(existing))
        return {
            "wiki_exists": True,
            # existing_wiki remains unchanged in state
            "logs": _log(state, "🔍 CHECK WIKI", log_msg),
            "status": "wiki_checked_memory",
        }

    exists   = wiki_exists(state["item_name"])
    existing = read_existing_wiki(state["item_name"]) if exists else ""

    log_msg = (
        f"- Wiki file exists on disk: **{'Yes' if exists else 'No'}**\n"
        f"- Existing wiki size: {len(existing)} chars\n"
        f"- Decision: {'UPDATE existing wiki' if exists else 'CREATE new wiki'}"
    )

    logger.info(
        "🔍  CHECK  │ disk wiki_exists=%s  existing_len=%d",
        exists, len(existing),
    )

    return {
        "wiki_exists":   exists,
        "existing_wiki": existing,
        "logs":          _log(state, "🔍 CHECK WIKI", log_msg),
        "status":        "wiki_checked",
    }


# ─────────────────────────────────────────────────────────────────────────────
# 4. CREATE NODE — first source, no existing wiki
# ─────────────────────────────────────────────────────────────────────────────

def _build_wiki_from_sources(
    state: WikiState,
    sources: list,
    existing_wiki: str,
    is_create: bool,
) -> tuple:
    """
    Core logic: process each source individually, one LLM call per source.
    Returns (final_wiki, all_refs, all_doubts, all_step_tokens, confidence, log_lines)
    """
    skill_prompt = load_skill("wiki_builder.md")
    system_prompt = skill_prompt or (
        "You are an expert technical writer for an Indian B2B marketplace. "
        "Build or update a comprehensive Wikipedia-style markdown article. "
        "Maintain 9-section structure and inline [source.json] citations."
    )
    if not DYNAMIC_WEB_SEARCH:
        system_prompt += (
            "\n\n***SYSTEM DIRECTIVE: LIVE WEB SEARCH IS DISABLED. "
            "Rely strictly on provided source data. DO NOT emit <WEB_SEARCH> tags!***"
        )

    removed = state.get("removed_sources", [])
    removed_context = ""
    if removed:
        removed_context = (
            f"\n\nNOTE: The following sources were REMOVED — do NOT include their data: "
            f"{', '.join(removed)}"
        )

    eval_context = ""
    eval_feedback = state.get("eval_feedback", "")
    eval_score    = state.get("eval_score", 0.0)
    eval_gaps     = state.get("eval_top_gaps", [])
    if eval_feedback and eval_score > 0:
        eval_context = (
            f"\n\n── EVALUATOR FEEDBACK (Score: {eval_score}/10) ──\n"
            f"{eval_feedback}\n\n"
        )
        if eval_gaps:
            eval_context += "Top Gaps to Address:\n"
            for i, gap in enumerate(eval_gaps, 1):
                eval_context += f"  {i}. {gap}\n"
            eval_context += "\nPRIORITY: Address these gaps using the new source data.\n"

    all_refs         = list(state.get("references", []))
    all_doubts       = list(state.get("doubts", []))
    all_step_tokens  = list(state.get("_step_tokens", []))
    confidence       = state.get("_confidence", [])
    log_lines        = []
    wiki_content     = existing_wiki
    total            = len(sources)

    chunk_size = 3
    for chunk_idx in range(0, total, chunk_size):
        wiki_content_before = wiki_content
        batch = sources[chunk_idx:chunk_idx + chunk_size]
        
        src_labels = [s.get("label", f"source_{chunk_idx+i+1}") for i, s in enumerate(batch)]
        src_label_str = ", ".join(src_labels)
        
        src_content = ""
        for i, s in enumerate(batch):
            src_content += f"--- SOURCE {chunk_idx+i+1}: {src_labels[i]} ---\n{s.get('content', '')}\n\n"
            
        step_num  = state.get("eval_iteration", 0) * 100 + (chunk_idx // chunk_size) + 1

        # Build doubts context from unresolved ones
        unresolved = [d for d in all_doubts if not d.get("resolved")]
        doubt_context = ""
        if unresolved:
            doubt_context = "\n\n── Unresolved Doubts ──\n"
            doubt_context += "If this source resolves any, emit <RESOLVED doubt_id=NNN>reason</RESOLVED>.\n\n"
            for d in unresolved:
                doubt_context += (
                    f"- [Doubt {d.get('doubt_id','?')}] {d['section']}/{d['field']}: "
                    f"{d['question']}\n"
                )

        if is_create and chunk_idx == 0:
            # First source ever → create from scratch
            action_verb = "CREATE"
            user_prompt = (
                f"Item Name: {state['item_name']}\n"
                f"Category: {state['category']}\n"
                f"Sources {chunk_idx+1} to {chunk_idx+len(batch)} of {total}: [{src_label_str}]\n\n"
                f"**STRICT DIRECTIVE**: Include inline citations for every data point, "
                f"e.g., [{src_labels[0]}] or [Web].\n\n"
                f"── Source Data ──\n{src_content}\n\n"
                f"Create a comprehensive wiki article from these sources. "
                f"Structure it with all 9 sections. More sources will follow."
                f"{removed_context}{eval_context}"
            )
        else:
            # All subsequent sources → merge into existing wiki
            action_verb = "UPDATE"
            user_prompt = (
                f"Item Name: {state['item_name']}\n"
                f"Category: {state['category']}\n"
                f"Sources {chunk_idx+1} to {chunk_idx+len(batch)} of {total}: [{src_label_str}]\n\n"
                f"**STRICT DIRECTIVE**: Include inline citations for every data point, "
                f"e.g., [{src_labels[0]}] or [Web].\n\n"
                f"── New Source Data ──\n{src_content}\n\n"
                f"── Existing Wiki (merge into this) ──\n{wiki_content}\n\n"
                f"Merge these sources into the wiki. Preserve existing content, "
                f"add new data points, flag contradictions with [CONFLICT: ...].\n"
                f"**WEB SEARCH**: If the provided source data is thin or you see specific gaps mentioned in the evaluator feedback below, "
                f"use your SEARCH tool proactively to find missing specs, prices, or regulatory details for the Indian market."
                f"{removed_context}{doubt_context}{eval_context}"
            )

        logger.info(
            "📄  %s  │ sources %d-%d/%d → %s",
            action_verb, chunk_idx + 1, chunk_idx + len(batch), total, src_label_str,
        )

        new_wiki, web_refs, _, new_doubts, step_tokens, step_conf = call_agentic_llm(
            system_prompt, user_prompt, f"📄 {action_verb} [{chunk_idx+1}-{chunk_idx+len(batch)}/{total}]",
            state=state, step_num=step_num, node_name=action_verb,
            allow_search=DYNAMIC_WEB_SEARCH,
        )

        # Strip extraction_summary tag
        summary_match = re.search(
            r"<extraction_summary>(.*?)</extraction_summary>", new_wiki, re.DOTALL
        )
        extraction_summary = f"Sources {chunk_idx+1}-{chunk_idx+len(batch)}: {src_label_str}"
        if summary_match:
            extraction_summary = summary_match.group(1).strip()
            new_wiki = new_wiki.replace(summary_match.group(0), "").strip()

        wiki_content = new_wiki
        is_create = False  # After first batch, all become updates

        # Accumulate refs
        for s in batch:
            all_refs.extend(_add_ref(
                state, s,
                key_extractions=extraction_summary,
                data_points=f"Processed in batch of {len(batch)}",
            ))
        for wr in web_refs:
            all_refs.append(wr)

        # Accumulate doubts & tokens
        all_doubts.extend(new_doubts)
        if step_tokens:
            all_step_tokens.append(step_tokens)
        if step_conf:
            confidence = step_conf

        # Generate diff for this batch
        diff = difflib.unified_diff(
            (wiki_content_before or "").splitlines(keepends=True),
            (wiki_content or "").splitlines(keepends=True),
            fromfile='current_wiki',
            tofile='updated_wiki',
            n=0  # minimal context for cleaner logs
        )
        diff_text = "".join(diff)
        diff_block = f"\n\n```diff\n{diff_text}\n```" if diff_text else "\n\n*(No text changes in this batch)*"

        log_lines.append(
            f"- **Sources {chunk_idx+1}-{chunk_idx+len(batch)}/{total}** `{src_label_str}`: "
            f"{len(src_content):,} chars → wiki now {len(wiki_content):,} chars "
            f"({step_tokens.get('total_tokens', 0):,} tokens)\n"
            f"  - **Extraction Summary:** {extraction_summary}"
            f"{diff_block}"
        )

    return wiki_content, all_refs, all_doubts, all_step_tokens, confidence, log_lines


# ─────────────────────────────────────────────────────────────────────────────
# 4. CREATE NODE — no existing wiki, process sources one by one
# ─────────────────────────────────────────────────────────────────────────────

def create_node(state: WikiState) -> dict:
    """Build a brand-new wiki by processing each picked source individually."""
    sources = state.get("raw_sources", [])
    if not sources:
        logger.warning("📝 CREATE │ no sources to process, skipping")
        return {"status": "create_skipped", "logs": state.get("logs", [])}

    wiki_content, refs, doubts, tokens, confidence, log_lines = _build_wiki_from_sources(
        state=state,
        sources=sources,
        existing_wiki="",
        is_create=True,
    )

    log_msg = (
        f"- Action: **CREATE** (one LLM call per source)\n"
        f"- Sources processed: {len(sources)}\n"
        f"- Final wiki size: {len(wiki_content):,} chars\n\n"
        + "\n".join(log_lines)
    )
    logger.info("📝  CREATE  │ %d sources → %d chars", len(sources), len(wiki_content))

    return {
        "updated_wiki":  wiki_content,
        "existing_wiki": wiki_content,
        "logs":          _log(state, "📝 CREATE", log_msg),
        "references":    refs,
        "doubts":        doubts,
        "_step_tokens":  tokens,
        "_confidence":   confidence,
        "status":        "wiki_created",
    }


# ─────────────────────────────────────────────────────────────────────────────
# 5. UPDATE NODE — existing wiki, process sources one by one
# ─────────────────────────────────────────────────────────────────────────────

def update_node(state: WikiState) -> dict:
    """Merge each picked source individually into the existing wiki."""
    sources = state.get("raw_sources", [])
    if not sources:
        logger.warning("🔄 UPDATE │ no new sources to process")
        return {"status": "update_skipped", "logs": state.get("logs", [])}

    iteration = state.get("eval_iteration", 0)

    wiki_content, refs, doubts, tokens, confidence, log_lines = _build_wiki_from_sources(
        state=state,
        sources=sources,
        existing_wiki=state.get("existing_wiki", ""),
        is_create=False,
    )

    log_msg = (
        f"- Action: **UPDATE** iteration {iteration} (one LLM call per source)\n"
        f"- Sources processed: {len(sources)}\n"
        f"- Final wiki size: {len(wiki_content):,} chars\n\n"
        + "\n".join(log_lines)
    )
    logger.info("🔄  UPDATE  │ iter=%d  %d sources → %d chars", iteration, len(sources), len(wiki_content))

    return {
        "updated_wiki":  wiki_content,
        "logs":          _log(state, "🔄 UPDATE", log_msg),
        "references":    refs,
        "doubts":        doubts,
        "_step_tokens":  tokens,
        "_confidence":   confidence,
        "status":        f"wiki_updated_iter_{iteration}",
    }



# ─────────────────────────────────────────────────────────────────────────────
# 7. ENRICH NODE
# ─────────────────────────────────────────────────────────────────────────────

def enrich_node(state: WikiState) -> dict:
    """Final polish: cross-links, insights, market patterns, formatting.
    
    If the LLM signals it needs more information via [WEB_SEARCH]...[/WEB_SEARCH]
    tags, this node performs those searches, injects the results, and calls the
    LLM again for a final enriched output.
    """
    skill_prompt = load_skill("enricher.md")

    system_prompt = skill_prompt or (
        "You are a wiki enrichment specialist for an Indian B2B marketplace. "
        "Enhance the wiki article with cross-references, market insights, "
        "buyer patterns, a Quick Facts infobox, and a See Also section. "
        "Return the COMPLETE enriched article in markdown."
    )

    all_sources = state.get("all_sources", state.get("raw_sources", []))

    # Inject existing doubt context so LLM can potentially resolve them
    existing_doubts = state.get("doubts", [])
    doubt_context = ""
    unresolved = [d for d in existing_doubts if not d.get("resolved")]
    if unresolved:
        doubt_lines = []
        for d in unresolved:
            doubt_lines.append(
                f"  - DOUBT-{d['doubt_id']:03d} [{d['severity']}]: "
                f"{d['section']} > {d['field']} — {d['question']}"
            )
        doubt_context = (
            f"\n\n── UNRESOLVED DOUBTS FROM EARLIER STEPS ──\n"
            f"If you find evidence that resolves any of these, emit:\n"
            f"<RESOLVED doubt_id=NNN>Your resolution reason</RESOLVED>\n\n"
            + "\n".join(doubt_lines)
        )

    user_prompt = (
        f"Item Name: {state['item_name']}\n"
        f"Category: {state['category']}\n"
        f"Total Sources Ingested: {len(all_sources)}\n\n"
        f"── Wiki Article ──\n{state['updated_wiki']}"
        f"{doubt_context}"
    )

    # Enrich step is the next sequence number after all source processing
    enrich_step = len(state.get("raw_sources", [])) + 1

    enriched, web_refs, queries_found, new_doubts, step_tokens, confidence = call_agentic_llm(
        system_prompt, user_prompt, "✨  ENRICH",
        state=state, step_num=enrich_step, node_name="ENRICH"
    )

    log_msg = (
        f"- Action: **ENRICH** (final polish pass)\n"
        f"- Wiki before enrichment: {len(state['updated_wiki'])} chars\n"
        f"- Wiki after enrichment: {len(enriched)} chars\n"
        f"- Delta: {len(enriched) - len(state['updated_wiki']):+d} chars\n"
        f"- Web searches triggered: {len(queries_found) if queries_found else 0}\n"
        f"- Doubts raised: {len(new_doubts)}\n"
        f"- Doubts resolved: {sum(1 for d in existing_doubts if d.get('resolved'))}\n"
        f"- Tokens: {step_tokens.get('total_tokens', 0):,} (in={step_tokens.get('prompt_tokens', 0):,} out={step_tokens.get('completion_tokens', 0):,})\n"
        f"- Enhancements: cross-links, market intelligence, "
        f"Quick Facts, See Also, metadata\n"
        f"- System prompt: `enricher.md`"
    )
    
    if web_refs:
        log_msg += "\n\n**🌐 Web Searches Executed:**\n"
        for wr in web_refs:
            q = wr.get("query", "")
            rationale = wr.get("rationale", "")
            inferred = wr.get("inferred", "")
            updates = wr.get("updates", "")
            cnt = wr.get("data_points", "")
            log_msg += f"- 🔍 **Query:** `{q}` ({cnt})\n"
            log_msg += f"  - **Rationale:** {rationale}\n"
            if inferred or updates:
                log_msg += f"  - **Inferred:** {inferred}\n"
                log_msg += f"  - **Updates made:** {updates}\n"
            if wr.get("web_results"):
                url = wr["web_results"][0].get("url", "")
                if url:
                    log_msg += f"  - **Top hit:** {url}\n"
    
    if DETAILED_LOGS:
        old_text = state['updated_wiki']
        diff_lines = list(difflib.unified_diff(
            old_text.splitlines(keepends=True),
            enriched.splitlines(keepends=True),
            fromfile='Before Enrich', tofile='After Enrich', n=1
        ))
        diff_text = "".join(diff_lines)
        log_msg += f"\n\n<details><summary><b>View Structural Enhancements (Diff - Expand)</b></summary>\n\n```diff\n{diff_text}\n```\n</details>"

    # Merge existing refs + web search refs
    refs = list(state.get("references", []))
    for wr in web_refs:
        refs.append(wr)

    # Final doubts = existing (potentially resolved) + new from enrich
    all_doubts = list(existing_doubts) + new_doubts

    # Accumulate tokens
    all_step_tokens = list(state.get("_step_tokens", []))
    if step_tokens:
        all_step_tokens.append(step_tokens)

    logger.info("✨  ENRICH  │ final wiki → %d chars", len(enriched))

    return {
        "updated_wiki": enriched,
        "logs":         _log(state, "✨ ENRICH", log_msg),
        "references":   refs,
        "doubts":       all_doubts,
        "_step_tokens": all_step_tokens,
        "_confidence":  confidence,
        "status":       "wiki_enriched",
    }


# ─────────────────────────────────────────────────────────────────────────────
# 8. EVALUATE NODE — Scores the wiki, drives the agentic loop
# ─────────────────────────────────────────────────────────────────────────────

def _parse_evaluation(text: str) -> dict:
    """Parse <EVALUATION>...</EVALUATION> XML block from evaluator response."""
    import xml.etree.ElementTree as ET
    result = {
        "overall_score": 0.0,
        "overall_assessment": "",
        "section_scores": [],
        "top_gaps": [],
        "improvement_prompt": "",
        "data_needs": "",
        "data_request": {
            "calls": 0,
            "pdfs": 0,
            "web_search": False,
            "done": False
        }
    }
    
    match = re.search(r'<EVALUATION>(.*?)</EVALUATION>', text, re.DOTALL)
    if not match:
        logger.warning("Could not find <EVALUATION> block in evaluator response")
        # Try to extract score from plain text
        score_match = re.search(r'(?:overall[_ ]?score|score)[:\s]*(\d+(?:\.\d+)?)', text, re.IGNORECASE)
        if score_match:
            result["overall_score"] = float(score_match.group(1))
        return result
    
    xml_str = match.group(1).strip()
    
    # Parse overall_score
    score_match = re.search(r'<overall_score>(.*?)</overall_score>', xml_str, re.DOTALL)
    if score_match:
        try:
            result["overall_score"] = float(score_match.group(1).strip())
        except ValueError:
            pass
    
    # Parse overall_assessment
    assess_match = re.search(r'<overall_assessment>(.*?)</overall_assessment>', xml_str, re.DOTALL)
    if assess_match:
        result["overall_assessment"] = assess_match.group(1).strip()
    
    # Parse section scores
    section_pattern = r'<section\s+name="([^"]+)"\s+score="(\d+)">(.*?)</section>'
    for m in re.finditer(section_pattern, xml_str, re.DOTALL):
        result["section_scores"].append({
            "name": m.group(1),
            "score": int(m.group(2)),
            "reason": m.group(3).strip(),
        })
    
    # Parse top_gaps
    gaps_match = re.search(r'<top_gaps>(.*?)</top_gaps>', xml_str, re.DOTALL)
    if gaps_match:
        for line in gaps_match.group(1).strip().split('\n'):
            line = line.strip()
            if line and re.match(r'\d+\.', line):
                result["top_gaps"].append(re.sub(r'^\d+\.\s*', '', line))
    
    # Parse improvement_prompt
    imp_match = re.search(r'<improvement_prompt>(.*?)</improvement_prompt>', xml_str, re.DOTALL)
    if imp_match:
        result["improvement_prompt"] = imp_match.group(1).strip()
    
    # Parse data_needs
    dn_match = re.search(r'<data_needs>(.*?)</data_needs>', xml_str, re.DOTALL)
    if dn_match:
        result["data_needs"] = dn_match.group(1).strip()
    # Parse data_request
    dr_match = re.search(r'<data_request>(.*?)</data_request>', xml_str, re.DOTALL)
    if dr_match:
        dr_str = dr_match.group(1).lower()
        
        c_match = re.search(r'calls:\s*(\d+)', dr_str)
        if c_match:
            result["data_request"]["calls"] = int(c_match.group(1))  # No hard cap — agent decides
            
        p_match = re.search(r'pdfs:\s*(\d+)', dr_str)
        if p_match:
            result["data_request"]["pdfs"] = int(p_match.group(1))  # No hard cap — agent decides
            
        w_match = re.search(r'web_search:\s*(true|false)', dr_str)
        if w_match:
            result["data_request"]["web_search"] = w_match.group(1) == "true"
            
    # Default to done if >= 9.0
    if result["overall_score"] >= 9.0:
        result["data_request"]["done"] = True
    
    return result


def evaluate_node(state: WikiState) -> dict:
    """Score the current wiki and produce actionable improvement feedback."""
    skill_prompt = load_skill("evaluator.md")
    
    if not skill_prompt:
        logger.warning("skills/evaluator.md not found — skipping evaluation, defaulting score=10")
        return {
            "eval_score": 10.0,
            "eval_feedback": "",
            "eval_iteration": state.get("eval_iteration", 0) + 1,
            "eval_next_action": "done",
            "status": "evaluation_skipped",
        }
    
    processed = len(state.get("all_sources", []))
    iteration = state.get("eval_iteration", 0) + 1
    
    calls_avail = state.get("pool_calls_available", 0)
    pdfs_avail  = state.get("pool_pdfs_available", 0)
    
    user_prompt = (
        f"Item Name: {state.get('item_name', 'Unknown')}\n"
        f"Category: {state.get('category', 'Unknown')}\n"
        f"Sources Ingested So Far: {processed}\n"
        f"Evaluation Iteration: {iteration}\n\n"
        f"── SOURCE POOLS AVAILABLE ──\n"
        f"Buyer Calls Remaining: {calls_avail}\n"
        f"Seller PDFs Remaining: {pdfs_avail}\n"
        f"NOTE: If you need to pick next, you MUST ONLY pick a source type that has > 0 remaining.\n\n"
        f"── WIKI ARTICLE TO EVALUATE ──\n"
        f"{state.get('updated_wiki', '')}\n"
    )
    
    response = call_llm(skill_prompt, user_prompt)
    eval_data = _parse_evaluation(response)
    
    score = eval_data["overall_score"]
    data_req = eval_data["data_request"]
    
    # Force done if score >= 9.0
    if score >= 9.0:
        data_req["done"] = True

    # Cap by iteration limits (max 5 calls, max 3 PDFs per loop)
    data_req["calls"] = min(int(data_req.get("calls", 0)), 5)
    data_req["pdfs"]  = min(int(data_req.get("pdfs", 0)), 3)

    # Further cap by actual pool availability
    data_req["calls"] = min(data_req["calls"], calls_avail)
    data_req["pdfs"] = min(data_req["pdfs"], pdfs_avail)



    # If agent asked for nothing but score is low and data is available, force a pick
    if not data_req.get("done") and score < 9.0:
        # User requested: Web search MUST always be true until threshold is reached.
        data_req["web_search"] = True
        
        if data_req["calls"] == 0 and data_req["pdfs"] == 0:
            if calls_avail > 0:
                data_req["calls"] = min(5, calls_avail)
                logger.info(f"📊 EVAL NUDGE: Score {score} low, forcing pick of {data_req['calls']} calls.")
            elif pdfs_avail > 0:
                data_req["pdfs"] = min(3, pdfs_avail)
                logger.info(f"📊 EVAL NUDGE: Score {score} low, forcing pick of {data_req['pdfs']} PDFs.")
            else:
                logger.info(f"📊 EVAL NUDGE: Score {score} low, no pool left, forcing web search.")

    # If truly nothing to do, mark done
    if data_req["calls"] == 0 and data_req["pdfs"] == 0 and not data_req["web_search"]:
        data_req["done"] = True

    # ── MAX ITERATION LIMIT (3) ──
    if iteration >= 3 and not data_req.get("done"):
        logger.warning(f"⚠️ Max iterations (3) reached. Forcing 'done' to output latest best version.")
        data_req["done"] = True
        data_req["calls"] = 0
        data_req["pdfs"] = 0
        data_req["web_search"] = False

    # ── ROLLBACK IF SCORE DROPS ──
    v1_score = state.get("eval_score", 0.0)
    updated_wiki_to_return = state.get("updated_wiki", "")
    existing_wiki_to_return = state.get("existing_wiki", "")
    
    if iteration > 1 and score < v1_score:
        logger.warning(f"⚠️ V{iteration} score ({score}) is worse than V{iteration-1} ({v1_score}). Rolling back wiki to V{iteration-1}.")
        
        # Rollback the wiki content
        updated_wiki_to_return = existing_wiki_to_return
        score = v1_score  # Restore the better score
        
        # If it got worse, it might be confused. Best to stop and output the good version.
        data_req["done"] = True
        data_req["calls"] = 0
        data_req["pdfs"] = 0
        data_req["web_search"] = False
        
        eval_data["overall_assessment"] = f"[ROLLED BACK TO V{iteration-1}] " + eval_data["overall_assessment"]
    else:
        # Score improved or stayed the same. This updated wiki is now our new baseline.
        existing_wiki_to_return = updated_wiki_to_return
    
    # Build section scores summary for logging
    section_summary = ""
    if eval_data["section_scores"]:
        section_summary = "\n".join(
            f"  - {s['name']}: **{s['score']}/10** — {s['reason']}"
            for s in eval_data["section_scores"]
        )
    
    gaps_summary = ""
    if eval_data["top_gaps"]:
        gaps_summary = "\n".join(f"  {i+1}. {g}" for i, g in enumerate(eval_data["top_gaps"]))
    
    log_msg = (
        f"- Action: **EVALUATE** (iteration {iteration})\n"
        f"- Overall Score: **{score}/10**\n"
        f"- Assessment: {eval_data['overall_assessment']}\n"
        f"- Data Requested: {data_req['calls']} calls, {data_req['pdfs']} PDFs, web_search={data_req['web_search']}\n"
    )
    if section_summary:
        log_msg += f"\n**Section Scores:**\n{section_summary}\n"
    if gaps_summary:
        log_msg += f"\n**Top Gaps:**\n{gaps_summary}\n"
    if eval_data["data_needs"]:
        log_msg += f"\n**Reasoning:** {eval_data['data_needs']}\n"
        
    logger.info(
        "📊  EVALUATE  │ iteration=%d  score=%.1f/10  req=(calls:%d pdfs:%d web:%s)",
        iteration, score, data_req["calls"], data_req["pdfs"], data_req["web_search"],
    )
    
    # Capture token usage
    step_tokens = {}
    log_entries = get_token_log()
    if log_entries:
        latest = log_entries[-1]
        step_tokens = {
            "step": f"Eval {iteration}",
            "node": "EVALUATE",
            "prompt_tokens": latest.get("prompt_tokens", 0),
            "completion_tokens": latest.get("completion_tokens", 0),
            "total_tokens": latest.get("total_tokens", 0),
        }
    
    all_step_tokens = list(state.get("_step_tokens", []))
    if step_tokens:
        all_step_tokens.append(step_tokens)
        
    # --- Inject Evaluator Gaps into Doubts so they appear in doubts.md ---
    all_doubts = list(state.get("doubts", []))
    if eval_data["top_gaps"]:
        # Create a formatted doubt entry for the evaluator's feedback
        gap_text = "\n".join(f"{i+1}. {g}" for i, g in enumerate(eval_data["top_gaps"]))
        eval_doubt = {
            "doubt_id": len(all_doubts) + 1,
            "section": "Evaluator Feedback",
            "field": f"Iteration {iteration}",
            "type": "Quality Gap",
            "severity": "high" if score < 7.0 else "medium",
            "raised_at_step": f"Eval {iteration}",
            "raised_at_node": "EVALUATE",
            "question": f"Evaluator requires improvements to reach score 9.0 (Current: {score}/10)",
            "evidence": gap_text,
            "action_taken": f"Agent requested {data_req['calls']} calls, {data_req['pdfs']} PDFs, web_search={data_req['web_search']}",
            "suggested_resolution": eval_data["improvement_prompt"],
            "resolved": False
        }
        all_doubts.append(eval_doubt)
        
    # --- Accumulate string for evaluator_result.md ---
    eval_log_entry = (
        f"## Version {iteration}\n"
        f"**Score:** {score}/10\n\n"
        f"**Assessment:** {eval_data['overall_assessment']}\n\n"
    )
    if section_summary:
        eval_log_entry += f"### Section Scores\n{section_summary}\n\n"
    if gaps_summary:
        eval_log_entry += f"### Top Gaps Identified\n{gaps_summary}\n\n"
    if eval_data["data_needs"]:
        eval_log_entry += f"**Reasoning for Next Action:** {eval_data['data_needs']}\n\n"
    
    eval_log_entry += f"**Data Requested for Next Version:** {data_req['calls']} calls, {data_req['pdfs']} PDFs, web_search={data_req['web_search']}\n\n"
    eval_log_entry += "---\n"
    
    all_eval_logs = list(state.get("evaluator_results_log", []))
    all_eval_logs.append(eval_log_entry)
    
    return {
        "updated_wiki":        updated_wiki_to_return,
        "existing_wiki":       existing_wiki_to_return,
        "eval_score":          score,
        "eval_feedback":       eval_data["improvement_prompt"],
        "eval_iteration":      iteration,
        "eval_section_scores": eval_data["section_scores"],
        "eval_top_gaps":       eval_data["top_gaps"],
        "eval_data_needs":     eval_data["data_needs"],
        "eval_data_request":   data_req,
        "evaluator_results_log": all_eval_logs,
        "doubts":              all_doubts,
        "logs":                _log(state, "📊 EVALUATE", log_msg),
        "_step_tokens":        all_step_tokens,
        "status":              f"evaluated_iter_{iteration}_score_{score}",
    }


# ─────────────────────────────────────────────────────────────────────────────
# 9. SAVE NODE
# ─────────────────────────────────────────────────────────────────────────────

def _apply_clickable_citations(content: str, url_map: dict) -> str:
    """Post-process wiki text to turn [call 1.json] into [[call 1.json]](url).
    
    Matches citation patterns like [call 1.json], [pdf 3.json], etc.
    and converts them to clickable markdown links if a source_url exists.
    """
    if not url_map:
        return content
    
    def _replace_citation(match):
        full_match = match.group(0)       # e.g. [call 1.json]
        label = match.group(1).strip()    # e.g. call 1.json
        
        url = url_map.get(label, "")
        if url:
            return f"[[{label}]]({url})"
        return full_match  # No URL found, leave as-is
    
    # Match [call X.json], [pdf Y - name.json], etc. but NOT already-linked [[...]](...) 
    # and NOT markdown links [text](url)
    # Pattern: standalone [label] where label contains "call" or "pdf" and ends with ".json"
    pattern = r'(?<!\[)\[([^\[\]]*?\.json)\](?!\()'
    
    result = re.sub(pattern, _replace_citation, content)
    return result


def save_node(state: WikiState) -> dict:
    """Persist wiki, logs, references, doubts, and update manifest."""
    item_name = state["item_name"]
    mcat_id   = str(state.get("mcat_id", ""))
    category  = state.get("category", "")

    # 1. Apply clickable citations, then save the wiki article
    content = state.get("updated_wiki") or state.get("existing_wiki", "")
    url_map = state.get("source_url_map", {})
    content = _apply_clickable_citations(content, url_map)
    wiki_path = save_wiki(item_name, content)

    # 2. Save execution logs
    all_src = state.get("all_sources", state.get("raw_sources", []))
    new_src = state.get("new_sources", [])
    removed = state.get("removed_sources", [])

    logs_path = save_logs(
        item_name=item_name,
        logs=state.get("logs", []),
        mcat_id=mcat_id,
        category=category,
        sources=all_src,
        new_count=len(new_src),
        removed_sources=removed,
    )

    # 3. Save references
    refs_path = save_references(
        item_name=item_name,
        references=state.get("references", []),
        mcat_id=mcat_id,
        category=category,
    )

    # 4. Save doubts
    all_doubts = state.get("doubts", [])
    doubts_path = save_doubts(
        item_name=item_name,
        doubts=all_doubts,
        mcat_id=mcat_id,
        category=category,
    )
    unresolved_count = sum(1 for d in all_doubts if not d.get("resolved"))

    # 5. Save evaluator results
    eval_log_path = save_evaluator_results(
        item_name=item_name,
        results_log=state.get("evaluator_results_log", [])
    )

    # 6. Save token usage
    step_tokens_list = state.get("_step_tokens", [])
    total_usage = get_total_usage()
    total_usage["model"] = MODEL
    tokens_path = save_token_usage(
        item_name=item_name,
        step_usage=step_tokens_list,
        total_usage=total_usage,
        mcat_id=mcat_id,
        category=category,
        confidence=state.get("_confidence"),
    )

    # 7. Save manifest
    manifest = state.get("_manifest")
    if manifest and mcat_id:
        save_run_manifest(mcat_id, manifest)

    log_msg = (
        f"- Wiki saved: `{wiki_path.name}` ({len(content)} chars)\n"
        f"- Logs saved: `{logs_path.name}`\n"
        f"- References saved: `{refs_path.name}`\n"
        f"- Doubts saved: `{doubts_path.name}` ({len(all_doubts)} total, {unresolved_count} unresolved)\n"
        f"- Evaluator results: `{eval_log_path.name}`\n"
        f"- Token usage saved: `{tokens_path.name}` ({total_usage['total_tokens']:,} total tokens)\n"
        f"- Manifest updated for mcat_id=`{mcat_id}`"
    )

    logger.info("💾  SAVE   │ wiki=%s  logs=%s  refs=%s  doubts=%s  eval=%s  tokens=%s",
                wiki_path.name, logs_path.name, refs_path.name,
                doubts_path.name, eval_log_path.name, tokens_path.name)
    
    if unresolved_count > 0:
        logger.warning("⚠️  SAVE   │ %d UNRESOLVED DOUBTS — review %s",
                       unresolved_count, doubts_path.name)

    logger.info("💰  COST   │ total_tokens=%s  input=%s  output=%s  calls=%d",
                f"{total_usage['total_tokens']:,}",
                f"{total_usage['prompt_tokens']:,}",
                f"{total_usage['completion_tokens']:,}",
                total_usage['calls'])

    return {
        "logs":   _log(state, "💾 SAVE", log_msg),
        "status": f"saved:{wiki_path.name}",
    }


# ─────────────────────────────────────────────────────────────────────────────
# 9. INDEX NODE
# ─────────────────────────────────────────────────────────────────────────────

def index_node(state: WikiState) -> dict:
    """Rebuild the category-specific index file."""
    item_name = state["item_name"]
    rebuild_index(item_name)
    path = get_index_path(item_name)

    log_msg = (
        f"- Action: Generated category-specific index\n"
        f"- Path: `wiki/index/{path.name}`\n"
        f"- Includes links to Wiki, Logs, References, and Doubts"
    )

    logger.info("📇  INDEX  │ %s rebuilt", path.name)
    return {
        "logs":   _log(state, "📇 INDEX", log_msg),
        "status": "complete",
    }