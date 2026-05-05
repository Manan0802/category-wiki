"""
file_handler.py — Low-level file I/O utilities.

Handles reading / writing text files and loading skill prompt templates
from the skills/ directory.  HTML comments are stripped from skill files
so that placeholder guidance never leaks into LLM prompts.
"""
import re
import logging
from pathlib import Path

from config import SKILLS_DIR

logger = logging.getLogger(__name__)

# Matches <!-- ... --> including multi-line comments
_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)


# ─── Generic file helpers ────────────────────────────────────────────────────

def read_file(path: str | Path) -> str:
    """Read and return the full contents of a UTF-8 text file."""
    path = Path(path)
    if not path.exists():
        logger.warning("File not found: %s", path)
        return ""
    return path.read_text(encoding="utf-8")


def write_file(path: str | Path, content: str) -> None:
    """Write *content* to *path*, creating parent directories as needed."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    logger.info("Wrote %d chars → %s", len(content), path)


# ─── Skill / prompt loader ───────────────────────────────────────────────────

def load_skill(skill_filename: str) -> str:
    """Load a prompt template from ``skills/<skill_filename>``.

    Strips HTML comments (<!-- ... -->) so placeholder guidance never
    reaches the LLM.  Returns empty string if file is missing or blank
    after stripping — calling node should fall back to its built-in prompt.
    """
    skill_path = SKILLS_DIR / skill_filename
    raw = read_file(skill_path)

    # Strip HTML comments (placeholder guidance for developers)
    clean = _HTML_COMMENT_RE.sub("", raw).strip()

    if not clean:
        logger.warning(
            "Skill file '%s' is empty after stripping comments — "
            "node will use fallback prompt.",
            skill_filename,
        )
    return clean