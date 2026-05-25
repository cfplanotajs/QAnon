from __future__ import annotations

import base64
from pathlib import Path

import requests


def extract_with_vision_model(
    model: str,
    prompt: str,
    image_path: Path,
    base_url: str,
    timeout_seconds: int,
) -> str:
    try:
        image_bytes = image_path.read_bytes()
    except OSError as exc:
        raise RuntimeError(f"Could not read image file '{image_path}': {exc}") from exc

    encoded_image = base64.b64encode(image_bytes).decode("utf-8")
    endpoint = f"{base_url.rstrip('/')}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "images": [encoded_image],
        "stream": False,
    }

    try:
        response = requests.post(endpoint, json=payload, timeout=timeout_seconds)
    except requests.exceptions.Timeout as exc:
        raise RuntimeError(
            f"Ollama request timed out after {timeout_seconds}s for image '{image_path.name}'."
        ) from exc
    except requests.exceptions.ConnectionError as exc:
        raise RuntimeError(f"Could not connect to Ollama at '{base_url}': {exc}") from exc
    except requests.RequestException as exc:
        raise RuntimeError(f"Ollama request failed for image '{image_path.name}': {exc}") from exc

    if response.status_code != 200:
        raise RuntimeError(
            f"Ollama returned HTTP {response.status_code} for image '{image_path.name}': {response.text}"
        )

    try:
        body = response.json()
    except ValueError as exc:
        raise RuntimeError(f"Ollama returned non-JSON response for image '{image_path.name}'.") from exc

    model_response = body.get("response")
    if not isinstance(model_response, str):
        raise RuntimeError(
            f"Ollama response missing expected 'response' text field for image '{image_path.name}'."
        )

    return model_response
