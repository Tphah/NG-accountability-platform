# Nigeria Government Accountability Platform

A federal, all-sector civic-data MVP connecting public procurement records to their sources.

## Run locally

Requires Python 3.11+; no packages, accounts or paid services required.

```bash
python -m app.import_ocds
python -m app.server
```

Open http://127.0.0.1:8000. Search by title or agency, open a record, inspect the separate financial entries and original JSON.

To import an existing snapshot:

```bash
python -m app.import_ocds --input path/to/snapshot.jsonl.gz --source-url https://example.org/original-download
python -m unittest discover -s tests -v
```

## What is implemented

- OCDS compiled-release JSONL / gzip importer, SHA-256 snapshot identity, timestamp and source URL.
- Atomic import, duplicate-OCID rejection, repeat-file detection and record updates.
- SQLite schema retaining raw source JSON and exact decimal amounts as text.
- Separate planning budgets, awards, contracts and transactions, with JSON source paths.
- Local read-only search and record pages. No AI guesses, inferred completion scores or corruption allegations.

A contracting process is not necessarily a single physical project. The 2026 download is a source-defined slice, not a verified list of 2026 appropriations. Buyer names are source-reported agencies, not independently verified responsibility assignments.

## Data and limitations

See [source catalogue](docs/sources.md), [first import report](docs/first-import.md), and [implementation backlog](docs/backlog.md).

Downloaded data and the database are ignored by Git. Source licence verification is outstanding; this repository publishes the importer and aggregate validation results, not the source dataset. Re-run the importer locally to populate the MVP. Downloads can change; compare snapshot hashes.

This is a local development foundation, not a deployed production service. Government budget-document reconciliation, federal-scope validation per record, citizen evidence, complaint routing, authentication, moderation, PostgreSQL and public hosting remain future work. Do not expose the development HTTP server publicly.

The database stores the latest imported version per OCID. Imports retain snapshot metadata, but full historical versions require retaining source snapshots outside Git. Import newer snapshots in chronological order; stale-snapshot rejection is not yet implemented.
