# MVP implementation backlog

Federal pilot · all sectors · AI-assisted development · initial software budget under AUD 1,000.

## Delivered
- First real-data procurement import, provenance, local database and read-only explorer.
- Import integrity tests and reproducible run instructions.

## Next sprint
1. Confirm dataset republication licence with the publisher and document permission.
2. Validate agency and federal scope; quarantine uncertain records rather than infer scope.
3. Add immutable record revisions, stale-source protection and data-quality review queue.
4. Obtain one official federal appropriation document; extract budget codes with page references and human review.
5. Introduce canonical projects and reviewed links between appropriation, procurement and payment records. Keep uncertain matches separate.
6. Add PostgreSQL migrations and hosted application/API; establish an explicit monthly cost ceiling before paid services.
7. Add pagination, agency/year filters and accessible mobile layouts; user-test with citizens and CSOs.
8. Design private citizen submissions, consent, abuse controls and moderation before accepting evidence.
9. Verify agency grievance routes and dates before adding complaint guidance.

Public launch gate: licence confirmed, scope reviewed, source-linked data reviewed, production security and backups configured. No citizen identity data or credentials in Git.
