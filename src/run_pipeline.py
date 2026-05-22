from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.build_report import build_reports
from src.config import load_config
from src.extract_cards import extract_cards_from_pages
from src.render_pdf import render_pdf_pages
from src.schemas import CardRecord, IssueRecord


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Phase 2 MVP pipeline for kids board/card game QA checker.")
    parser.add_argument("--pdf", required=True, help="Path to source PDF, e.g. input/product.pdf")
    parser.add_argument("--context", required=True, help="Path to context text file, e.g. input/context.txt")
    parser.add_argument("--config", default="config.yaml", help="Optional config path (default: config.yaml)")
    parser.add_argument("--output-dir", help="Optional output base directory override")
    return parser.parse_args()


def _write_json(path: Path, payload: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def resolve_output_path(base_output_dir: Path, configured_path: str) -> Path:
    configured = Path(configured_path)
    if configured.is_absolute():
        return configured

    configured_parts = configured.parts
    if configured_parts and configured_parts[0] == "output":
        return base_output_dir.joinpath(*configured_parts[1:])

    return base_output_dir / configured


def _placeholder_cards(rendered_pages: list[tuple[int, Path]]) -> list[CardRecord]:
    cards: list[CardRecord] = []
    for page_number, shot_path in rendered_pages:
        cards.append(
            CardRecord(
                card_id=f"CARD-{page_number:03d}",
                page_number=page_number,
                title=f"Page {page_number}",
                common_name="",
                scientific_name="",
                main_fact="",
                challenge_text="",
                all_visible_text="",
                screenshot_path=shot_path.as_posix(),
            )
        )
    return cards


def main() -> int:
    args = parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    print("[1/5] Loading config...")
    config = load_config(args.config)

    pdf_path = Path(args.pdf)
    context_path = Path(args.context)

    if not pdf_path.exists():
        print(f"Error: PDF file not found: {pdf_path}")
        return 1
    if not context_path.exists():
        print(f"Error: Context file not found: {context_path}")
        return 1

    base_output_dir = Path(args.output_dir) if args.output_dir else Path(config.output.base_dir)
    screenshots_dir = resolve_output_path(base_output_dir, config.output.screenshots_dir)
    debug_dir = resolve_output_path(base_output_dir, config.output.debug_dir)
    extracted_cards_path = resolve_output_path(base_output_dir, config.output.extracted_cards_json)
    raw_issues_path = resolve_output_path(base_output_dir, config.output.raw_issues_json)
    issues_csv_path = resolve_output_path(base_output_dir, config.output.issues_csv)
    issues_xlsx_path = resolve_output_path(base_output_dir, config.output.issues_xlsx)
    summary_md_path = resolve_output_path(base_output_dir, config.output.summary_md)

    base_output_dir.mkdir(parents=True, exist_ok=True)
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    debug_dir.mkdir(parents=True, exist_ok=True)

    context_text = context_path.read_text(encoding="utf-8")
    prompt_template = Path("prompts/extraction_prompt.md").read_text(encoding="utf-8")

    print("[2/5] Rendering PDF pages...")
    try:
        rendered_pages = render_pdf_pages(
            pdf_path=pdf_path,
            screenshots_dir=screenshots_dir,
            dpi=config.pdf.dpi,
            image_format=config.pdf.image_format,
        )
    except RuntimeError as exc:
        print(f"Error: {exc}")
        return 1
    except ValueError as exc:
        print(f"Error: {exc}")
        return 1

    if not rendered_pages:
        print("Error: No pages were rendered from the PDF.")
        return 1

    print("[3/5] Extracting card text...")
    if config.extraction.enabled:
        cards = extract_cards_from_pages(
            rendered_pages=rendered_pages,
            prompt_template=prompt_template,
            context_text=context_text,
            model=config.models.vision_extraction,
            base_url=config.ollama.base_url,
            timeout_seconds=config.ollama.timeout_seconds,
            debug_dir=debug_dir,
            save_raw_responses=config.extraction.save_raw_responses,
        )
    else:
        print("Extraction is disabled in config; using placeholder card records.")
        cards = _placeholder_cards(rendered_pages)

    _write_json(extracted_cards_path, [card.model_dump() for card in cards])

    print("[4/5] Building issue log...")
    issues: list[IssueRecord] = []
    _write_json(raw_issues_path, [issue.model_dump() for issue in issues])

    print("[5/5] Writing reports...")
    output_files = [extracted_cards_path, raw_issues_path, issues_csv_path, issues_xlsx_path, summary_md_path]
    build_reports(
        issues=issues,
        issues_csv_path=issues_csv_path,
        issues_xlsx_path=issues_xlsx_path,
        summary_md_path=summary_md_path,
        source_pdf=pdf_path,
        context_file=context_path,
        cards_checked=len(cards),
        output_files=output_files,
        sort_by_severity=config.reports.sort_by_severity,
        freeze_header_row=config.reports.freeze_header_row,
    )

    print("Done.")
    print("Created:")
    for path in output_files:
        print(f"- {path.as_posix()}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
