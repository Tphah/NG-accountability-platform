# Initial data-source catalogue

Checked 16 October 2026 UTC.

| Source | Access verified | Use | Remaining checks |
|---|---|---|---|
| OCP registry, Nigeria BPP/NOCOPO: https://data.open-contracting.org/en/publication/64 | Registry page and 2026 gzip JSONL downloaded successfully | First ingestion source | Per-record scope, licence, dates and completeness |
| 2026 download: https://data.open-contracting.org/en/publication/64/download?name=2026.jsonl.gz | HTTP download and 257 JSONL records imported | Compiled contracting-process records | Source-defined year selection is not appropriation year |
| NOCOPO licence: https://nocopo.bpp.gov.ng/license | Verification attempt returned 502 | Reuse clearance | Confirm applicable dataset licence before republication; registry website CC BY notice does not establish dataset rights |
| Budget Office: https://budgetoffice.gov.ng/ | Candidate only in this implementation | Independent appropriations and implementation reports | Select and retrieve document, record licence, build parser, reconcile identifiers |
| GovSpend / Tracka | Not integrated | Potential expenditure / field-evidence partners | Confirm API, access and permission before integration |

The registry reports data through September 2026 and a 20 September retrieval. It documents JSONL as one compiled release per line and flags inconsistent dates, OCID prefixes and publication-policy gaps. These are source warnings, not findings of wrongdoing.

We preserve every raw record and label financial stages. Planning budgets from procurement data are not certified appropriation or expenditure. Payments are source transactions, not independently audited actual spending. Missing fields remain unknown.
