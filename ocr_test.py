
import pymupdf
import pytesseract
from PIL import Image
from io import BytesIO
from pathlib import Path
import shutil

PDF = r"C:\Users\LakshyaVarshney\Desktop\RS-Growth Ortho\ProgressNotes\Growthortho\progres note.pdf"

tesseract = shutil.which("tesseract")
if tesseract is None:
    tesseract_path = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")
    if not tesseract_path.is_file():
        raise FileNotFoundError(
            "Tesseract was not found on PATH or at "
            r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        )
    tesseract = str(tesseract_path)
pytesseract.pytesseract.tesseract_cmd = tesseract

doc = pymupdf.open(PDF)
all_text = []

for page_num, page in enumerate(doc, start=1):
    pix = page.get_pixmap(
        matrix=pymupdf.Matrix(2, 2),
        alpha=False
    )

    image = Image.open(BytesIO(pix.tobytes("png")))

    extracted_text = pytesseract.image_to_string(
        image,
        config="--psm 3"
    )

    all_text.append(
        f"\n{'='*50}\nPAGE {page_num}\n{'='*50}\n"
        + extracted_text
    )

with open("growth_ortho_ocr_output.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(all_text))

doc.close()

print("OCR output saved successfully.")
