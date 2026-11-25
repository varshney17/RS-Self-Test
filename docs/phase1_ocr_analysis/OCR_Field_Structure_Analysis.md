# OCR Field Structure Analysis

## Executive Summary

One OCR text sample was inspected: `growth_ortho_ocr_output.txt`. It contains four clearly marked OCR pages and represents one physical-therapy progress-note document plus a page-4 correspondence metadata block. The sample contains 42 normalized observed fields across 53 inventory rows. Most fields are present and identifiable, but repeated headers, OCR substitutions, split sections, and missing expected clinical sections prevent the output from being treated as a production-ready schema without review.

No source PDF or alternate OCR sample was present inside `RS-Self-Test`, so this report does not determine whether an issue originated in the source or in OCR.

## Files Inspected

| File | Type | Role |
|---|---|---|
| `growth_ortho_ocr_output.txt` | OCR text | Primary analysis sample; 4 marked pages |
| `ocr_test.py` | Python | Identifies the intended source PDF name and describes OCR generation |
| `inspect_pdf.py` | Python | Supporting file-text inspection utility; not executed against a workspace PDF |
| `requirements.txt` | Text | Existing Python dependency declaration |
| `analyze_ocr_field_structure.py` | Python | Reusable label-occurrence inventory script |

## Document Structure

- Pages 1-3 contain the apparent rehabilitation progress note.
- Page 1 contains patient header, encounter details, plan of care, diagnoses, subjective narrative, assessment, goals, range-of-motion and muscle-testing evidence.
- Page 2 continues goals and muscle testing, then contains the plan and therapeutic-content list.
- Page 3 contains remaining therapy modalities, signature data, certification period, and footer.
- Page 4 is a correspondence/admin block with labels and values in a table-like layout.
- The output repeats patient, provider, account, visit/date, document ID and page/footer information across pages.

## Field Inventory

The complete machine-readable inventory is [`OCR_Field_Inventory.csv`](OCR_Field_Inventory.csv). The 53 inventory rows cover 42 normalized observed fields and 10 explicit missing/partial expected fields. Redacted representative evidence is included in the CSV.

### Observed Field Summary

