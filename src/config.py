from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel


class PdfConfig(BaseModel):
    dpi: int = 220
    image_format: str = "png"


class OutputConfig(BaseModel):
    base_dir: str = "output"
    screenshots_dir: str = "output/screenshots"
    debug_dir: str = "output/debug"
    extracted_cards_json: str = "output/extracted_cards.json"
    raw_issues_json: str = "output/raw_issues.json"
    issues_csv: str = "output/qa_issues.csv"
    issues_xlsx: str = "output/qa_issues.xlsx"
    summary_md: str = "output/qa_summary.md"


class QaConfig(BaseModel):
    default_market: str = "USA"
    default_language: str = "American English"
    default_age_range: str = "5-8"


class ReportsConfig(BaseModel):
    sort_by_severity: bool = True
    freeze_header_row: bool = True


class AppConfig(BaseModel):
    pdf: PdfConfig = PdfConfig()
    output: OutputConfig = OutputConfig()
    qa: QaConfig = QaConfig()
    reports: ReportsConfig = ReportsConfig()


def load_config(config_path: str | Path | None = None) -> AppConfig:
    path = Path(config_path or "config.yaml")
    if not path.exists():
        return AppConfig()

    with path.open("r", encoding="utf-8") as f:
        raw: dict[str, Any] = yaml.safe_load(f) or {}

    return AppConfig(**raw)
