"""Sanitized, one-shot Gemini diagnostics for an authorized environment.

The script reads GEMINI_API_KEY from the process environment and never prints
the key, request text, or provider response body. It is intentionally separate
from the web application so it cannot become a public diagnostic endpoint.
"""

from __future__ import annotations

import os
import re
import sys
from typing import Any

import httpx


API_VERSION = os.getenv("GEMINI_API_VERSION", "v1beta").strip() or "v1beta"
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash").strip()
TIMEOUT = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "30"))
BASE_URL = "https://generativelanguage.googleapis.com"

SYSTEM_TEXT = "Compare os dados fornecidos e responda somente em JSON válido."
USER_TEXT = (
    "<curriculo>Experiência fictícia com Python e APIs REST.</curriculo>"
    "<vaga>Busca experiência com Python e APIs REST.</vaga>"
)


def provider_field(body: Any) -> str:
    """Extract only a simple field token from an error message."""
    try:
        message = str(body.get("error", {}).get("message", ""))
    except (AttributeError, TypeError):
        return "unknown"
    match = re.search(
        r"(?:at|field|name)\s*[\"']([A-Za-z][A-Za-z0-9_.-]{0,79})",
        message,
        flags=re.IGNORECASE,
    )
    return match.group(1) if match else "unknown"


def report(stage: str, response: httpx.Response | None = None, field: str = "unknown") -> None:
    status = "network_error" if response is None else str(response.status_code)
    print(f"stage={stage} status={status} field={field}")


def run_diagnostic() -> int:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        print("stage=configuration status=missing field=GEMINI_API_KEY")
        return 2

    headers = {"x-goog-api-key": api_key}
    models_url = f"{BASE_URL}/{API_VERSION}/models"
    generate_url = f"{BASE_URL}/{API_VERSION}/models/{MODEL}:generateContent"

    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            models_response = client.get(models_url, headers=headers)
            configured_model = None
            supports_generate = False
            if models_response.is_success:
                for item in models_response.json().get("models", []):
                    name = str(item.get("name", ""))
                    if name.rsplit("/", 1)[-1] == MODEL:
                        configured_model = name
                        supports_generate = "generateContent" in item.get(
                            "supportedGenerationMethods", []
                        )
                        break
            report(
                "models",
                models_response,
                field="generateContent" if configured_model and not supports_generate else "none",
            )
            if models_response.is_success:
                print(f"stage=model_check status=200 field={'supported' if supports_generate else 'unsupported'}")

            payload: dict[str, Any] = {
                "contents": [{"role": "user", "parts": [{"text": USER_TEXT}]}]
            }
            steps = [
                ("contents", None),
                ("systemInstruction", {"parts": [{"text": SYSTEM_TEXT}]}),
                ("temperature", 0.2),
                ("maxOutputTokens", 256),
            ]
            for stage, value in steps:
                if stage != "contents":
                    if stage == "systemInstruction":
                        payload[stage] = value
                    else:
                        payload.setdefault("generationConfig", {})[stage] = value
                response = client.post(generate_url, headers=headers, json=payload)
                if response.is_success:
                    report(stage, response, field="none")
                    continue
                try:
                    body = response.json()
                except ValueError:
                    body = {}
                report(stage, response, field=provider_field(body))
                return 1
    except (httpx.TimeoutException, httpx.RequestError, ValueError, TypeError):
        report("network", field="unknown")
        return 1

    return 0


def main() -> int:
    return run_diagnostic()


if __name__ == "__main__":
    sys.exit(main())
