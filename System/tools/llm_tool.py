from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Optional
from urllib import error, request

_MODEL_AVAILABLE_CACHE: dict[str, bool] = {}
_LAST_ERROR: Optional[str] = None


@dataclass(frozen=True)
class LLMConfig:
    model: str = "llama3:8b"
    endpoint: str = "http://localhost:11434/v1/responses"
    timeout_seconds: int = 8


def get_last_ollama_error() -> Optional[str]:
    return _LAST_ERROR


def _set_last_error(message: Optional[str]) -> None:
    global _LAST_ERROR
    _LAST_ERROR = message


def _post_json(url: str, payload: dict, timeout_seconds: int) -> Optional[dict]:
    req = request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=timeout_seconds) as response:
        return json.loads(response.read().decode("utf-8"))


def _is_model_available(cfg: LLMConfig) -> bool:
    if cfg.model in _MODEL_AVAILABLE_CACHE:
        return _MODEL_AVAILABLE_CACHE[cfg.model]

    try:
        with request.urlopen("http://localhost:11434/api/tags", timeout=cfg.timeout_seconds) as response:
            body = json.loads(response.read().decode("utf-8"))
        models = body.get("models", []) or []
        names = {model.get("model", "") for model in models}
        available = cfg.model in names
        _MODEL_AVAILABLE_CACHE[cfg.model] = available
        if not available:
            _set_last_error(
                f"Model '{cfg.model}' is not installed. Run: ollama pull {cfg.model}"
            )
        return available
    except (error.URLError, error.HTTPError, TimeoutError, ValueError, TypeError, json.JSONDecodeError):
        _set_last_error("Ollama server is unreachable. Start it with: ollama serve")
        return False


def generate_with_ollama(prompt: str, config: Optional[LLMConfig] = None) -> Optional[str]:
    """
    Generate text from a local Ollama model.

    Returns None when Ollama is unavailable so callers can fallback safely.
    """
    cfg = config or LLMConfig()
    if not _is_model_available(cfg):
        return None

    payload = {"model": cfg.model, "input": prompt}

    try:
        body = _post_json(cfg.endpoint, payload, cfg.timeout_seconds)
        output_items = body.get("output", [])
        for item in output_items:
            for content in item.get("content", []):
                text = content.get("text", "").strip()
                if text:
                    _set_last_error(None)
                    return text
        return None
    except (error.URLError, error.HTTPError, TimeoutError, ValueError, TypeError, json.JSONDecodeError):
        # Backward-compat fallback for older Ollama installs.
        legacy_payload = {"model": cfg.model, "prompt": prompt, "stream": False}
        try:
            legacy_body = _post_json("http://localhost:11434/api/generate", legacy_payload, cfg.timeout_seconds)
            output = legacy_body.get("response", "").strip()
            if output:
                _set_last_error(None)
            return output or None
        except (error.URLError, error.HTTPError, TimeoutError, ValueError, TypeError, json.JSONDecodeError):
            _set_last_error(
                "Generation failed for both /v1/responses and /api/generate. "
                "Check Ollama version compatibility and model installation."
            )
            return None
