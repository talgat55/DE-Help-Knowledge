import fitz

def read_pdf(path: str) -> str:
    doc = fitz.open(path)
    pages =  []

    for page_num, page in enumerate(doc, start=1):
        text = page.get_text()
        if text.strip():
            pages.append(f"\n\n---PAGE {page_num} ---\n{text}")

    return "\n".join(pages)