"""
preprocessor.py — Raw source loader + change-tracking for the Category Wiki Agent.

Scans an mcat folder (data/inputs/input_<mcat_id>/) and:
  1. Loads all source files (JSON, TXT, CSV, MD, HTML, etc.)
  2. Compares against a .manifest.json to detect NEW and REMOVED sources
  3. Returns structured source dicts ready for LLM ingestion

The manifest is a JSON file stored alongside the input files that records
which files have been processed in previous runs.  This enables:
  - Only processing NEW sources (skip already-processed ones)
  - Detecting REMOVED sources so their info can be cleaned from the wiki
"""
import json
import hashlib
import logging
import re
from pathlib import Path
from datetime import datetime, timezone

from config import RAW_DIR

logger = logging.getLogger(__name__)

# Regex to detect bare URLs inside text files
_URL_RE = re.compile(r"https?://[^\s\"'<>]+")

# Extensions we try to read as text
_TEXT_EXTENSIONS = {".txt", ".md", ".csv", ".html", ".htm", ""}


# ─── File content hash ──────────────────────────────────────────────────────

def _file_hash(path: Path) -> str:
    """Return SHA-256 hex digest of a file's contents."""
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


# ─── Individual file parsers ─────────────────────────────────────────────────

def _format_json(data, label: str) -> str:
    """Recursively flatten a JSON object into readable key: value lines."""
    lines = [f"=== Source: {label} (JSON) ==="]

    def _walk(obj, prefix=""):
        if isinstance(obj, dict):
            for k, v in obj.items():
                _walk(v, f"{prefix}{k}.")
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                _walk(v, f"{prefix}[{i}].")
        else:
            if obj not in (None, "", [], {}):
                lines.append(f"{prefix.rstrip('.')}: {obj}")

    _walk(data)
    return "\n".join(lines)


def _format_text(text: str, label: str) -> str:
    """Return plain text with a source header."""
    return f"=== Source: {label} (Text) ===\n{text.strip()}"


def _format_url_list(urls: list[str], label: str) -> str:
    """Format a list of URLs as a source block."""
    body = "\n".join(f"  - {u}" for u in urls)
    return f"=== Source: {label} (URLs) ===\n{body}"


# ─── Single-file loader ──────────────────────────────────────────────────────

def load_source_file(file_path: Path) -> dict:
    """Load one file and return a source dict.

    Returns empty dict for empty / unreadable files.
    """
    label = file_path.name
    suffix = file_path.suffix.lower()
    raw = file_path.read_text(encoding="utf-8-sig", errors="replace").strip()

    if not raw:
        # User requested to process even purely empty files
        raw = ""

    # Determine descriptive category for LLM citations
    if "call" in label.lower():
        cat = "buyer call data"
    elif "pdf" in label.lower() or "catalog" in label.lower():
        cat = "manufacturer catalog"
    elif "quotation" in label.lower() or "quote" in label.lower():
        cat = "quotation data"
    elif "price" in label.lower():
        cat = "market price list"
    elif "standard" in label.lower() or "is_" in label.lower():
        cat = "regulatory standard"
    else:
        cat = "reference document"

    # ── JSON ──────────────────────────────────────────────────────────────
    if suffix == ".json":
        try:
            data = json.loads(raw)
            return {
                "path":    str(file_path),
                "type":    "json",
                "label":   label,
                "category": cat,
                "hash":    _file_hash(file_path),
                "content": _format_json(data, label),
            }
        except json.JSONDecodeError:
            logger.warning("%s is not valid JSON — treating as text", label)

    # ── Text / Markdown / CSV / HTML ──────────────────────────────────────
    if suffix in _TEXT_EXTENSIONS:
        urls = _URL_RE.findall(raw)
        if urls and len(urls) / max(len(raw.splitlines()), 1) > 0.5:
            return {
                "path":    str(file_path),
                "type":    "url_list",
                "label":   label,
                "category": cat,
                "hash":    _file_hash(file_path),
                "content": _format_url_list(urls, label),
            }
        return {
            "path":    str(file_path),
            "type":    "text",
            "label":   label,
            "category": cat,
            "hash":    _file_hash(file_path),
            "content": _format_text(raw, label),
        }

    # ── Unknown extension — try reading as text ───────────────────────────
    return {
        "path":    str(file_path),
        "type":    "unknown",
        "label":   label,
        "category": cat,
        "hash":    _file_hash(file_path),
        "content": _format_text(raw, label),
    }