| Field Category | Original Label(s) | Normalized Name | Location | Status | Coding Relevance |
|---|---|---|---|---|---|
| Administrative | `select Fax server` | fax_server_header | Page 1-3 | PRESENT_BUT_INCONSISTENT | Low |
| Demographics | `Patient:` | patient_name | Page 1-3 | DUPLICATED | No |
| Identifier | `Acct #: ` | account_number | Page 1-3 | PRESENT_AND_CLEAR | Yes |
| Encounter | `Visit Date:`, `Dos:` | visit_date | Page 1-3 | PRESENT_BUT_INCONSISTENT | Yes |
| Demographics | `DOB:` | date_of_birth | Page 1-3 | DUPLICATED | Yes |
| Payer | `FSC:` | coverage_class | Page 1 | PRESENT_AND_CLEAR | Yes |
| Payer | `Payor:` | payor | Page 1 | PRESENT_AND_CLEAR | Yes |
| Provider | `Clinician:` | clinician | Page 1 | PRESENT_AND_CLEAR | Yes |
| Provider | `Prim Phy:` | primary_physician | Page 1 | PRESENT_AND_CLEAR | Yes |
| Administrative | `Insured:` | insured_status | Page 1 | PRESENT_AND_CLEAR | No |
| Administrative | `Employer:` | employer_status | Page 1 | PRESENT_AND_CLEAR | No |
| Encounter | `Inj. Date:` | injury_date | Page 1 | PRESENT_AND_CLEAR | Yes |
| Encounter | `Visits:` | visit_count | Page 1 | PRESENT_AND_CLEAR | No |
| Encounter | `Surg. Date:` | surgical_date | Page 1 | PRESENT_AND_CLEAR | Yes |
| Clinical | `CxyNs:` | ambiguous_cxy_count | Page 1 | AMBIGUOUS | No |
| Plan | `Plan of Care` | plan_of_care | Page 1-2 | PRESENT_AND_CLEAR | Yes |
| Assessment | `Diagnoses` | diagnosis_section | Page 1 | PRESENT_AND_CLEAR | Yes |
| Diagnosis | `Spine MS4.50` | icd_label_m54_50 | Page 1 | PRESENT_BUT_INCONSISTENT | Yes |
| Diagnosis | `R39.15` | icd_label_r39_15 | Page 1 | PRESENT_AND_CLEAR | Yes |
| Diagnosis | `R35.0` | icd_label_r35_0 | Page 1 | PRESENT_AND_CLEAR | Yes |
| Chief Complaint | `Subjective` | subjective | Page 1 | PRESENT_AND_CLEAR | Yes |
| Functional Status | `ADL/ Functional Status:` | functional_status | Page 1 | PRESENT_AND_CLEAR | Yes |
| Examination | `Range of Motion:` | range_of_motion | Page 1-2 | PRESENT_BUT_INCONSISTENT | Yes |
| Examination | `Muscle Testing:` | muscle_testing | Page 1-2 | PRESENT_BUT_INCONSISTENT | Yes |
| Examination | `Special Tests:` | special_tests | Page 2 | PRESENT_AND_CLEAR | Yes |
| Assessment | `Assessment` | assessment | Page 1-2 | PRESENT_AND_CLEAR | Yes |
| Treatment | `Recommendations:` | recommendations | Page 1 | PRESENT_AND_CLEAR | Yes |
| Chief Complaint | `Chief Complaint:` | chief_complaint | Page 1-2 | PRESENT_BUT_INCONSISTENT | Yes |
| Goals | `L7G` | long_term_goal | Page 1-2 | AMBIGUOUS | Yes |
| Goals | `STG` | short_term_goal | Page 2 | PRESENT_BUT_INCONSISTENT | Yes |
| Outcome | `GROC` | groc | Page 1-2 | PRESENT_BUT_INCONSISTENT | Yes |
| Treatment | `Therapeutic Contents:` | therapeutic_contents | Page 2 | PRESENT_AND_CLEAR | Yes |
| Treatment | `Amount, Frequency and Duration:` | treatment_frequency_duration | Page 2 | PRESENT_AND_CLEAR | Yes |
| Follow-up | `Certification Period:` | certification_period | Page 3 | PRESENT_AND_CLEAR | Yes |
| Administrative | `Signed on` | signature_date | Page 3 | PRESENT_AND_CLEAR | Yes |
| Administrative | `Document ID:`/`Document 1D:` | document_id | Page 1-3 | DUPLICATED | Yes |
| Administrative | `Status: Signed off` | signature_status | Page 1-3 | DUPLICATED | Yes |
| Provider | Clinician/signature name | provider_signature | Page 1-3 | DUPLICATED | Yes |
| Administrative | `Page 1 of 3` | source_page_footer | Page 1-3 | PRESENT_BUT_INCONSISTENT | No |
| Correspondence | `Correspondence for` | correspondence_header | Page 4 | PRESENT_AND_CLEAR | No |
| Correspondence | `Import date` | correspondence_import_date | Page 4 | PRESENT_BUT_INCONSISTENT | No |
| Correspondence | `Sent` | correspondence_sent | Page 4 | PRESENT_AND_CLEAR | No |
| Correspondence | `Sign off` | correspondence_signoff | Page 4 | PRESENT_AND_CLEAR | No |

### Missing or Partially Extracted Expected Fields

