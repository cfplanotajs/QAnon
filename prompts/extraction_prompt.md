You are extracting visible text from a kids board/card game PDF screenshot.

Return only valid JSON.
Do not include Markdown fences.
Do not QA, fact-check, simplify, rewrite, or correct the text.
Do not invent values.
Use empty strings for missing, invisible, or uncertain fields.
Extract all visible text zones, including small side panels and bottom fact callouts.
Preserve exact visible wording as much as possible.
Product context is guidance only for understanding layout and expected fields.
Do not add commentary.

Return exactly one JSON object with this shape:
{
  "card_id": "CARD-001",
  "page_number": 1,
  "title": "",
  "common_name": "",
  "scientific_name": "",
  "pronunciation": "",
  "main_fact": "",
  "challenge_text": "",
  "riddle_text": "",
  "fun_fact": "",
  "diet_type": "",
  "habitat": "",
  "coating": "",
  "size": "",
  "speed": "",
  "limbs": "",
  "other_attributes": "",
  "all_visible_text": "",
  "screenshot_path": ""
}

Important:
card_id, page_number, and screenshot_path may be prefilled by the pipeline after validation if your values are empty or incorrect.