# ─── Manifest management ────────────────────────────────────────────────────

def _manifest_path(mcat_id: str) -> Path:
    """Path to the change-tracking manifest for a given mcat."""
    return RAW_DIR / f"input_{mcat_id}" / ".manifest.json"


def _load_manifest(mcat_id: str) -> dict:
    """Load existing manifest, or return empty structure."""
    mp = _manifest_path(mcat_id)
    if mp.exists():
        return json.loads(mp.read_text(encoding="utf-8-sig"))
    return {"processed_files": {}, "last_run": None}


def _save_manifest(mcat_id: str, manifest: dict) -> None:
    """Persist the manifest after a successful run."""
    mp = _manifest_path(mcat_id)
    mp.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Manifest saved: %s", mp)


# ─── Folder scanner (priority ordering) ──────────────────────────────────────

_PRIORITY = {".json": 0, ".csv": 1, ".md": 2, ".txt": 3, ".html": 4, "": 5}


def _sort_key(p: Path) -> tuple:
    return (_PRIORITY.get(p.suffix.lower(), 9), p.name.lower())


# ─── Main public API ────────────────────────────────────────────────────────

def load_sources_with_tracking(mcat_id: str) -> dict:
    """Scan input folder, compare with manifest, return tracking info.

    Returns
    -------
    dict with keys:
        all_sources:     list[dict]  — every source file loaded
        new_sources:     list[dict]  — only NEW (not yet processed) sources
        removed_sources: list[str]   — filenames that were removed since last run
        manifest:        dict        — updated manifest (call save after success)
    """
    folder = RAW_DIR / f"input_{mcat_id}"

    if not folder.exists():
        raise FileNotFoundError(
            f"Input folder not found: {folder}\n"
            f"Expected: data/inputs/input_{mcat_id}/"
        )

    # Load manifest from previous run
    manifest = _load_manifest(mcat_id)
    prev_files = manifest.get("processed_files", {})

    # Scan current files
    files = sorted(
        [f for f in folder.iterdir()
         if f.is_file() and not f.name.startswith(".")],
        key=_sort_key,
    )

    if not files:
        raise ValueError(f"No source files found in: {folder}")

    # Load all sources
    all_sources = []
    current_files = {}
    for f in files:
        try:
            src = load_source_file(f)
            if src:
                all_sources.append(src)
                current_files[src["label"]] = src["hash"]
                logger.info("Loaded source: %s (%s)", src["label"], src["type"])
        except Exception as exc:
            logger.warning("Could not load %s: %s", f.name, exc)

    if not all_sources:
        raise ValueError(f"All files in {folder} were empty or unreadable.")

    # Determine NEW sources (not in previous manifest, or hash changed)
    new_sources = []
    for src in all_sources:
        old_hash = prev_files.get(src["label"])
        if old_hash is None or old_hash != src["hash"]:
            new_sources.append(src)
            logger.info("  NEW/CHANGED: %s", src["label"])

    # Determine REMOVED sources (in previous manifest but not on disk anymore)
    removed_sources = [
        fname for fname in prev_files
        if fname not in current_files
    ]
    for fname in removed_sources:
        logger.info("  REMOVED: %s", fname)

    # Build updated manifest (will be saved after successful run)
    updated_manifest = {
        "processed_files": current_files,
        "last_run": datetime.now(timezone.utc).isoformat(),
    }

    logger.info(
        "Preprocessor: %d total, %d new, %d removed from input_%s",
        len(all_sources), len(new_sources), len(removed_sources), mcat_id,
    )

    return {
        "all_sources":     all_sources,
        "new_sources":     new_sources,
        "removed_sources": removed_sources,
        "manifest":        updated_manifest,
    }


def save_run_manifest(mcat_id: str, manifest: dict) -> None:
    """Public wrapper to persist manifest after a successful pipeline run."""
    _save_manifest(mcat_id, manifest)


# ─── Legacy compat (used by input_node if needed) ───────────────────────────

def load_sources_from_folder(mcat_id: str) -> list[dict]:
    """Load all sources without tracking (backward compat)."""
    result = load_sources_with_tracking(mcat_id)
    return result["all_sources"]