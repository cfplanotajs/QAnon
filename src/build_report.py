from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

import pandas as pd
from openpyxl import load_workbook

from src.schemas import IssueRecord

ISSUE_COLUMNS = [
    "issue_id",
    "card_id",
    "page_number",
    "card_title",
    "issue_type",
    "severity",
    "current_text",
    "problem",
    "suggested_fix",
    "confidence",
    "needs_human_review",
    "notes",
    "screenshot_path",
]
SEVERITY_RANK = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}


def _issues_dataframe(issues: Sequence[IssueRecord], sort_by_severity: bool) -> pd.DataFrame:
    rows = [issue.model_dump() for issue in issues]
    df = pd.DataFrame(rows, columns=ISSUE_COLUMNS)
    if df.empty:
        return df
    if sort_by_severity:
        df["severity_rank"] = df["severity"].map(SEVERITY_RANK).fillna(99)
        df = df.sort_values(by=["severity_rank", "page_number", "issue_id"]).drop(columns=["severity_rank"])
    return df


def _format_xlsx(xlsx_path: Path, freeze_header_row: bool) -> None:
    wb = load_workbook(xlsx_path)
    ws = wb.active
    ws.auto_filter.ref = ws.dimensions
    if freeze_header_row:
        ws.freeze_panes = "A2"

    for col_cells in ws.columns:
        max_len = max(len(str(cell.value)) if cell.value is not None else 0 for cell in col_cells)
        ws.column_dimensions[col_cells[0].column_letter].width = min(max(max_len + 2, 14), 60)

    wb.save(xlsx_path)


def build_reports(
    *,
    issues: Sequence[IssueRecord],
    issues_csv_path: Path,
    issues_xlsx_path: Path,
    summary_md_path: Path,
    source_pdf: Path,
    context_file: Path,
    cards_checked: int,
    output_files: Sequence[Path],
    sort_by_severity: bool,
    freeze_header_row: bool,
) -> None:
    df = _issues_dataframe(issues, sort_by_severity=sort_by_severity)
    for path in (issues_csv_path, issues_xlsx_path, summary_md_path):
        path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(issues_csv_path, index=False, encoding="utf-8")

    df.to_excel(issues_xlsx_path, index=False, engine="openpyxl")
    _format_xlsx(issues_xlsx_path, freeze_header_row=freeze_header_row)

    severity_counts = Counter(issue.severity for issue in issues)
    issue_type_counts = Counter(issue.issue_type for issue in issues)
    timestamp = datetime.now(timezone.utc).isoformat()

    summary_lines = [
        "# QA Summary",
        "",
        f"- Source PDF: `{source_pdf.name}`",
        f"- Context file: `{context_file.name}`",
        f"- Run timestamp (UTC): {timestamp}",
        f"- Pages/Cards checked: {cards_checked}",
        f"- Total issues found: {len(issues)}",
        "",
        "## Issues by Severity",
    ]

    for sev in ["Critical", "High", "Medium", "Low"]:
        summary_lines.append(f"- {sev}: {severity_counts.get(sev, 0)}")

    summary_lines.extend(["", "## Issues by Type"])
    if issue_type_counts:
        for issue_type, count in sorted(issue_type_counts.items()):
            summary_lines.append(f"- {issue_type}: {count}")
    else:
        summary_lines.append("- No issues logged")

    summary_lines.extend([
        "",
        "## Output Files",
        *[f"- `{path.as_posix()}`" for path in output_files],
        "",
        "## Recommended Next Action",
        "- Confirm that screenshots and extracted_cards.json were generated correctly and review extracted text quality.",
        "- qa_issues.csv and qa_issues.xlsx are expected to be empty in Phase 2 because no QA checks run yet.",
        "- Real issue detection will be added in later phases.",
        "",
        "Phase 2 extraction only: this run performs visual text extraction. No QA checks are executed yet.",
    ])

    summary_md_path.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")
