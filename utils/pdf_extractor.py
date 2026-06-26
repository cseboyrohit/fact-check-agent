"""
PDF text extraction using PyMuPDF (fitz).
Falls back to pdfplumber if fitz is unavailable.
"""
import io


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract all text from a PDF given its bytes."""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        pages = []
        for page in doc:
            pages.append(page.get_text("text"))
        doc.close()
        return "\n".join(pages)
    except ImportError:
        pass

    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            return "\n".join(
                page.extract_text() or "" for page in pdf.pages
            )
    except ImportError:
        pass

    raise RuntimeError(
        "No PDF library found. Install PyMuPDF: pip install pymupdf"
    )
