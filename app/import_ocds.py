"""Import a reviewed OCDS compiled-release JSONL snapshot. No third-party dependencies."""
import argparse
import gzip
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.request import urlopen

CATALOGUE = 'https://data.open-contracting.org/en/publication/64'
DEFAULT_URL = CATALOGUE + '/download?name=2026.jsonl.gz'

def connect(path):
    db = sqlite3.connect(path)
    db.executescript(Path(__file__).with_name('schema.sql').read_text())
    return db

def import_file(db, path, source_url, retrieved_at=None):
    payload = Path(path).read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    existing = db.execute('SELECT record_count FROM imports WHERE sha256=?', (digest,)).fetchone()
    if existing:
        return {'records': existing[0], 'sha256': digest, 'skipped': True}
    content = gzip.decompress(payload) if payload[:2] == b'\x1f\x8b' else payload
    count = 0
    seen = set()
    with db:
        cur = db.execute('INSERT INTO imports(sha256,source_url,retrieved_at) VALUES (?,?,?)',
                         (digest, source_url, retrieved_at or datetime.now(timezone.utc).isoformat()))
        import_id = cur.lastrowid
        for line_no, line in enumerate(content.decode('utf-8-sig').splitlines(), 1):
            if not line.strip():
                continue
            r = json.loads(line, parse_float=Decimal)
            ocid = r.get('ocid')
            if not isinstance(ocid, str) or not ocid.strip() or ocid in seen:
                raise ValueError(f'Line {line_no}: missing or duplicate OCID')
            seen.add(ocid)
            planning = r.get('planning') or {}
            budget = planning.get('budget') or {}
            tender = r.get('tender') or {}
            title = tender.get('title') or budget.get('project') or budget.get('description') or ocid
            # Raw text preserves the original numeric precision and every unmodelled field.
            db.execute('INSERT INTO records VALUES (?,?,?,?,?,?) ON CONFLICT(ocid) DO UPDATE SET title=excluded.title,buyer=excluded.buyer,release_date=excluded.release_date,import_id=excluded.import_id,raw_json=excluded.raw_json',
                       (ocid, title, (r.get('buyer') or {}).get('name'), r.get('date'), import_id, line))
            db.execute('DELETE FROM amounts WHERE ocid=?', (ocid,))
            def money(kind, key, value, pointer):
                if not value or value.get('amount') is None:
                    return
                try:
                    amount = Decimal(str(value['amount']))
                except InvalidOperation as exc:
                    raise ValueError(f'{ocid}: invalid money at {pointer}') from exc
                currency = value.get('currency')
                if not amount.is_finite() or not isinstance(currency, str) or len(currency) != 3:
                    raise ValueError(f'{ocid}: invalid amount/currency at {pointer}')
                db.execute('INSERT INTO amounts VALUES (?,?,?,?,?,?)',
                           (ocid, kind, str(key), str(amount), currency, pointer))
            money('planning_budget', 'budget', budget.get('amount'), '/planning/budget/amount')
            for group, kind in [('awards','award'), ('contracts','contract')]:
                for i, item in enumerate(r.get(group) or []):
                    money(kind, i, item.get('value'), f'/{group}/{i}/value')
                    if group == 'contracts':
                        for j, tx in enumerate((item.get('implementation') or {}).get('transactions') or []):
                            money('transaction', f'{i}:{j}', tx.get('value'), f'/contracts/{i}/implementation/transactions/{j}/value')
            count += 1
        if count == 0:
            raise ValueError('Snapshot contains no records')
        db.execute('UPDATE imports SET record_count=? WHERE id=?', (count, import_id))
    return {'records': count, 'sha256': digest, 'skipped': False}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, help='Existing .jsonl or .jsonl.gz snapshot')
    parser.add_argument('--source-url', default=DEFAULT_URL)
    parser.add_argument('--db', default='data/platform.sqlite')
    args = parser.parse_args()
    Path(args.db).parent.mkdir(parents=True, exist_ok=True)
    source = args.input
    if source is None:
        source = Path('data/nocopo-2026.jsonl.gz')
        with urlopen(args.source_url, timeout=60) as response:
            source.write_bytes(response.read())
    with connect(args.db) as db:
        print(json.dumps(import_file(db, source, args.source_url), indent=2))

if __name__ == '__main__':
    main()
