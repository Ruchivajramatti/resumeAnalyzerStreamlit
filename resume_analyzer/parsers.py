from __future__ import annotations

from pathlib import Path
from typing import Optional

import docx2txt
from pdfminer.high_level import extract_text as pdf_extract_text


def extract_text(file_path: str | Path) -> str:
    """Extract text from PDF, DOCX, or TXT files.

    Uses PyMuPDF (fitz) for PDFs, docx2txt for DOCX, and utf-8 decode for TXT.
    """
    path = Path(file_path)
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        # Use pdfminer.six for broader compatibility (pure Python)
        try:
            return pdf_extract_text(str(path)) or ""
        except Exception as e:
            raise RuntimeError("Failed to parse PDF with pdfminer.six") from e
    elif suffix in {".docx"}:
        return docx2txt.process(str(path)) or ""
    elif suffix in {".txt"}:
        return path.read_text(encoding="utf-8", errors="ignore")
    else:
        raise ValueError(f"Unsupported file type: {suffix}")


def clean_text(text: str) -> str:
    """Basic cleanup: normalize whitespace."""
    return " ".join(text.split())