| Original/Expected Label | Normalized Name | Status | Observation |
|---|---|---|---|
| History of Present Illness/HPI | hpi | MISSING | No explicit HPI section found. |
| Review of Systems | review_of_systems | MISSING | No explicit ROS section found. |
| Current Medications | medications | MISSING | No medication list found. |
| Allergies | allergies | MISSING | No allergy section found. |
| Past Medical History | medical_history | MISSING | No explicit past-medical-history section found. |
| Surgical History | surgical_history | PARTIALLY_EXTRACTED | Only `Surg. Date: Not Specified`; no detailed surgical history. |
| Imaging | imaging_findings | MISSING | No imaging findings section found. |
| CPT/HCPCS procedure codes | procedure_codes | MISSING | Therapy modality descriptions exist, but no code list is present. |
| Facility name/address | facility_name_address | PARTIALLY_EXTRACTED | Phone/fax/address fragments are present; no unambiguous facility name. |
| Explicit follow-up visit date | follow_up_visit_date | MISSING | Goal and certification dates exist, but no explicit next appointment date. |

## Field Quality Observations

### Repeated labels and inconsistent presentation

- The patient name is repeated on pages 1-3.
- Account number, visit date and DOB are repeated across the progress-note pages.
- Clinician/provider signature data is repeated on pages 1-3.
- Document ID/signature-status text differs slightly between OCR appearances: `Document ID:` versus `Document 1D:`, and OCR-character substitutions in the ID.
- Page metadata differs from clinical page numbering: fax-server page counters such as `PAGE 2/011` appear with document footer `Page 1 of 3`.
- Visit date is `Visit Date:` on the header, while page 2 also contains `Dos:` with a date that appears to be DOB in this OCR sample.

### OCR extraction ambiguity

- `Spine MS4.50` is not a clear equivalent of the diagnosis code label and is not safe to normalize semantically without source verification.
- `L7G Achieve` likely represents `LTG Achieve`, but the substitution is not established by automated evidence alone.
- `CxyNs: 1` cannot be interpreted as a field name or value with confidence.
- `Subjective E: inati` appears corrupted and should not be mapped semantically.
- Some line and bullet boundaries have been lost or merged.

### Reading order and section boundaries

- Range-of-motion and goal content continues across pages.
- Chief-complaint and muscle-testing sections are split by the page 1-2 boundary.
- Therapeutic-content bullets continue onto page 3.
- Page 4 begins a separate correspondence record and is not part of the clinical progress-note pagination.

### Missing versus unavailable information

- Missing explicit HPI, ROS, medication, allergy, past-medical-history, imaging and procedure-code fields could be absent from the source or omitted by OCR. The available sample alone cannot distinguish these causes.
- `Surg. Date: Not Specified` is an explicit value but does not provide a surgical-history narrative.
- Facility identity is not complete; address and fax/phone lines are visible.

### Downstream clinical/coding relevance

- The diagnosis strings and procedure/therapy descriptions are potentially coding-relevant.
- Dates, payer, coverage, provider and certification text are administratively relevant.
- Goals and treatment-frequency text are clinically relevant but must not be converted to ICD-10/CPT codes in this phase.
- M54.50, R39.15 and R35.0 should be treated as OCR-derived candidates only until source verification.

## Important Inconsistencies

1. `Spine MS4.50` instead of a clearly readable diagnosis code.
2. `L7G` may represent `LTG`.
3. `Dos:` appears beside a value that visually resembles a DOB.
4. Document ID is inconsistently OCRed and is redacted in this report.
5. Fax/server page counters are interleaved with clinical footer text.
6. Goals, ROM, chief complaints and muscle testing cross page boundaries.
7. Page 4 has correspondence metadata that is not an encounter clinical page.

## Completion Criteria Counts

| Measure | Count |
|---|---:|
| Files inspected | 1 OCR text + 3 workspace support/script files |
| OCR samples analyzed | 1 |
| Pages analyzed | 4 |
| Unique normalized observed fields | 42 |
| Inventory rows | 53 |
| Inconsistent fields | 9 |
| Missing fields | 9 |
| Duplicated fields | 5 |
| Ambiguous fields | 2 |
| Partially extracted fields | 2 |
