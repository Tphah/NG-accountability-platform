import json
import tempfile
import unittest
from pathlib import Path
from app.import_ocds import connect, import_file

class ImportTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'input.jsonl'; self.db=connect(':memory:'); self.addCleanup(self.db.close)
    def write(self, records):
        self.path.write_text('\n'.join(json.dumps(r) for r in records))
    def test_types_precision_and_idempotence(self):
        self.path.write_text('{"ocid":"test-1","planning":{"budget":{"amount":{"amount":123.45,"currency":"NGN"}}},"contracts":[{"value":{"amount":100,"currency":"NGN"},"implementation":{"transactions":[{"value":{"amount":0,"currency":"NGN"}}]}}]}')
        self.assertEqual(import_file(self.db,self.path,'https://example.org')['records'],1)
        self.assertTrue(import_file(self.db,self.path,'https://example.org')['skipped'])
        self.assertEqual(dict(self.db.execute('SELECT kind,amount FROM amounts')),{'planning_budget':'123.45','contract':'100','transaction':'0'})
    def test_invalid_snapshot_rolls_back(self):
        self.write([{'ocid':'valid'},{}])
        with self.assertRaises(ValueError): import_file(self.db,self.path,'source')
        self.assertEqual(self.db.execute('SELECT count(*) FROM records').fetchone()[0],0)
    def test_update_replaces_amounts(self):
        self.write([{'ocid':'one','contracts':[{'value':{'amount':10,'currency':'NGN'}}]}]); import_file(self.db,self.path,'source')
        self.write([{'ocid':'one','tender':{'title':'Updated'}}]); import_file(self.db,self.path,'source')
        self.assertEqual(self.db.execute('SELECT count(*) FROM records').fetchone()[0],1)
        self.assertEqual(self.db.execute('SELECT count(*) FROM amounts').fetchone()[0],0)
    def test_duplicate_rejected(self):
        self.write([{'ocid':'one'},{'ocid':'one'}])
        with self.assertRaises(ValueError): import_file(self.db,self.path,'source')

if __name__=='__main__': unittest.main()
