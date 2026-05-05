# Theory and Architecture: Autonomous Wiki Pipeline

This document explains the theoretical framework and operational logic of the **Category Wiki Generator**. It is designed as a high-fidelity synthesis system for the Indian B2B marketplace.

---

## 1. Core Objective
The system's goal is to transform "messy" real-world data (buyer calls, seller catalogs, PDF brochures, web results) into a **structured, authoritative product encyclopedia**. It doesn't just summarize; it synthesizes knowledge iteratively to build a compounding "Source of Truth."

---

## 2. Pipeline Architecture (LangGraph)
The system is built on a **directed acyclic graph (DAG)** that supports iterative loops. Unlike a linear script, the system can "think" and "loop" back to fetch more data until a quality threshold is met.

### The Macro Flow:
1. **Initialize**: Scan local input directories and load the persistent manifest.
2. **Pick Sources**: Select the next batch of data (Max 10 calls, 5 PDFs initially; then smaller batches).
3. **Build/Update**:
   - **CREATE**: If no wiki exists, build the first draft from initial sources.
   - **UPDATE**: If a wiki exists, merge new data into the existing structure using "Compounding Knowledge" logic.
4. **Evaluate**: A "Ruthless Evaluator" agent scores the wiki across 12 criteria (1-10 scale).
5. **Route**:
   - If **Score >= 9.0** OR **Max Iterations (3) reached**: End and save the final wiki.
   - If **Score < 9.0**: Identify specific gaps, request new sources, and Loop back to **Step 2**.

---

## 3. Key Operational Pillars

### A. Batched Ingestion (Efficiency & Audit)
Instead of processing all sources in one massive prompt (which causes "context loss" and high token costs), the system processes sources in **batches of 3**.
- **Audit Trail**: Every batch generates a **red/green diff** in the logs, showing exactly what content was added or changed by those specific sources.
- **Reference Tracking**: Every fact is tagged with a citation (e.g., `[call 1.json]` or `[pdf 3.json]`) to ensure 100% traceability.

### B. Persistent Manifest Tracking
The system maintains a `.run_manifest.json` for every category. 
- **Stateful Memory**: It knows exactly which files have been ingested.
- **Resilience**: If the process is interrupted, it can resume without re-ingesting the same files, saving time and money.

### C. Agentic Quality Control (Rollback & Cap)
To prevent the agent from getting "hallucination loops" or degrading quality:
- **Score Rollback**: If an iteration (V2) results in a lower score than the previous one (V1), the system **rolls back** to the better version (V1) and terminates.
- **Iteration Cap**: Strictly limited to **3 iterations**. This prevents infinite loops and ensures resource management.
- **Web Search Nudging**: If the score is below 9.0, the system forces `web_search=True` to ensure the agent looks for external regulatory or pricing data to fill the gaps.

---

## 4. The 12-Section Universal Structure
The system enforces a strict, category-agnostic structure to ensure consistency across the marketplace:
1.  **Quick Facts**: Compact summary table.
2.  **Category Overview**: Market and supply chain context.
3.  **Seller-Side Specifications**: Technical attributes used by suppliers.
4.  **Buyer Specifications**: Attributes used by buyers in RFQs/Calls.
5.  **Most Relevant Spec Combinations**: Typical product configurations/profiles.
6.  **Spec Contradictions & Flags**: Impossible combos or quality warnings.
7.  **Price-Defining Specs**: Ranking of what drives price variation.
8.  **Buyer Personas**: Profiles of who buys and why.
9.  **Seller Personas**: Profiles of who sells and their data reliability.
10. **Listing Spec Tiers**: Classification into Primary, Secondary, and Tertiary.
11. **Glossary**: Definitions of domain jargon.
12. **Wiki Metadata**: System versioning and completeness scores.

---

## 5. Technical Stack
- **Orchestration**: LangGraph (for the agentic state machine).
- **LLM**: Gemini 2.5/3.1 Pro (via Intermesh Gateway).
- **Tools**: 
  - `web_search`: Live search via Parallel AI API.
  - `pdf_pipeline`: Custom LLM-based extraction for complex technical catalogs.
- **Storage**: Local JSON/Markdown with Git integration for versioning.

## 6. The A-to-Z Lifecycle of a Wiki Generation

This is the step-by-step journey of how a category wiki is born, refined, and finalized.

### Phase 0: User Input (The Raw Materials)
Everything starts with data in the `data/inputs/input_<mcat_id>/` folder. 
- **Buyer Calls**: JSON files containing transcripts of actual B2B enquiries.
- **Seller PDFs**: Product catalogs and brochures (processed via the `pdf_pipeline.py` into JSON).
- **The Trigger**: The user runs `python main.py --mcat_id <id>`.

