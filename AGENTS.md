# AGENTS.md

## Project

This repo is a limited-scope MVP for a kids board/card game QA checker.

The tool accepts:
1. a PDF file
2. a plain-text product context brief

It outputs:
1. extracted card/page data as JSON
2. a full QA issue log as CSV
3. a full QA issue log as XLSX
4. a short Markdown summary

The tool is intended for internal product QA before files are sent to designers for correction.

## Primary Goal

Build a local Python command-line pipeline that can check a provided kids educational board/card game PDF and generate a designer-ready issue list.

The MVP does not edit PDFs, compare revised files, or integrate with Slack yet.

## Do Not Build

Do not add:
- Slack bot
- web dashboard
- database
- cloud deployment
- user accounts
- login/auth
- Docker setup unless specifically requested
- FastAPI/Flask app unless specifically requested
- React UI
- Electron app
- automatic PDF editing
- edited-file comparison
- designer task assignment workflow
- approval workflow
- payment/account system
- complex multi-agent framework unless specifically requested

Keep this MVP local, modular, and easy to test.

## Tech Stack

Use:
- Python 3.11+
- PyMuPDF for rendering PDF pages to images
- pandas for CSV/XLSX data handling
- openpyxl for Excel export
- pydantic for schema validation
- requests for calling local Ollama API
- standard library logging/pathlib/json where possible

Use Ollama as the local model provider for MVP testing.

## Expected Repo Structure

input/
  context.txt
  README.md

output/
  screenshots/
  debug/

src/
  run_pipeline.py
  config.py
  schemas.py
  render_pdf.py
  ollama_client.py
  extract_cards.py
  qa_copy.py
  qa_readability.py
  qa_factual.py
  qa_consistency.py
  qa_safety.py
  build_report.py

prompts/
  extraction_prompt.md
  copy_qa_prompt.md
  readability_qa_prompt.md
  factual_qa_prompt.md
  consistency_qa_prompt.md
  safety_qa_prompt.md

tests/
  README.md

README.md
requirements.txt
config.yaml
.gitignore
AGENTS.md

## Main Command

The repo should be runnable with:

python src/run_pipeline.py --pdf input/product.pdf --context input/context.txt

## Output Files

The pipeline should create:

output/screenshots/page_001.png
output/screenshots/page_002.png
output/extracted_cards.json
output/raw_issues.json
output/qa_issues.csv
output/qa_issues.xlsx
output/qa_summary.md

## Card Schema

Each extracted card/page should include:

- card_id
- page_number
- title
- common_name
- scientific_name
- main_fact
- challenge_text
- all_visible_text
- screenshot_path

If a field is missing, use an empty string instead of inventing content.

## Issue Schema

Each issue should include:

- issue_id
- card_id
- page_number
- card_title
- issue_type
- severity
- current_text
- problem
- suggested_fix
- confidence
- needs_human_review
- notes
- screenshot_path

## Allowed Issue Types

Use only:

- Factual Accuracy
- Scientific Name
- Grammar/Spelling
- Kid Readability
- Consistency
- Duplicate Content
- Safety/Brand Risk
- Layout/Text Length
- Other

## Allowed Severity Values

Use only:

- Critical
- High
- Medium
- Low

## Allowed Confidence Values

Use only:

- High
- Medium
- Low

## QA Passes

Implement separate QA passes:

1. Copy QA
   - spelling
   - grammar
   - punctuation
   - capitalization
   - awkward phrasing

2. Kid Readability QA
   - age fit
   - unclear instructions
   - too advanced vocabulary
   - sentence length
   - confusing wording

3. Factual QA
   - animal names
   - scientific names
   - habitats
   - geography
   - behavior
   - diet
   - exaggerated or absolute claims

4. Consistency QA
   - duplicate animals
   - duplicate or near-duplicate facts
   - inconsistent terminology
   - inconsistent formatting
   - inconsistent scientific-name styling

5. Safety / Brand Risk QA
   - unsafe physical actions
   - scary wording
   - inappropriate jokes
   - violent or gross content
   - risky marketplace/product claims

## Factual QA Rule

For uncertain factual issues, do not present them as definitive.

Use:

needs_human_review = true

and confidence = Medium or Low.

## Error Handling

The pipeline should not crash if:
- one model call fails
- one card cannot be extracted
- the model returns invalid JSON
- the PDF has an unexpected page
- an output folder already exists

If model JSON is invalid:
1. save the raw response to output/debug/
2. log the error clearly
3. continue with the next card/check

## Report Requirements

The XLSX should be easy to review:
- frozen header row
- readable column widths
- one issue per row
- sorted by severity, then card/page number
- include screenshot path

The CSV should have the same columns.

The Markdown summary should include:
- file name
- number of pages/cards checked
- total issues found
- issues by severity
- issues by type
- recommended next action

## Coding Style

Prefer:
- simple modular functions
- clear filenames
- readable logs
- typed function signatures where useful
- small files
- minimal dependencies

Avoid:
- over-engineering
- hidden global state
- hardcoded absolute paths
- unnecessary frameworks
- vague model prompts
- silent failures

## MVP Acceptance Criteria

The MVP is successful when:

1. It renders PDF pages into screenshots.
2. It extracts visible card/page text into JSON.
3. It runs multiple QA passes.
4. It exports CSV and XLSX issue logs.
5. It produces a short summary.
6. It handles model errors gracefully.
7. It is easy to run locally with one command.
