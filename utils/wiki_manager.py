"""
wiki_manager.py — Wiki-file, index, logs, and references management.

Centralises ALL wiki output logic:
  • sanitising item names into safe filenames
  • checking whether a wiki already exists
  • reading / writing wiki pages
  • building a DETAILED index.md (catalog with summaries & metadata)
  • building logs_<cat>.md   (agent execution logs — mini Langfuse)
  • building references_<cat>.md (all source references)
"""
import logging
from pathlib import Path
from datetime import datetime, timezone

from config import OUTPUT_DIR

logger = logging.getLogger(__name__)


# ─── Filename helpers ────────────────────────────────────────────────────────

def sanitize_filename(item_name: str) -> str:
    """Convert an item name to a filesystem-safe slug.

    Example: "AAC Block"  →  "aac_block"
    """
    safe = (
        item_name
        .lower()
        .strip()
        .replace(" ", "_")
        .replace("/", "_")
        .replace("\\", "_")
    )
    safe = "".join(c for c in safe if c.isalnum() or c == "_")
    return safe

def get_mcat_output_dir(item_name: str) -> Path:
    """Return the output_<mcat_name> folder path."""
    dir_path = OUTPUT_DIR / f"output_{sanitize_filename(item_name)}"
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path

def get_wiki_path(item_name: str) -> Path:
    """Return the absolute path to the wiki file for *item_name*."""
    return get_mcat_output_dir(item_name) / f"{sanitize_filename(item_name)}.md"

def get_logs_path(item_name: str) -> Path:
    """Return path: output_mcatname/logs.md"""
    return get_mcat_output_dir(item_name) / "logs.md"

def get_references_path(item_name: str) -> Path:
    """Return path: output_mcatname/references.md"""
    return get_mcat_output_dir(item_name) / "references.md"

def get_doubts_path(item_name: str) -> Path:
    """Return path: output_mcatname/doubts.md"""
    return get_mcat_output_dir(item_name) / "doubts.md"

def get_evaluator_result_path(item_name: str) -> Path:
    """Return path: output_mcatname/evaluator_result.md"""
    return get_mcat_output_dir(item_name) / "evaluator_result.md"

def save_evaluator_results(item_name: str, results_log: list) -> Path:
    """Save the accumulated evaluator results over iterations."""
    path = get_evaluator_result_path(item_name)
    content = "# Evaluator Run Results\n\n"
    if not results_log:
        content += "No evaluation feedback logged."
    else:
        content += "\n\n".join(results_log)
    
    path.write_text(content, encoding="utf-8")
    return path
def get_index_path(item_name: str) -> Path:
    """Return path: output_mcatname/index.md"""
    return get_mcat_output_dir(item_name) / "index.md"





# ─── Wiki CRUD ───────────────────────────────────────────────────────────────

def wiki_exists(item_name: str) -> bool:
    """Check whether a wiki page already exists for *item_name*."""
    return get_wiki_path(item_name).exists()


def read_existing_wiki(item_name: str) -> str:
    """Return the contents of an existing wiki, or '' if none."""
    path = get_wiki_path(item_name)
    if path.exists():
        return path.read_text(encoding="utf-8-sig")
    return ""


