# Board Game QA MVP

A local MVP pipeline for checking kids board/card game PDFs before production.

The tool accepts a PDF and a product context brief, extracts card/page text, runs QA checks, and outputs a designer-ready issue log.

## MVP Scope

This tool checks:

- factual accuracy
- scientific names
- spelling and grammar
- kid readability
- duplicate content
- consistency
- safety/brand risks

It does not currently:

- edit PDFs
- compare revised files
- integrate with Slack
- assign tasks to designers
- provide a web dashboard

## Requirements

- Python 3.11+
- Ollama installed locally
- Recommended Ollama models:
  - llama3.2-vision
  - qwen2.5

## Setup

Install dependencies:

pip install -r requirements.txt

Install Ollama models:

ollama pull llama3.2-vision
ollama pull qwen2.5

## Input

Place your PDF here:

input/product.pdf

Add product context here:

input/context.txt

Example context:

Product type: Kids animal facts card game
Audience: Ages 5–8
Market: USA
Language: American English
Card count: 60
Check for: factual accuracy, scientific names, grammar, readability, duplicates, consistency, safety
Tone: fun, simple, kid-friendly, educational

## Run

python src/run_pipeline.py --pdf input/product.pdf --context input/context.txt

## Output

The pipeline creates:

output/extracted_cards.json
output/raw_issues.json
output/qa_issues.csv
output/qa_issues.xlsx
output/qa_summary.md
output/screenshots/

## Notes

This MVP is designed to create a first-pass QA issue log. Human review is still required before sending corrections to designers.
