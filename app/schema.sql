PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS imports (
 id INTEGER PRIMARY KEY, sha256 TEXT NOT NULL UNIQUE, source_url TEXT NOT NULL,
 retrieved_at TEXT NOT NULL, record_count INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS records (
 ocid TEXT PRIMARY KEY, title TEXT NOT NULL, buyer TEXT,
 release_date TEXT, import_id INTEGER NOT NULL REFERENCES imports(id),
 raw_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS amounts (
 ocid TEXT NOT NULL REFERENCES records(ocid) ON DELETE CASCADE,
 kind TEXT NOT NULL CHECK(kind IN ('planning_budget','award','contract','transaction')),
 item_id TEXT NOT NULL, amount TEXT NOT NULL, currency TEXT NOT NULL,
 source_path TEXT NOT NULL, PRIMARY KEY(ocid,kind,item_id)
);
