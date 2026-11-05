"""Seed and read historical presidential campaign commitments."""
import argparse
import json
import sqlite3
from contextlib import closing
from pathlib import Path

SEED = Path(__file__).resolve().parent / 'seeds/buhari-2019.json'
SCHEMA = """
CREATE TABLE IF NOT EXISTS executive_terms (
    id TEXT PRIMARY KEY,
    metadata TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS campaign_commitments (
    term_id TEXT NOT NULL REFERENCES executive_terms(id),
    id TEXT NOT NULL,
    sector TEXT NOT NULL,
    title TEXT NOT NULL,
    target INTEGER NOT NULL CHECK (target > 0),
    unit TEXT NOT NULL,
    source_locator TEXT NOT NULL,
    PRIMARY KEY (term_id, id)
);
"""

def seed(db):
    snapshot = json.loads(SEED.read_text(encoding='utf-8'))
    commitments = snapshot.pop('commitments')
    db.execute('PRAGMA foreign_keys=ON')
    db.executescript(SCHEMA)
    with db:
        db.execute('INSERT INTO executive_terms VALUES (?, ?) ON CONFLICT(id) DO UPDATE SET metadata=excluded.metadata',
                   (snapshot['id'], json.dumps(snapshot)))
        db.execute('DELETE FROM campaign_commitments WHERE term_id=?', (snapshot['id'],))
        db.executemany('INSERT INTO campaign_commitments VALUES (?, ?, ?, ?, ?, ?, ?)', [
            (snapshot['id'], *(c[k] for k in ('id', 'sector', 'title', 'target', 'unit', 'source_locator')))
            for c in commitments
        ])
    return len(commitments)

def read_term(db, term_id):
    row = db.execute('SELECT metadata FROM executive_terms WHERE id=?', (term_id,)).fetchone()
    if row is None:
        return None
    result = json.loads(row[0])
    result['commitments'] = [
        dict(id=c[0], sector=c[1], title=c[2], target=c[3], unit=c[4],
             source_locator=c[5], assessment_status='not_assessed')
        for c in db.execute(
            'SELECT id, sector, title, target, unit, source_locator FROM campaign_commitments WHERE term_id=? ORDER BY sector, id',
            (term_id,))
    ]
    return result

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--db', type=Path, default=Path('data/platform.sqlite'))
    args = p.parse_args()
    args.db.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(args.db)) as db:
        print(f'Seeded {seed(db)} campaign commitments.')
