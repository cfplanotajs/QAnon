from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

import fitz


def render_pdf_pages(
    pdf_path: Path,
    screenshots_dir: Path,
    dpi: int,
    image_format: str = "png",
) -> List[Tuple[int, Path]]:
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    try:
        document = fitz.open(pdf_path)
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"Could not open PDF '{pdf_path}': {exc}") from exc

    normalized_format = image_format.lower().lstrip(".")
    if normalized_format not in {"png", "jpg", "jpeg"}:
        raise ValueError(
            f"Unsupported image format '{image_format}'. Supported formats: png, jpg, jpeg."
        )

    rendered_pages: list[tuple[int, Path]] = []
    with document:
        zoom = dpi / 72.0
        matrix = fitz.Matrix(zoom, zoom)

        for page_index in range(document.page_count):
            page_number = page_index + 1
            try:
                page = document.load_page(page_index)
                pixmap = page.get_pixmap(matrix=matrix)
                output_path = screenshots_dir / f"page_{page_number:03d}.{normalized_format}"
                pixmap.save(output_path)
                rendered_pages.append((page_number, output_path))
                print(f"Rendered page {page_number} -> {output_path}")
            except Exception as exc:  # noqa: BLE001
                print(f"Warning: Could not render page {page_number}: {exc}")

    return rendered_pages
