from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

IssueType = Literal[
    "Factual Accuracy",
    "Scientific Name",
    "Grammar/Spelling",
    "Kid Readability",
    "Consistency",
    "Duplicate Content",
    "Safety/Brand Risk",
    "Layout/Text Length",
    "Other",
]
SeverityType = Literal["Critical", "High", "Medium", "Low"]
ConfidenceType = Literal["High", "Medium", "Low"]


class CardRecord(BaseModel):
    card_id: str
    page_number: int
    title: str = ""
    common_name: str = ""
    scientific_name: str = ""
    pronunciation: str = ""
    main_fact: str = ""
    challenge_text: str = ""
    riddle_text: str = ""
    fun_fact: str = ""
    diet_type: str = ""
    habitat: str = ""
    coating: str = ""
    size: str = ""
    speed: str = ""
    limbs: str = ""
    other_attributes: str = ""
    all_visible_text: str = ""
    screenshot_path: str


class IssueRecord(BaseModel):
    issue_id: str
    card_id: str
    page_number: int
    card_title: str
    issue_type: IssueType
    severity: SeverityType
    current_text: str
    problem: str
    suggested_fix: str
    confidence: ConfidenceType
    needs_human_review: bool
    notes: str
    screenshot_path: str
