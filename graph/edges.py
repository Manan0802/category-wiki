"""
edges.py — LangGraph wiring for the Category Wiki pipeline (Agentic Loop).

Flow:
  START → input_node → category_node → check_wiki_node
        → (wiki_exists?) → create_node : update_node
        → evaluate_node
              → score >= 9.0 → enrich_node → save_node → index_node → END
              → score < 9.0 + more sources → load_next_source → update_node → evaluate_node (LOOP)
              → score < 9.0 + no sources → enrich_node → save_node → index_node → END

The agentic evaluation loop ensures the wiki is iteratively improved
until it meets the quality threshold (9/10) or all sources are exhausted.
"""
import logging

from langgraph.graph import StateGraph, END

from graph.state import WikiState
from graph.nodes import (
    pick_sources_node,
    category_node,
    check_wiki_node,
    create_node,
    update_node,
    evaluate_node,
    enrich_node,
    save_node,
    index_node,
)

logger = logging.getLogger(__name__)

# ─── Conditional edge functions ──────────────────────────────────────────────

def route_after_check(state: WikiState) -> str:
    """First source: CREATE if no wiki exists, UPDATE if there are new sources, or SKIP if 0 new sources."""
    if state.get("wiki_exists", False):
        if len(state.get("raw_sources", [])) == 0:
            logger.info("⤵️  ROUTE  │ wiki exists & no new info → save_node")
            return "save_node"
            
        logger.info("⤵️  ROUTE  │ wiki exists → update_node")
        return "update_node"
        
    logger.info("⤵️  ROUTE  │ wiki missing → create_node")
    return "create_node"


def route_after_evaluate(state: WikiState) -> str:
    """After evaluation, decide: done → enrich, or loop back to pick sources."""
    data_req = state.get("eval_data_request", {})
    is_done = data_req.get("done", False)

    if is_done:
        logger.info("⤵️  ROUTE  │ data_request=done → enrich_node")
        return "enrich_node"

    logger.info(f"⤵️  ROUTE  │ req=(calls:{data_req.get('calls')}, pdfs:{data_req.get('pdfs')}, web:{data_req.get('web_search')}) → pick_sources_node")
    return "pick_sources_node"


# ─── Graph builder ───────────────────────────────────────────────────────────

def build_graph() -> StateGraph:
    """Construct and compile the full LangGraph pipeline with agentic evaluation loop."""
    workflow = StateGraph(WikiState)

    # ── Register nodes ───────────────────────────────────────────────────
    workflow.add_node("pick_sources_node",     pick_sources_node)
    workflow.add_node("category_node",         category_node)
    workflow.add_node("check_wiki_node",       check_wiki_node)
    workflow.add_node("create_node",           create_node)
    workflow.add_node("update_node",           update_node)
    workflow.add_node("evaluate_node",         evaluate_node)
    workflow.add_node("enrich_node",           enrich_node)
    workflow.add_node("save_node",             save_node)
    workflow.add_node("index_node",            index_node)

    # ── Entry & linear flow ──────────────────────────────────────────────
    workflow.set_entry_point("pick_sources_node")
    workflow.add_edge("pick_sources_node", "category_node")
    workflow.add_edge("category_node",     "check_wiki_node")

    # ── Branch: first source → create, update, or skip ──────────────────────
    workflow.add_conditional_edges(
        "check_wiki_node",
        route_after_check,
        {
            "create_node": "create_node",
            "update_node": "update_node",
            "save_node": "save_node"
        },
    )

    # ── After create/update → always evaluate ───────────────────────────
    workflow.add_edge("create_node", "evaluate_node")
    workflow.add_edge("update_node", "evaluate_node")

    # ── After evaluate: decide → enrich (done) or pick_sources (loop) ───
    workflow.add_conditional_edges(
        "evaluate_node",
        route_after_evaluate,
        {
            "enrich_node":       "enrich_node",
            "pick_sources_node": "pick_sources_node",
        },
    )

    # ── Post-enrichment linear flow ───────────────────────────────────────
    workflow.add_edge("enrich_node", "save_node")
    workflow.add_edge("save_node",   "index_node")
    workflow.add_edge("index_node",  END)

    return workflow.compile()