def save_wiki(item_name: str, content: str) -> Path:
    """Write *content* to the wiki file for *item_name*."""
    path = get_wiki_path(item_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    logger.info("Saved wiki → %s (%d chars)", path.name, len(content))
    return path


# ─── Logs management ────────────────────────────────────────────────────────

def save_logs(item_name: str, logs: list, mcat_id: str,
              category: str, sources: list, new_count: int,
              removed_sources: list) -> Path:
    """Build and write a detailed logs_<cat>.md file.

    This is a mini-Langfuse: records every step the agent took,
    what sources it read, what inferences it made, timing, and decisions.
    """
    now = datetime.now(timezone.utc)
    slug = sanitize_filename(item_name)
    path = get_logs_path(item_name)

    lines = [
        f"> **🚀 Run:** {now:%Y-%m-%d %H:%M:%S UTC}",
        "",
        f"> **MCAT ID:** {mcat_id}",
        f"> **Category:** {category}",
        f"> **Total sources scanned:** {len(sources)}",
        f"> **New/changed sources processed:** {new_count}",
        f"> **Sources removed since last run:** {len(removed_sources)}",
        "",
        "---",
        "",
        "## 📊 Run Summary",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| MCAT ID | `{mcat_id}` |",
        f"| Item Name | {item_name} |",
        f"| Category | {category} |",
        f"| Total Sources | {len(sources)} |",
        f"| New/Changed Sources | {new_count} |",
        f"| Removed Sources | {len(removed_sources)} |",
        f"| Wiki Output | `items/{slug}.md` |",
        f"| Timestamp | {now:%Y-%m-%d %H:%M:%S UTC} |",
        "",
        "---",
        "",
        "## 📂 Sources Inventory",
        "",
        "| # | Source File | Type | Status |",
        "|---|-----------|------|--------|",
    ]

    for i, src in enumerate(sources, 1):
        label = src.get("label", "unknown")
        stype = src.get("type", "unknown")
        # Determine if this was new or already processed
        status = "🆕 New" if any(
            ns.get("label") == label
            for ns in ([] if not isinstance(sources, list) else sources)
            if ns.get("hash") != src.get("_prev_hash")
        ) else "✅ Processed"
        lines.append(f"| {i} | `{label}` | {stype} | {status} |")

    if removed_sources:
        lines.append("")
        lines.append("## 🗑️ Removed Sources")
        lines.append("")
        for fname in removed_sources:
            lines.append(f"- ~~`{fname}`~~ — removed from input folder")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 🔄 Step-by-Step Execution Log")
    lines.append("")

    for i, entry in enumerate(logs, 1):
        import re
        first_line = entry.split("\n")[0]
        # Example first_line: "**[12:30:15] 🔄 UPDATE**"
        title = first_line.replace("**", "").split("] ", 1)[-1] if "] " in first_line else "Action"
        
        source_match = re.search(r"- Source: `(.*?)`", entry)
        detail = f" — {source_match.group(1)}" if source_match else ""
        
        lines.append(f"### Step {i}: {title}{detail}")
        lines.append("")
        lines.append(entry)
        lines.append("")

    lines.append("---")
    lines.append("")

    if path.exists():
        existing = path.read_text(encoding="utf-8-sig")
        new_content = existing.strip() + "\n\n<br>\n\n" + "\n".join(lines) + "\n"
        path.write_text(new_content, encoding="utf-8")
    else:
        header = f"# 📋 Agent Execution Log — {item_name}\n\n"
        path.write_text(header + "\n".join(lines) + "\n", encoding="utf-8")

    logger.info("Saved logs → %s", path.name)
    return path


# ─── References management ──────────────────────────────────────────────────

def save_references(item_name: str, references: list,
                    mcat_id: str, category: str) -> Path:
    """Build and write a detailed references_<cat>.md file.

    Each reference records the source file, what type it was,
    and what key information was extracted from it.
    """
    now = datetime.now(timezone.utc)
    path = get_references_path(item_name)

    lines = [
        f"> **🚀 Run:** {now:%Y-%m-%d %H:%M:%S UTC}",
        "",
        f"> **MCAT ID:** {mcat_id}",
        f"> **Category:** {category}",
        f"> **Total New References:** {len(references)}",
        "",
        "---",
        "",
    ]

    # Group references by type
    by_type: dict[str, list] = {}
    for ref in references:
        rtype = ref.get("type", "unknown")
        by_type.setdefault(rtype, []).append(ref)

    for rtype, refs in by_type.items():
        type_label = {
            "json": "📄 JSON Data Sources",
            "text": "📝 Text Sources",
            "url_list": "🔗 URL Sources",
            "csv": "📊 CSV Data Sources",
            "unknown": "❓ Other Sources",
        }.get(rtype, f"📎 {rtype.title()} Sources")

        lines.append(f"## {type_label}")
        lines.append("")

        for i, ref in enumerate(refs, 1):
            lines.append(f"### {i}. `{ref.get('label', 'Unknown')}`")
            lines.append("")
            lines.append(f"- **File:** `{ref.get('label', 'N/A')}`")
            lines.append(f"- **Type:** {ref.get('type', 'N/A')}")
            lines.append(f"- **Path:** `{ref.get('path', 'N/A')}`")

            if ref.get("key_extractions"):
                lines.append(f"- **Key Extractions:** {ref['key_extractions']}")

            if ref.get("data_points"):
                lines.append(f"- **Data Points Contributed:** {ref['data_points']}")

            if ref.get("inferred"):
                lines.append(f"- **Agent Reasoning (Inferred):** {ref['inferred']}")
                
            if ref.get("updates"):
                lines.append(f"- **Wiki Updates Made:** {ref['updates']}")

            # Show ALL web search result URLs — no trimming
            if ref.get("web_results"):
                lines.append("- **Web Search Results:**")
                for wr in ref["web_results"]:
                    title = wr.get("title", "Untitled")
                    url = wr.get("url", "")
                    if url:
                        lines.append(f"  - [{title}]({url})")
                    else:
                        lines.append(f"  - {title}")

            lines.append("")

        lines.append("---")
        lines.append("")

    if path.exists():
        existing = path.read_text(encoding="utf-8-sig")
        new_content = existing.strip() + "\n\n<br>\n\n" + "\n".join(lines) + "\n"
        path.write_text(new_content, encoding="utf-8")
    else:
        header = f"# 📖 References — {item_name}\n\n"
        path.write_text(header + "\n".join(lines) + "\n", encoding="utf-8")

    logger.info("Saved references → %s", path.name)
    return path


# ─── Doubts management ──────────────────────────────────────────────────────

def save_doubts(item_name: str, doubts: list, mcat_id: str,
                category: str) -> Path:
    """Build and write a detailed doubts file for human review.

    Each doubt records what confused the agent, what evidence it had,
    what action it took, and whether it was later resolved.
    """
    now = datetime.now(timezone.utc)
    path = get_doubts_path(item_name)

    # Separate resolved vs unresolved
    unresolved = [d for d in doubts if not d.get("resolved")]
    resolved   = [d for d in doubts if d.get("resolved")]

    lines = [
        f"> **🚀 Run:** {now:%Y-%m-%d %H:%M:%S UTC}",
        "",
        f"> **MCAT ID:** {mcat_id}",
        f"> **Category:** {category}",
        f"> **Total Doubts Raised This Run:** {len(doubts)}",
        f"> **Unresolved:** {len(unresolved)} 🔴",
        f"> **Self-Resolved:** {len(resolved)} ✅",
        "",
        "---",
        "",
    ]

    if not doubts:
        lines.append("_No doubts raised during this run. The agent was confident in all data._")
        lines.append("")
    else:
        # ── Unresolved first ──
        if unresolved:
            lines.append("## 🔴 Unresolved Doubts")
            lines.append("")
            for i, d in enumerate(unresolved, 1):
                sev_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(d.get("severity", ""), "⚪")
                lines.append(f"### {sev_icon} DOUBT-{d.get('doubt_id', i):03d}: {d.get('section', 'Unknown')} → {d.get('field', 'Unknown')}")
                lines.append("")
                lines.append(f"- **Type:** `{d.get('type', 'unknown')}`")
                lines.append(f"- **Severity:** {d.get('severity', 'unknown')}")
                lines.append(f"- **Raised at:** Step {d.get('raised_at_step', '?')} ({d.get('raised_at_node', '?')})")
                lines.append(f"- **Question:** {d.get('question', 'N/A')}")
                lines.append("")
                if d.get("evidence"):
                    lines.append("**Evidence:**")
                    lines.append("```")
                    lines.append(d["evidence"])
                    lines.append("```")
                    lines.append("")
                if d.get("action_taken"):
                    lines.append(f"**Action Taken by Agent:** {d['action_taken']}")
                    lines.append("")
                if d.get("suggested_resolution"):
                    lines.append(f"**Suggested Resolution:** {d['suggested_resolution']}")
                    lines.append("")
                lines.append("---")
                lines.append("")

        # ── Resolved ──
        if resolved:
            lines.append("## ✅ Self-Resolved Doubts")
            lines.append("")
            for i, d in enumerate(resolved, 1):
                lines.append(f"### DOUBT-{d.get('doubt_id', i):03d}: {d.get('section', 'Unknown')} → {d.get('field', 'Unknown')} *(Resolved)*")
                lines.append("")
                lines.append(f"- **Originally raised at:** Step {d.get('raised_at_step', '?')}")
                lines.append(f"- **Question:** {d.get('question', 'N/A')}")
                lines.append(f"- **Resolved at:** Step {d.get('resolved_at_step', '?')} ({d.get('resolved_at_node', '?')})")
                lines.append(f"- **Resolution:** {d.get('resolution', 'N/A')}")
                lines.append("")
                lines.append("---")
                lines.append("")

    if path.exists():
        existing = path.read_text(encoding="utf-8-sig")
        new_content = existing.strip() + "\n\n<br>\n\n" + "\n".join(lines) + "\n"
        path.write_text(new_content, encoding="utf-8")
    else:
        header = f"# 🤔 Agent Doubt Log — {item_name}\n\n"
        path.write_text(header + "\n".join(lines) + "\n", encoding="utf-8")

    logger.info("Saved doubts → %s (%d total, %d unresolved)",
                path.name, len(doubts), len(unresolved))
    return path


# ─── Token usage management ──────────────────────────────────────────────────

def save_token_usage(item_name: str, step_usage: list, total_usage: dict,
                     mcat_id: str, category: str,
                     confidence: list = None) -> Path:
    """Build and write a detailed token usage report for cost analysis."""
    now = datetime.now(timezone.utc)
    path = get_mcat_output_dir(item_name) / "tokens.md"

    lines = [
        f"> **🚀 Run:** {now:%Y-%m-%d %H:%M:%S UTC}",
        "",
        f"> **MCAT ID:** {mcat_id}",
        f"> **Category:** {category}",
        f"> **Model:** {total_usage.get('model', 'N/A')}",
        f"> **Total LLM Calls:** {total_usage.get('calls', 0)}",
        "",
        "---",
        "",
        "## 📊 Summary",
        "",
        "| Metric | Value |",
        "|--------|------|",
        f"| **Total Input Tokens** | {total_usage.get('prompt_tokens', 0):,} |",
        f"| **Total Output Tokens** | {total_usage.get('completion_tokens', 0):,} |",
        f"| **Total Tokens** | {total_usage.get('total_tokens', 0):,} |",
        f"| **Total LLM Calls** | {total_usage.get('calls', 0)} |",
        "",
        "---",
        "",
        "## 🔄 Step-by-Step Token Breakdown",
        "",
        "| Step | Node | Input Tokens | Output Tokens | Total Tokens |",
        "|------|------|-------------|--------------|-------------|",
    ]

    for entry in step_usage:
        lines.append(
            f"| {entry.get('step', '?')} | {entry.get('node', '?')} | "
            f"{entry.get('prompt_tokens', 0):,} | "
            f"{entry.get('completion_tokens', 0):,} | "
            f"{entry.get('total_tokens', 0):,} |"
        )

    # Section confidence scores
    if confidence:
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("## 📊 Section Confidence Scores")
        lines.append("")
        lines.append("| Section | Confidence | Reason |")
        lines.append("|---------|-----------|--------|")
        for c in confidence:
            level = c.get("level", "?")
            icon = {"high": "🟢", "medium": "🟡", "low": "🔴"}.get(level, "⚪")
            lines.append(
                f"| {c.get('section', '?')} | {icon} {level.upper()} | "
                f"{c.get('reason', '')} |"
            )

    lines.append("")
    lines.append("---")
    lines.append("")

    if path.exists():
        existing = path.read_text(encoding="utf-8-sig")
        new_content = existing.strip() + "\n\n<br>\n\n" + "\n".join(lines) + "\n"
        path.write_text(new_content, encoding="utf-8")
    else:
        header = f"# 💰 Token Usage Report — {item_name}\n\n"
        path.write_text(header + "\n".join(lines) + "\n", encoding="utf-8")

    logger.info("Saved token usage → %s (%d total tokens)",
                path.name, total_usage.get('total_tokens', 0))
    return path


# ─── Detailed index management ──────────────────────────────────────────────

def rebuild_index(item_name: str) -> None:
    """Regenerate a category-specific index file in ``output_mcatname/index.md``.

    This is a proper product-specific dashboard containing:
    - Summary of the category
    - Links to Wiki, Logs, References, and Doubts
    - Detailed document structure (Headings, Tables, etc.)
    """
    now = datetime.now(timezone.utc)
    wiki_path = get_wiki_path(item_name)
    
    if not wiki_path.exists():
        logger.warning("Cannot build index for %s: Wiki file not found.", item_name)
        return

    display = item_name.title()
    path = get_index_path(item_name)

    # Extract first meaningful paragraph as summary
    content = wiki_path.read_text(encoding="utf-8-sig")
    summary = _extract_summary(content)

    lines = [
        f"# 📑 Category Index — {display}",
        "",
        f"> Generated on {now:%Y-%m-%d %H:%M:%S UTC}",
        "",
        "This is the central dashboard for this category, linking to the full wiki article, "
        "execution logs, and source references.",
        "",
        "---",
        "",
        "## 📝 Category Overview",
        "",
        f"> {summary}",
        "",
        "## 🔗 Traceability & Files",
        "",
        f"- **📚 Wiki Page:** [{wiki_path.name}]({wiki_path.name})",
    ]

    # Check for companion files
    log_p = get_logs_path(item_name)
    ref_p = get_references_path(item_name)
    doubt_p = get_doubts_path(item_name)
    
    logs_exists = log_p.exists()
    refs_exists = ref_p.exists()
    doubts_exists = doubt_p.exists()

    if logs_exists:
        lines.append("- **📋 Execution Logs:** [logs.md](logs.md)")
    if refs_exists:
        lines.append("- **📖 Source References:** [references.md](references.md)")
    if doubts_exists:
        lines.append("- **🤔 Agent Doubts:** [doubts.md](doubts.md)")

    lines.append("")
    lines.append("---")
    lines.append("")

    # Detailed entries section
    def extract_document_structure(p: Path) -> list:
        import re
        if not p.exists(): return []
        lines = p.read_text(encoding="utf-8-sig").splitlines()
        
        nodes = []
        heading_level_base = 0
        in_table = False
        skip_table = False
        in_code_block = False
        
        for ln in lines:
            s = ln.strip()
            if s.startswith("```"):
                in_code_block = not in_code_block
                continue
            if in_code_block: continue
            if not s: continue
            
            leading_spaces = len(ln) - len(ln.lstrip())
            list_depth = leading_spaces // 4
            
            if s.startswith("## ") and len(s) > 3:
                nodes.append({"type": "H", "text": s[3:].strip(), "level": 1})
                heading_level_base = 1
                in_table = False
            elif s.startswith("### ") and len(s) > 4:
                nodes.append({"type": "H", "text": s[4:].strip(), "level": 2})
                heading_level_base = 2
                in_table = False
            elif s.startswith("#### ") and len(s) > 5:
                nodes.append({"type": "H", "text": s[5:].strip(), "level": 3})
                heading_level_base = 3
                in_table = False
            elif s.startswith("> ⚠️") or s.startswith("> **"):
                m = re.search(r'\*\*(.*?)\*\*', s)
                if m:
                    label = m.group(1).replace(":", "").strip()
                    nodes.append({"type": "quote", "text": label, "level": heading_level_base + 1})
                in_table = False
            elif s.startswith("* ") or s.startswith("- ") or re.match(r'\d+\.\s', s):
                m = re.match(r'^(?:\* |- |\d+\.\s)\s*\*\*(.*?)\*\*', s)
                if m:
                    label = m.group(1).replace(":", "").strip()
                    if label.lower() not in ["file", "type", "path", "key extractions", "data points contributed"]:
                        nodes.append({"type": "bullet", "text": label, "level": heading_level_base + 1 + list_depth})
                in_table = False
            elif s.startswith("|") and not s.endswith("="):
                if "---" in s or ":--" in s:
                    in_table = True
                    continue
                parts = s.split("|")
                if len(parts) > 2:
                    c1 = parts[1].strip()
                    if not in_table:
                        if c1.lower().replace("*", "") in ["source", "file", "reference", "link", "#", "metric"]:
                            skip_table = True
                        else:
                            skip_table = False
                    elif in_table and not skip_table:
                        label = c1.replace("**", "").replace("*", "").strip()
                        if label: nodes.append({"type": "table", "text": label, "level": heading_level_base + 1})
            else:
                in_table = False
                skip_table = False

        for i in range(len(nodes)):
            nodes[i]["has_children"] = False
            if i + 1 < len(nodes):
                if nodes[i+1]["level"] > nodes[i]["level"]:
                    nodes[i]["has_children"] = True

        tree = []
        for n in nodes:
            indent = "  " * (n["level"] - 1)
            if n["type"] == "H" or n["has_children"]:
                tree.append(f"{indent}- **{n['text']}**")
            else:
                icon = {"quote": "🔸", "link": "🔗"}.get(n["type"], "🔹")
                tree.append(f"{indent}- {icon} {n['text']}")
        return tree

    wiki_sections = extract_document_structure(wiki_path)
    
    logs_sections = extract_document_structure(log_p)
    refs_sections = extract_document_structure(ref_p)
    doubts_sections = extract_document_structure(doubt_p)

    if wiki_sections:
        lines.append("## 🗺️ Wiki Structure")
        lines.append("")
        for s in wiki_sections:
            lines.append(f"- {s}")
        lines.append("")

    if logs_sections:
        lines.append("## 📋 Log Sections")
        lines.append("")
        for s in logs_sections:
            lines.append(f"- {s}")
        lines.append("")

    if refs_sections:
        lines.append("## 📖 Reference Sections")
        lines.append("")
        for s in refs_sections:
            lines.append(f"- {s}")
        lines.append("")

    if doubts_sections:
        lines.append("## 🤔 Agent Doubt Log")
        lines.append("")
        for s in doubts_sections:
            lines.append(f"- {s}")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(f"*Index generated at {now:%Y-%m-%d %H:%M:%S UTC}*")
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Saved category index → %s", path.name)


def _extract_summary(content: str, max_len: int = 200) -> str:
    """Extract a one-line summary from wiki content.

    Looks for the first non-heading, non-empty paragraph after the title.
    """
    for line in content.splitlines():
        stripped = line.strip()
        # Skip headings, empty lines, tables, metadata markers
        if (not stripped
                or stripped.startswith("#")
                or stripped.startswith("|")
                or stripped.startswith(">")
                or stripped.startswith("---")
                or stripped.startswith("```")
                or stripped.startswith("*")):
            continue
        # Found a content line — use it as summary
        if len(stripped) > max_len:
            return stripped[:max_len].rsplit(" ", 1)[0] + "…"
        return stripped

    return "No summary available."
