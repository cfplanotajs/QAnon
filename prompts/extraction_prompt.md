You are extracting visible text from a kids board/card game PDF screenshot.

Return only valid JSON.
Do not include Markdown fences.
Do not invent missing content.
Use empty strings for fields you cannot find.
Preserve exact visible text in all_visible_text as much as possible.
Infer title, common_name, scientific_name, main_fact, and challenge_text only from visible text.
Do not perform QA or fact checking.
Do not rewrite text.
Do not add commentary.

Return exactly one JSON object with this shape:
{
  "card_id": "CARD-001",
  "page_number": 1,
  "title": "",
  "common_name": "",
  "scientific_name": "",
  "main_fact": "",
  "challenge_text": "",
  "all_visible_text": "",
  "screenshot_path": ""
}

Important:
card_id, page_number, and screenshot_path may be prefilled by the pipeline after validation if your values are empty or incorrect.
