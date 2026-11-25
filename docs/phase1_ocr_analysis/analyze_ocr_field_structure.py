import argparse
import csv
import json
import re
from pathlib import Path


PAGE_RE = re.compile(r"^={10,}\s*\nPAGE\s+(\d+)\s*\n={10,}", re.MULTILINE)
PHI_PATTERNS = [
    (re.compile(r"\bVeloss(?:\s+[A-Z])?\s+Epperson\b"), "[REDACTED PATIENT NAME]"),
    (re.compile(r"(?i)\bDocument\s+ID:\s*[^\s]+"), "Document ID: [REDACTED DOCUMENT ID]"),
    (re.compile(r"(?i)\bDocument\s+1D:\s*[^\s]+"), "Document ID: [REDACTED DOCUMENT ID]"),
    (re.compile(r"\b3[£E]904C32(?:\.\d+)?(?:0?1[¢c]?)?\b"), "[REDACTED DOCUMENT ID]"),
    (re.compile(r"(?i)\bUpdox e-Sign:\s*[^/]+"), "Updox e-Sign: [REDACTED SIGNATURE ID]"),
    (re.compile(r"\b(?:Veloss|[A-Z][a-z]+)\s+[A-Z]\s+[A-Z][a-z]+\b"), "[REDACTED PATIENT NAME]"),
    (re.compile(r"\b\d{3}-\d{9}\b"), "[REDACTED ACCOUNT]"),
    (re.compile(r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2}, \d{4}\b"), "[REDACTED DATE]"),
    (re.compile(r"\b\d{1,2}/\d{1,2}/\d{4}(?:,\s+\d{1,2}:?\d{2}:\d{2}\s*[AP]M)?\b"), "[REDACTED DATE/TIME]"),
    (re.compile(r"\b\d{3}-\d{3}-\d{4}\b"), "[REDACTED PHONE/FAX]"),
    (re.compile(r"\b\d{10,}\b"), "[REDACTED IDENTIFIER]"),
]

FIELD_RULES = [
    ("Administrative", "select Fax server", "fax_server_header", "PRESENT_BUT_INCONSISTENT", "No", "Low", "Fax-server timestamp and page counter repeated with clinical text."),
    ("Patient Demographics", "Patient:", "patient_name", "DUPLICATED", "Yes", "No", "Repeated on each of the first three pages."),
    ("Patient Identifiers", "Acct #:", "account_number", "PRESENT_AND_CLEAR", "Yes", "Yes", "Present on pages 1-3."),
    ("Encounter", "Visit Date:", "visit_date", "PRESENT_BUT_INCONSISTENT", "Yes", "Yes", "Repeated, but page 2 contains 'Dos:' instead of a visit-date label."),
    ("Patient Demographics", "DOB:", "date_of_birth", "DUPLICATED", "Yes", "Yes", "Repeated on pages 1-3."),
    ("Payer", "FSC:", "coverage_class", "PRESENT_AND_CLEAR", "No", "Yes", "FSC label appears once and Medicare is clear."),
    ("Payer", "Payor:", "payor", "PRESENT_AND_CLEAR", "Yes", "Yes", "MEDICARE is present."),
    ("Provider", "Clinician:", "clinician", "PRESENT_AND_CLEAR", "Yes", "Yes", "PT clinician name and credentials."),
    ("Provider", "Prim Phy:", "primary_physician", "PRESENT_AND_CLEAR", "No", "Yes", "Name is present."),
    ("Administrative", "Insured:", "insured_status", "PRESENT_AND_CLEAR", "No", "No", "Value: Not Specified."),
    ("Administrative", "Employer:", "employer_status", "PRESENT_AND_CLEAR", "No", "No", "Value: Retired."),
    ("Encounter", "Inj. Date:", "injury_date", "PRESENT_AND_CLEAR", "Yes", "Yes", "Date is present."),
    ("Encounter", "Visits:", "visit_count", "PRESENT_AND_CLEAR", "Yes", "No", "Numeric value 10."),
    ("Administrative", "Surg. Date:", "surgical_date", "PRESENT_AND_CLEAR", "No", "Yes", "Value: Not Specified."),
    ("Clinical", "CxyNs:", "ambiguous_cxy_count", "AMBIGUOUS", "Yes", "No", "OCR is likely a section or count, but its intended label is uncertain."),
    ("Clinical", "Plan of Care", "plan_of_care", "PRESENT_AND_CLEAR", "No", "Yes", "Section begins on page 1."),
    ("Assessment", "Diagnoses", "diagnosis_section", "PRESENT_AND_CLEAR", "No", "Yes", "Diagnosis section includes spine and urinary diagnoses."),
    ("Diagnosis", "M54.50", "icd_label_m54_50", "PRESENT_BUT_INCONSISTENT", "Yes", "Yes", "OCR shows 'Spine MS4.50' instead of a clear code."),
    ("Diagnosis", "R39.15", "icd_label_r39_15", "PRESENT_AND_CLEAR", "Yes", "Yes", "Urgency diagnosis is present."),
    ("Diagnosis", "R35.0", "icd_label_r35_0", "PRESENT_AND_CLEAR", "Yes", "Yes", "Frequency diagnosis is present."),
    ("Chief Complaint", "Subjective", "subjective", "PRESENT_AND_CLEAR", "No", "Yes", "Subjective section is present."),
    ("Functional Status", "ADL/ Functional Status:", "functional_status", "PRESENT_AND_CLEAR", "No", "Yes", "Current limitations are described."),
    ("Physical Examination", "Range of Motion:", "range_of_motion", "PRESENT_BUT_INCONSISTENT", "Yes", "Yes", "Percentages and goals are split across pages 1-2."),
    ("Physical Examination", "Muscle Testing:", "muscle_testing", "PRESENT_BUT_INCONSISTENT", "Yes", "Yes", "Includes lower-extremity and pelvic-floor testing."),
    ("Physical Examination", "Special Tests:", "special_tests", "PRESENT_AND_CLEAR", "Yes", "Yes", "Anal wink and motor-control findings."),
    ("Assessment", "Assessment", "assessment", "PRESENT_AND_CLEAR", "No", "Yes", "Education and prognosis narrative is present."),
    ("Treatment Plan", "Recommendations:", "recommendations", "PRESENT_AND_CLEAR", "No", "Yes", "Pain, function, strength and premorbid-state goals."),
    ("Chief Complaint", "Chief Complaint:", "chief_complaint", "PRESENT_BUT_INCONSISTENT", "Yes", "Yes", "Pain severity appears with formatting artifacts."),
    ("Goals", "L7G", "long_term_goal", "AMBIGUOUS", "Yes", "Yes", "OCR likely reads 'LTG' as 'L7G' and also splits goal text."),
    ("Goals", "STG", "short_term_goal", "PRESENT_BUT_INCONSISTENT", "Yes", "Yes", "Short-term goal text and dates are present."),
    ("Outcome", "GROC", "groc", "PRESENT_BUT_INCONSISTENT", "Yes", "Yes", "Current GROC values +2/+4 are separated by surrounding text."),
    ("Treatment Plan", "Therapeutic Contents:", "therapeutic_contents", "PRESENT_AND_CLEAR", "No", "Yes", "Multiple therapy modalities are listed."),
    ("Treatment Plan", "Amount, Frequency and Duration:", "treatment_frequency_duration", "PRESENT_AND_CLEAR", "No", "Yes", "Two visits/week and four-week duration."),
    ("Follow-up", "Certification Period:", "certification_period", "PRESENT_AND_CLEAR", "Yes", "Yes", "From and to dates are present."),
    ("Administrative", "Signed on", "signature_date", "PRESENT_AND_CLEAR", "Yes", "Yes", "Signature timestamp is present."),
    ("Administrative", "Document ID:", "document_id", "DUPLICATED", "Yes", "Yes", "Repeated on pages 1-3."),
    ("Administrative", "Status: Signed off", "signature_status", "DUPLICATED", "No", "Yes", "Repeated on pages 1-3."),
    ("Provider", "Christopher M. Kaczmarek", "provider_signature", "DUPLICATED", "No", "Yes", "Repeated signature/credentials on pages 1-3."),
    ("Administrative", "Page 1 of 3", "source_page_footer", "PRESENT_BUT_INCONSISTENT", "No", "No", "Also includes scanner/fax page counter text."),
    ("Correspondence", "Correspondence for", "correspondence_header", "PRESENT_AND_CLEAR", "No", "No", "Appears only on page 4."),
    ("Correspondence", "Import date", "correspondence_import_date", "PRESENT_BUT_INCONSISTENT", "Yes", "No", "Mon Oct 17 text plus separate sent/sign-off fields."),
    ("Correspondence", "Sent", "correspondence_sent", "PRESENT_AND_CLEAR", "No", "No", "Boolean-like values false/true are present."),
    ("Correspondence", "Sign off", "correspondence_signoff", "PRESENT_AND_CLEAR", "No", "No", "Boolean-like value false is present."),
]

MISSING_RULES = [
    ("Clinical", "Explicit HPI label", "hpi", "MISSING", "No", "Yes", "No explicit History of Present Illness or HPI section found."),
    ("Clinical", "Review of Systems", "review_of_systems", "MISSING", "No", "Yes", "No explicit ROS section found."),
    ("Clinical", "Current Medications", "medications", "MISSING", "No", "Yes", "No complete medication list found."),
    ("Clinical", "Allergies", "allergies", "MISSING", "No", "Yes", "No allergy section found."),
    ("Clinical", "Past Medical History", "medical_history", "MISSING", "No", "Yes", "No explicit past-medical-history section found."),
    ("Clinical", "Surgical History", "surgical_history", "PARTIALLY_EXTRACTED", "No", "Yes", "Only 'Surg. Date: Not Specified'; no detailed history."),
    ("Clinical", "Imaging", "imaging_findings", "MISSING", "No", "Yes", "No imaging findings section found."),
    ("Clinical", "Procedure CPT/HCPCS", "procedure_codes", "MISSING", "No", "Yes", "Therapeutic modalities are present, but no CPT/HCPCS procedure code list was found."),
    ("Encounter", "Facility name/address", "facility_name_address", "PARTIALLY_EXTRACTED", "No", "No", "Fax/phone details and address fragments exist; no unambiguous facility name."),
    ("Follow-up", "Explicit follow-up visit date", "follow_up_visit_date", "MISSING", "No", "Yes", "Certification and goal dates exist, but no explicit next appointment date."),
]


def redact(text):
    for pattern, replacement in PHI_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def split_pages(text):
    matches = list(PAGE_RE.finditer(text))
    pages = {}
    for index, match in enumerate(matches):
        page_number = int(match.group(1))
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        pages[page_number] = text[start:end].strip()
    return pages


def evidence_for(pages, label, page_hint=None):
    hits = []
    for page_number, body in pages.items():
        if page_hint is not None and page_hint != page_number:
            continue
        for line in body.splitlines():
            if label.lower() in line.lower():
                hits.append((page_number, line.strip()))
    if not hits:
        return []
    return hits[:3]


def main():
    parser = argparse.ArgumentParser(description="Analyze existing OCR text labels without OCR regeneration.")
    parser.add_argument("ocr_file", nargs="?", default="../../growth_ortho_ocr_output.txt")
    parser.add_argument("--out-dir", default=".")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    ocr_path = Path(args.ocr_file)
    if not ocr_path.is_absolute():
        ocr_path = (script_dir / ocr_path).resolve()
    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = (script_dir / out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    text = ocr_path.read_text(encoding="utf-8")
    pages = split_pages(text)

    rows = []
    observed_fields = set()
    for category, original_label, normalized, status, normalize, coding, observation in FIELD_RULES:
        evidence = evidence_for(pages, original_label)
        if evidence:
            observed_fields.add(normalized)
            locations = "; ".join(f"Page {page}" for page, _ in evidence)
            values = " | ".join(redact(line) for _, line in evidence)
            value_complete = "Yes" if len(evidence) else "No"
            rows.append({
                "Field Category": category,
                "Original Label": original_label,
                "Normalized Name": normalized,
                "Source Location": locations,
                "Quality Status": status,
                "Normalization Required": normalize,
                "Coding Relevance": coding,
                "Observation": observation,
                "Redacted Evidence": values,
                "Value Complete": value_complete,
            })
        else:
            rows.append({
                "Field Category": category,
                "Original Label": original_label,
                "Normalized Name": normalized,
                "Source Location": "Not observed",
                "Quality Status": "MISSING",
                "Normalization Required": normalize,
                "Coding Relevance": coding,
                "Observation": observation,
                "Redacted Evidence": "",
                "Value Complete": "No",
            })

    for category, original_label, normalized, status, normalize, coding, observation in MISSING_RULES:
        rows.append({
            "Field Category": category,
            "Original Label": original_label,
            "Normalized Name": normalized,
            "Source Location": "Not observed in OCR pages 1-4",
            "Quality Status": status,
            "Normalization Required": normalize,
            "Coding Relevance": coding,
            "Observation": observation,
            "Redacted Evidence": "",
            "Value Complete": "No",
        })

    csv_path = out_dir / "OCR_Field_Inventory.csv"
    fieldnames = list(rows[0].keys())
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    status_counts = {}
    for row in rows:
        status_counts[row["Quality Status"]] = status_counts.get(row["Quality Status"], 0) + 1

    summary = {
        "files_inspected": 1,
        "ocr_samples_analyzed": 1,
        "pages_analyzed": len(pages),
        "unique_observed_fields": len(observed_fields),
        "inventory_rows": len(rows),
        "quality_status_counts": status_counts,
    }
    json_path = out_dir / "OCR_Analysis_Summary.json"
    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
