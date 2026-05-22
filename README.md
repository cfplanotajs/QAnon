# Kids Board/Card Game QA Checker MVP

This is a local MVP pipeline for checking kids board/card game PDFs before production.

## Phase 2 Scope (Current)

Phase 2 currently:
- renders PDF pages to screenshots
- runs visual extraction with local Ollama (`llama3.2-vision`) per screenshot
- uses `input/context.txt` to guide extraction context only (not QA)
- validates extracted card JSON with Pydantic schema
- falls back safely per page when extraction fails
- exports CSV/XLSX/Markdown reports

## Still Not Included Yet

- no real QA checks (copy/readability/factual/consistency/safety)
- no Slack integration
- no dashboard
- no database
- no edited-file comparison
- no automatic PDF editing

## Requirements

- Python 3.11+
- Ollama installed locally

## Setup

```bash
pip install -r requirements.txt
```

Install the required local vision model:

```bash
ollama pull llama3.2-vision
```

Verify Ollama/model:

```bash
ollama list
ollama run llama3.2-vision
```

## Input

- `input/product.pdf`
- `input/context.txt`

## Run

```bash
python src/run_pipeline.py --pdf input/product.pdf --context input/context.txt
```

Also supported:

```bash
python -m src.run_pipeline --pdf input/product.pdf --context input/context.txt
```

## Expected Outputs

- `output/screenshots/page_001.png`
- `output/extracted_cards.json`
- `output/raw_issues.json`
- `output/qa_issues.csv`
- `output/qa_issues.xlsx`
- `output/qa_summary.md`

If Ollama extraction succeeds, `output/extracted_cards.json` should contain real extracted visible text where possible.
In Phase 2, `output/extracted_cards.json` is the main output to inspect.
`output/qa_issues.csv` and `output/qa_issues.xlsx` are expected to contain headers with zero issue rows until QA passes are implemented.

## Troubleshooting

- **PDF path missing**: make sure `--pdf` points to an existing file.
- **Context path missing**: make sure `--context` points to an existing file.
- **Ollama not running**: start Ollama and verify `http://localhost:11434` is reachable.
- **`llama3.2-vision` not installed**: run `ollama pull llama3.2-vision`.
- **Invalid JSON from model**: pipeline falls back per page and writes debug files in `output/debug/`.
- **Extraction fields are empty**: check `output/debug/` for `_raw`, `_invalid`, and `_error` extraction files.
- **Dependency installation issues**: rerun `pip install -r requirements.txt`.

## Next Phases

- **Phase 3**: copy/readability/safety QA
- **Phase 4**: consistency QA
- **Phase 5**: factual QA
