"""
Configuration module for Category Wiki Agent.
Loads environment variables and provides centralized config.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# ── Load .env from project root ──────────────────────────────────────────────
load_dotenv(Path(__file__).parent / ".env")

# ── Project root (absolute, so every module resolves paths correctly) ────────
PROJECT_ROOT = Path(__file__).parent.resolve()

# ── LLM Gateway Configuration ───────────────────────────────────────────────
API_URL = os.getenv(
    "LLM_GATEWAY_URL",
    "https://imllm.intermesh.net/v1/chat/completions",
)
API_KEY  = os.getenv("LLM_GATEWAY_API_KEY")
MODEL    = os.getenv("LLM_MODEL", "google/gemini-2.5-pro")
MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "32000"))

# ── Directory paths ──────────────────────────────────────────────────────────
RAW_DIR    = PROJECT_ROOT / "data" / "inputs"   # mcat folders live here
OUTPUT_DIR = PROJECT_ROOT / "output"            # root output directory
SKILLS_DIR = PROJECT_ROOT / "skills"

# ── Runtime flags ────────────────────────────────────────────────────────────
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
DETAILED_LOGS = os.getenv("DETAILED_LOGS", "False").lower() in ("true", "1", "yes")
DYNAMIC_WEB_SEARCH = os.getenv("DYNAMIC_WEB_SEARCH", "False").lower() in ("true", "1", "yes")

# ── Ensure required directories exist ────────────────────────────────────────
RAW_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)