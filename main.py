"""
main.py — CLI entry-point for the Category Wiki Agent.

Usage:
    python main.py --mcat-id <ID> --mcat-name "<NAME>"
    python main.py                                            # interactive mode
"""
import sys
import logging
import argparse

from config import DEBUG
from graph.edges import build_graph

# ── Logging setup ────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(name)s  │  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("wiki-agent")


# ─── Interactive fallback ─────────────────────────────────────────────────────

def _interactive_input() -> dict:
    print("\n╔══════════════════════════════════════════════════╗")
    print("║       📚  Category Wiki Agent — Interactive      ║")
    print("╚══════════════════════════════════════════════════╝\n")

    mcat_id = input("  MCAT ID       : ").strip()
    if not mcat_id:
        print("❌  MCAT ID cannot be empty.")
        sys.exit(1)

    mcat_name = input("  MCAT Name     : ").strip()
    if not mcat_name:
        print("❌  MCAT Name cannot be empty.")
        sys.exit(1)

    return {"mcat_id": mcat_id, "mcat_name": mcat_name}


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Category Wiki Agent — build Wikipedia-style wikis from raw source files.",
    )
    parser.add_argument(
        "--mcat-id", "-id",
        help="MCAT folder ID (folder will be data/inputs/input_<mcat-id>/).",
    )
    parser.add_argument(
        "--mcat-name", "-n",
        help="Human-readable MCAT name .",
    )
    parser.add_argument(
        "--reset", action="store_true",
        help="Reset existing wiki, logs, and manifest for this category before running.",
    )

    args = parser.parse_args()

    # ── Determine input ──────────────────────────────────────────────────
    if args.mcat_id and args.mcat_name:
        initial_state = {
            "mcat_id":   args.mcat_id,
            "mcat_name": args.mcat_name,
        }
    else:
        initial_state = _interactive_input()

    # ── Reset functionality ──────────────────────────────────────────────
    if args.reset:
        logger.warning("🗑️ RESET FLAG DETECTED — Clearing previous artifacts for this category...")
        from config import RAW_DIR
        from utils.wiki_manager import get_wiki_path, get_logs_path, get_references_path
        
        manifest_path = RAW_DIR / f"input_{initial_state['mcat_id']}" / ".manifest.json"
        if manifest_path.exists(): manifest_path.unlink()
        
        wp = get_wiki_path(initial_state['mcat_name'])
        lp = get_logs_path(initial_state['mcat_name'])
        rp = get_references_path(initial_state['mcat_name'])
        
        if wp.exists(): wp.unlink()
        if lp.exists(): lp.unlink()
        if rp.exists(): rp.unlink()

    # ── Pre-Process Calls ────────────────────────────────────────────────
    import os
    from process_call_csv import process_csv
    
    csv_path = "calls_data.csv"
    if os.path.exists(csv_path):
        logger.info(f"Checking for new calls in {csv_path}...")
        process_csv(csv_path, initial_state["mcat_id"])
    else:
        logger.warning(f"Could not find {csv_path}. Skipping call extraction.")

    # ── Build & invoke graph ─────────────────────────────────────────────
    logger.info("Building LangGraph pipeline…")
    graph = build_graph()

    logger.info(
        "Starting pipeline │ mcat_id=%s  mcat_name=%s",
        initial_state["mcat_id"],
        initial_state["mcat_name"],
    )

    result = graph.invoke(initial_state)

    # ── Report ───────────────────────────────────────────────────────────
    all_src  = result.get("all_sources", result.get("raw_sources", []))
    new_src  = result.get("new_sources", [])
    removed  = result.get("removed_sources", [])

    print("\n" + "═" * 58)
    print("  ✅  Pipeline complete!")
    print(f"  📦  MCAT ID      : {result.get('mcat_id')}")
    print(f"  📄  Item         : {result.get('item_name')}")
    print(f"  🏷️  Category     : {result.get('category')}")
    print(f"  📁  Total Sources: {len(all_src)} file(s)")
    print(f"  🆕  New/Changed  : {len(new_src)} file(s)")
    print(f"  🗑️  Removed      : {len(removed)} file(s)")
    print(f"  📊  Eval Score   : {result.get('eval_score', 'N/A')}/10")
    print(f"  🔄  Eval Iters   : {result.get('eval_iteration', 0)}")
    print(f"  📊  Status       : {result.get('status')}")
    print(f"  📝  Wiki         : output/")
    print(f"  📋  Logs         : output/")
    print(f"  📖  References   : output/")
    print("═" * 58 + "\n")

if __name__ == "__main__":
    main()