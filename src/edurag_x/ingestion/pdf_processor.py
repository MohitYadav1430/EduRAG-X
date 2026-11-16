import pymupdf
from pathlib import Path


class PDFProcessor:

    def extract_text(self, pdf_path):

        pdf_path = Path(pdf_path)

        # First check file extension
        if pdf_path.suffix.lower() != ".pdf":
            raise ValueError("Only PDF files are supported.")

        # Then check file existence
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        extracted_pages = []

        with pymupdf.open(pdf_path) as document:

            for page_number, page in enumerate(document, start=1):

                text = page.get_text("text").strip()

                if text:
                    extracted_pages.append({
                        "page_number": page_number,
                        "text": text,
                        "source": pdf_path.name
                    })

        return extracted_pages