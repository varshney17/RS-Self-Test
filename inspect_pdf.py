
import fitz
import sys

pdf_path = sys.argv[1]
doc = fitz.open(pdf_path)

print("Pages:", len(doc))

for page_number, page in enumerate(doc, start=1):
    text = page.get_text("text")
    images = page.get_images(full=True)

    print(f"\nPage {page_number}")
    print("Extracted characters:", len(text.strip()))
    print("Embedded images:", len(images))
    print("Text preview:", repr(text[:300]))
