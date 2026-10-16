# First import validation

Run: 16 October 2026 UTC. Download: OCP Nigeria BPP/NOCOPO 2026 JSONL gzip.

- Compressed bytes: 60,153
- SHA-256: `b397100f5f370831ad62222500e206c0f474d5477c129afcb87c46a86ce56db8`
- Contracting-process records: **257**
- Planning-budget entries: **257**
- Award entries: **54**
- Contract entries: **26**
- Implementation transaction entries: **12**

Import was atomic and successful. Unit checks cover exact decimal storage, zero values, financial-stage separation, repeat imports, record replacement, invalid-record rollback and duplicate OCID rejection. Local HTTP smoke checks cover search, detail, missing record and health endpoints.

No aggregate spending total is reported: financial stages overlap. This is not national coverage, independent project verification or a completed appropriation-to-payment reconciliation. Source data is deliberately excluded from the public repository while reuse terms remain unconfirmed.
