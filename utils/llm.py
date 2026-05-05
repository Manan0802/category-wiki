"""
llm.py — Thin wrapper around the custom LLM gateway.

Uses raw ``requests.post`` (NOT any LangChain LLM wrapper).
Includes robust retry logic for network and timeout errors.
Tracks token usage per call for cost analysis.
All configuration is pulled from ``config.py``.
"""
import time
import logging
import requests
from requests.exceptions import RequestException

from config import API_URL, API_KEY, MODEL, MAX_TOKENS

logger = logging.getLogger(__name__)

# ── Module-level token accumulator ───────────────────────────────────────────
# Each call appends a dict here. Nodes read this for per-step tracking.
_token_log: list[dict] = []


def get_token_log() -> list[dict]:
    """Return the full token usage log (list of dicts)."""
    return _token_log


def reset_token_log():
    """Clear the token usage log (call at start of each pipeline run)."""
    _token_log.clear()


def get_total_usage() -> dict:
    """Aggregate total token usage across all calls."""
    total = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0, "calls": 0}
    for entry in _token_log:
        total["prompt_tokens"] += entry.get("prompt_tokens", 0)
        total["completion_tokens"] += entry.get("completion_tokens", 0)
        total["total_tokens"] += entry.get("total_tokens", 0)
        total["calls"] += 1
    return total


def call_llm(system_prompt: str, user_prompt: str, max_retries: int = 4, retry_delay: int = 30, pdf_base64: str = None) -> str:
    """Send a chat-completion request to the LLM gateway and return the
    assistant's response text.

    If a network error or timeout occurs, will retry up to ``max_retries`` times
    with a ``retry_delay`` wait in between.

    Token usage from each successful call is automatically logged to the
    module-level ``_token_log`` list.

    Raises
    ------
    RuntimeError
        If the HTTP request fails after all retries or the response is malformed.
    ValueError
        If the API key is not configured.
    """
    if not API_KEY:
        raise ValueError(
            "LLM_GATEWAY_API_KEY is not set.  "
            "Add it to your .env file or environment."
        )

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }

    if pdf_base64:
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_prompt},
                    {"type": "file", "file": {"file_data": pdf_base64}},
                ]
            }
        ]
        payload = {
            "model": MODEL,
            "messages": messages,
            "max_tokens": MAX_TOKENS,
            "extra_body": {
                "google": {
                    "thinking_config": {
                        "thinking_budget": 32768,
                        "include_thoughts": True,
                    }
                }
            }
        }
    else:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        payload = {
            "model": MODEL,
            "messages": messages,
            "max_tokens": MAX_TOKENS,
        }

    logger.debug(
        "LLM request → model=%s  system_len=%d  user_len=%d  has_pdf=%s",
        MODEL,
        len(system_prompt),
        len(user_prompt),
        bool(pdf_base64)
    )

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.post(
                API_URL,
                headers=headers,
                json=payload,
                timeout=160,
            )
            response.raise_for_status()
            
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            
            # ── Track token usage ────────────────────────────────────────
            usage = data.get("usage", {})
            token_entry = {
                "prompt_tokens":     usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens":      usage.get("total_tokens", 0),
                "model":             data.get("model", MODEL),
                "timestamp":         time.time(),
            }
            _token_log.append(token_entry)
            
            logger.debug(
                "LLM response ← %d chars  tokens: in=%d out=%d total=%d",
                len(content),
                token_entry["prompt_tokens"],
                token_entry["completion_tokens"],
                token_entry["total_tokens"],
            )
            return content
            
        except RequestException as exc:
            if attempt < max_retries:
                logger.warning(
                    "⚠️ LLM request failed (attempt %d/%d): %s. Retrying in %d seconds...", 
                    attempt, max_retries, exc, retry_delay
                )
                time.sleep(retry_delay)
            else:
                logger.error("❌ LLM gateway request failed after %d attempts: %s", max_retries, exc)
                raise RuntimeError(f"LLM gateway request failed after {max_retries} attempts: {exc}") from exc
                
        except (KeyError, IndexError) as exc:
            try:
                raw_data = response.json()
            except Exception:
                raw_data = response.text
                
            logger.error("Unexpected LLM response shape: %s", raw_data)
            raise RuntimeError(
                f"Malformed LLM response — missing choices[0].message.content: {raw_data}"
            ) from exc