### Phase 1: The Initial Spark (V1)
1. **Pick Sources**: The `pick_sources_node` scans the folder. For the first run (V1), it picks a "Starter Pack": up to **10 call transcripts** and **5 PDFs**.
2. **Category Detection**: The `category_node` looks at the first few sources to understand exactly what product we are dealing with (e.g., "Electric Rickshaw" or "PVC Pipes").
3. **The First Draft (CREATE)**: The `create_node` calls the LLM. It processes the starter pack and builds the first version of the wiki, filling all 12 sections.

### Phase 2: The "Ruthless" Audit (Evaluation)
1. **Scoring**: The `evaluate_node` passes the V1 wiki to an Evaluator Agent.
2. **Gap Analysis**: The evaluator assigns a score (0-10) and lists **Top Gaps** (e.g., "Missing pricing for Bihar region," "Regulatory standards for battery safety not clear").
3. **Data Request**: If the score is `< 9.0`, the evaluator requests specific data: "I need 2 more calls, 1 more PDF, and Web Search."

### Phase 3: The Refinement Loop (V2 & V3)
1. **Nudging**: If the score is low, the system forces `web_search=True` even if the LLM forgot to ask for it.
2. **Batch Update**: The `update_node` picks the *newly* requested sources.
3. **3-Source Batching**: Instead of one big call, it merges these new sources into the wiki in **batches of 3**. For each batch, it generates a **red/green diff** so you can see exactly what changed.
4. **Web Search**: If requested, the agent performs a live Google search to find missing regulatory codes or price ranges.

### Phase 4: Quality Lock & Completion
1. **The Rollback Check**: After V2 is built, it is scored again. 
   - If **V2 Score < V1 Score**, the system says "Stop! V2 made it worse," rolls back to the V1 content, and ends the run.
2. **The 3rd Try**: If the score is still low but improving, it repeats for V3.
3. **The Final Output**: Once it hits **Score 9.0** OR reaches **Iteration 3**, it stops. It saves the final wiki to `output/output_<mcat_id>/`.

### Phase 5: The Audit Trail (Logs)
The system produces more than just a wiki. In the output folder, you get:
- **wiki.md**: The final high-quality encyclopedia.
- **evaluator_result.md**: The history of how the score improved over iterations.
- **logs.md**: The "black box" recording — includes every search query, every batch diff, and every decision the agent made.

## 7. System Guardrails & Hardcoded Constraints

To ensure stability, predictability, and cost-control, the system operates under several strict guardrails and hardcoded logic gates.

### A. Execution Guardrails
- **Max Iteration Limit (3)**: The pipeline is hard-coded to stop after 3 versions (V1, V2, V3). Even if the score is still below 9.0, the system terminates to prevent infinite loops and excessive API costs.
- **Batched Processing (3)**: During updates, sources are processed in fixed batches of 3. This balances the context window (not too much data at once) with auditability (clean diffs for every 3 sources).
- **First-Run "Starter Pack"**: V1 is always built from a maximum of **10 calls and 5 PDFs**. This ensures the first draft is comprehensive but not overwhelmed by 100+ files.

### B. Quality Guardrails
- **Score-Based Rollback**: If Version `N` receives a lower score than Version `N-1`, the system automatically reverts the wiki content to `N-1` and finishes the run. It assumes the agent is "confused" or the new data was contradictory/noisy.
- **Forced Web Search Nudge**: If the evaluator score is below 9.0, the system overrides the agent's decision and forces `web_search=True`. This ensures that as long as we are below the quality threshold, we are always looking for more data.
- **9.0/10 Quality Gate**: The system treats 9.0 as the "Gold Standard." It will only stop looping early if this score is reached.

### C. Technical & Safety Constraints
- **Immediate Manifest Saving**: The system saves the `.run_manifest.json` *immediately* after picking sources for an iteration. This ensures that even if the code crashes mid-iteration, those sources are marked as "picked" and won't be duplicated in the next attempt.
- **NoneType Length Fallback**: The `call_llm` wrapper has a safety catch that treats `null` or empty LLM responses as `""` (empty string) instead of `None` to prevent `TypeError` crashes during logging.
- **Strict Section Enforcement**: The prompts are hard-coded to require all **12 sections**. The agent is forbidden from merging or renaming these sections, ensuring the output always matches the Universal Structure.

### D. Resource Limits (Per Iteration)
- **Call/PDF Limits**: The evaluator is prompted to limit its requests to **5 calls and 3 PDFs** per iteration. This prevents the system from trying to ingest too much data in a single refinement loop.

---
*Generated by Antigravity AI Assistant*
