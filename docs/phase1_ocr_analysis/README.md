# Phase 1 OCR Analysis

## Reproduce

From `RS-Self-Test`:

```powershell
..\Revenue-Shield---Spine\.venv\Scripts\python.exe docs\phase1_ocr_analysis\analyze_ocr_field_structure.py
```

The script reads only `growth_ortho_ocr_output.txt`, splits its existing `PAGE` markers, matches configured labels, redacts likely PHI in evidence, and rewrites:

- `OCR_Field_Inventory.csv`
- `OCR_Analysis_Summary.json`

It does not regenerate OCR, modify the source OCR file, inspect PDFs, call external services, access databases, or use the Revenue Shield engine.
