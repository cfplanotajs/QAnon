from __future__ import annotations

import json
from pathlib import Path
from typing import Sequence

from src.ollama_client import extract_with_vision_model
from src.schemas import CardRecord


def _fallback_card(page_number: int, screenshot_path: Path) -> CardRecord:
    return CardRecord(
        card_id=f"CARD-{page_number:03d}",
        page_number=page_number,
        title=f"Page {page_number}",
        common_name="",
        scientific_name="",
        main_fact="",
        challenge_text="",
        all_visible_text="",
        screenshot_path=screenshot_path.as_posix(),
    )


def _extract_json_object(raw_response: str) -> dict:
    try:
        parsed = json.loads(raw_response)
        if isinstance(parsed, dict):
            return parsed
        raise ValueError("Top-level JSON is not an object.")
    except json.JSONDecodeError:
        start = raw_response.find("{")
        end = raw_response.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("No JSON object found in response.")
        snippet = raw_response[start : end + 1]
        parsed = json.loads(snippet)
        if not isinstance(parsed, dict):
            raise ValueError("Extracted JSON is not an object.")
        return parsed


def extract_cards_from_pages(
    *,
    rendered_pages: Sequence[tuple[int, Path]],
    prompt_template: str,
    model: str,
    base_url: str,
    timeout_seconds: int,
    debug_dir: Path,
    save_raw_responses: bool,
) -> list[CardRecord]:
    debug_dir.mkdir(parents=True, exist_ok=True)
    cards: list[CardRecord] = []

    for page_number, screenshot_path in rendered_pages:
        card_id = f"CARD-{page_number:03d}"
        prompt = (
            f"{prompt_template.strip()}\n\n"
            f"Pipeline context:\n"
            f"- card_id: {card_id}\n"
            f"- page_number: {page_number}\n"
            f"- screenshot_path: {screenshot_path.as_posix()}\n"
        )

        try:
            raw_response = extract_with_vision_model(
                model=model,
                prompt=prompt,
                image_path=screenshot_path,
                base_url=base_url,
                timeout_seconds=timeout_seconds,
            )
            if save_raw_responses:
                (debug_dir / f"extraction_page_{page_number:03d}_raw.txt").write_text(
                    raw_response,
                    encoding="utf-8",
                )
        except RuntimeError as exc:
            print(f"Warning: Extraction failed on page {page_number}: {exc}")
            (debug_dir / f"extraction_page_{page_number:03d}_error.txt").write_text(
                str(exc) + "\n",
                encoding="utf-8",
            )
            cards.append(_fallback_card(page_number, screenshot_path))
            continue

        try:
            payload = _extract_json_object(raw_response)
            extracted = CardRecord.model_validate(payload)
            normalized = extracted.model_copy(
                update={
                    "card_id": card_id,
                    "page_number": page_number,
                    "screenshot_path": screenshot_path.as_posix(),
                }
            )
            cards.append(normalized)
        except (ValueError, json.JSONDecodeError) as exc:
            print(f"Warning: Invalid extraction JSON on page {page_number}: {exc}")
            (debug_dir / f"extraction_page_{page_number:03d}_invalid.txt").write_text(
                raw_response,
                encoding="utf-8",
            )
            cards.append(_fallback_card(page_number, screenshot_path))
        except Exception as exc:  # pydantic validation
            print(f"Warning: Extraction schema validation failed on page {page_number}: {exc}")
            (debug_dir / f"extraction_page_{page_number:03d}_invalid.txt").write_text(
                raw_response,
                encoding="utf-8",
            )
            cards.append(_fallback_card(page_number, screenshot_path))

    return cards
