"""Local read-only MVP. Bind to localhost; not a production server."""
import argparse
import html
import json
import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
from pathlib import Path

PAGE = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Nigeria Accountability</title><style>body{font:17px system-ui;background:#f4f7f6;color:#16342d;max-width:1050px;margin:50px auto;padding:20px}header{border-bottom:4px solid #168269;padding-bottom:24px}a{color:#00654d}article{background:white;padding:22px;margin:15px 0;border-radius:10px}input{padding:14px;width:65%;font:inherit}button{padding:14px;font:inherit}small{color:#54665f}pre{white-space:pre-wrap;overflow-wrap:anywhere}table{width:100%;text-align:left}td{padding:10px;border-bottom:1px solid #ddd}</style><header><small>FEDERAL PILOT · ALL SECTORS</small><h1>Nigeria Government Accountability Platform</h1><p>Follow the public record, from money to delivery.</p></header><p>Procurement records from BPP/NOCOPO via the Open Contracting Partnership. Records are source-reported and have not been independently verified. Missing data does not mean zero spending.</p>{body}</html>'''

def handler(database):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            u = urlparse(self.path)
            params = parse_qs(u.query)
            with sqlite3.connect(database) as db:
                db.row_factory = sqlite3.Row
                if u.path == '/health':
                    self.send(200, 'application/json', '{"status":"ok"}')
                    return
                if u.path == '/project':
                    row = db.execute('SELECT r.*,i.source_url,i.retrieved_at,i.sha256 FROM records r JOIN imports i ON i.id=r.import_id WHERE ocid=?', (params.get('ocid',[''])[0],)).fetchone()
                    if row is None:
                        self.send(404,'text/plain','Record not found'); return
                    e = html.escape
                    body = '<p><a href="/">← Explore</a></p><article><h2>'+e(row['title'])+'</h2><p>'+e(row['buyer'] or 'Agency unknown')+'</p><p>OCID: '+e(row['ocid'])+'</p><p>Source release date: '+e(row['release_date'] or 'Unknown')+'</p><table><tr><th>Type</th><th>Amount</th><th>Source field</th></tr>'
                    for a in db.execute('SELECT * FROM amounts WHERE ocid=?',(row['ocid'],)):
                        body += '<tr><td>'+e(a['kind'])+'</td><td>'+e(a['currency']+' '+a['amount'])+'</td><td>'+e(a['source_path'])+'</td></tr>'
                    body += '</table><p>Amounts are separate source entries; do not add budgets, awards, contracts and payments together. A procurement planning budget is not independently confirmed appropriation.</p><p>Citizen verification: unavailable. Government responsibility: buyer as reported; not independently confirmed.</p><p>Snapshot retrieved: '+e(row['retrieved_at'])+'</p><p>Source: '+e(row['source_url'])+'</p><details><summary>Original source record</summary><pre>'+e(json.dumps(json.loads(row['raw_json']),indent=2))+'</pre></details></article>'
                elif u.path == '/':
                    q = params.get('q',[''])[0][:200]
                    total = db.execute('SELECT count(*) FROM records').fetchone()[0]
                    rows = db.execute('SELECT ocid,title,buyer FROM records WHERE instr(lower(title || " " || coalesce(buyer,"")),lower(?))>0 ORDER BY title LIMIT 100',(q,)).fetchall()
                    from urllib.parse import quote
                    body = '<h2>Explore public procurement</h2><form><input name="q" aria-label="Search title or agency" placeholder="Search title or agency" value="'+html.escape(q,quote=True)+'"><button>Search</button></form><p>'+str(total)+' records imported · Showing up to 100 matches</p>'
                    for r in rows:
                        body += '<article><h3><a href="/project?ocid='+quote(r['ocid'],safe='')+'">'+html.escape(r['title'])+'</a></h3><small>'+html.escape(r['buyer'] or 'Agency unknown')+'</small></article>'
                else:
                    self.send(404,'text/plain','Not found'); return
            self.send(200,'text/html; charset=utf-8',PAGE.replace('{body}',body))
        def send(self, code, content_type, text):
            data = text.encode()
            self.send_response(code); self.send_header('Content-Type',content_type)
            self.send_header('Content-Length',str(len(data))); self.end_headers(); self.wfile.write(data)
    return Handler

if __name__ == '__main__':
    p=argparse.ArgumentParser(); p.add_argument('--db',default='data/platform.sqlite'); p.add_argument('--port',type=int,default=8000); a=p.parse_args()
    if not Path(a.db).exists(): p.error('Run the importer first')
    print(f'Open http://127.0.0.1:{a.port}',flush=True)
    HTTPServer(('127.0.0.1',a.port),handler(a.db)).serve_forever()
