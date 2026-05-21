# Kids Board/Card Game QA Checker MVP

This is a local MVP pipeline for checking kids board/card game PDFs before production.

## Phase 1 Scope

Phase 1 currently:
- renders PDF pages to screenshots
- creates placeholder extracted card data
- creates placeholder QA issues
- exports CSV/XLSX/Markdown reports

## What Phase 1 Does Not Do

- no AI extraction
- no real QA checks
- no Slack integration
- no dashboard
- no edited-file comparison

## Requirements

- Python 3.11+

## Setup

```bash
pip install -r requirements.txt
```

## Input

- `input/product.pdf`
- `input/context.txt`

## Run

```bash
python src/run_pipeline.py --pdf input/product.pdf --context input/context.txt
```

## Expected Outputs

- `output/screenshots/page_001.png`
- `output/extracted_cards.json`
- `output/raw_issues.json`
- `output/qa_issues.csv`
- `output/qa_issues.xlsx`
- `output/qa_summary.md`

## Troubleshooting

- **PDF path missing**: make sure `--pdf` points to an existing file.
- **Context path missing**: make sure `--context` points to an existing file.
- **PyMuPDF install issue**: reinstall dependencies with `pip install -r requirements.txt`.
- **No output folder**: the pipeline creates output folders automatically.

## Next Phases

- **Phase 2**: Ollama visual extraction
- **Phase 3**: copy/readability/safety QA
- **Phase 4**: consistency QA
- **Phase 5**: factual QA
