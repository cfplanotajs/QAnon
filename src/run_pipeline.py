from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from build_report import build_reports
from config import load_config
from render_pdf import render_pdf_pages
from schemas import CardRecord, IssueRecord


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Phase 1 MVP pipeline for kids board/card game QA checker.")
    parser.add_argument("--pdf", required=True, help="Path to source PDF, e.g. input/product.pdf")
    parser.add_argument("--context", required=True, help="Path to context text file, e.g. input/context.txt")
    parser.add_argument("--config", default="config.yaml", help="Optional config path (default: config.yaml)")
    parser.add_argument("--output-dir", help="Optional output base directory override")
    return parser.parse_args()


def _write_json(path: Path, payload: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


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
    screenshots_dir = base_output_dir / Path(config.output.screenshots_dir).name
    debug_dir = base_output_dir / Path(config.output.debug_dir).name
    extracted_cards_path = base_output_dir / Path(config.output.extracted_cards_json).name
    raw_issues_path = base_output_dir / Path(config.output.raw_issues_json).name
    issues_csv_path = base_output_dir / Path(config.output.issues_csv).name
    issues_xlsx_path = base_output_dir / Path(config.output.issues_xlsx).name
    summary_md_path = base_output_dir / Path(config.output.summary_md).name

    base_output_dir.mkdir(parents=True, exist_ok=True)
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    debug_dir.mkdir(parents=True, exist_ok=True)

    _ = context_path.read_text(encoding="utf-8")

    print("[2/5] Rendering PDF pages...")
    try:
        rendered_pages = render_pdf_pages(pdf_path=pdf_path, screenshots_dir=screenshots_dir, dpi=config.pdf.dpi)
    except RuntimeError as exc:
        print(f"Error: {exc}")
        return 1

    if not rendered_pages:
        print("Error: No pages were rendered from the PDF.")
        return 1

    print("[3/5] Creating placeholder card records...")
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
    _write_json(extracted_cards_path, [card.model_dump() for card in cards])

    print("[4/5] Building placeholder issue log...")
    issues: list[IssueRecord] = []
    max_issues = min(2, len(cards))
    for i in range(max_issues):
        card = cards[i]
        issues.append(
            IssueRecord(
                issue_id=f"ISSUE-{i + 1:03d}",
                card_id=card.card_id,
                page_number=card.page_number,
                card_title=card.title,
                issue_type="Other",
                severity="Low",
                current_text="Placeholder only",
                problem="Phase 1 placeholder issue for pipeline testing only.",
                suggested_fix="Replace with real QA findings in later phases.",
                confidence="Low",
                needs_human_review=True,
                notes="Placeholder/test issue; not a real QA finding.",
                screenshot_path=card.screenshot_path,
            )
        )
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
