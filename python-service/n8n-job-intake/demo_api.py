#!/usr/bin/env python3
"""Local demonstration API for the real n8n job-intake workflow. No cloud accounts."""
import json,os,sqlite3,threading,datetime
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path

BASE=Path(__file__).resolve().parent
DB=Path(os.environ.get("PORTFOLIO_SQLITE_PATH",str(BASE/"state"/"jobs.sqlite3")))
DB.parent.mkdir(parents=True,exist_ok=True)
PORT=int(os.environ.get("PORTFOLIO_API_PORT","8767"))
conn=sqlite3.connect(str(DB),check_same_thread=False,timeout=10)
conn.execute("PRAGMA journal_mode=WAL")
conn.execute("""CREATE TABLE IF NOT EXISTS jobs(
    external_id TEXT PRIMARY KEY, title TEXT NOT NULL, city TEXT NOT NULL,
    language TEXT, employment_type TEXT, pay TEXT, work_date TEXT,
    source TEXT, created_at TEXT NOT NULL)""")
conn.execute("""CREATE TABLE IF NOT EXISTS delivery_attempts(
    external_id TEXT PRIMARY KEY, attempts INTEGER NOT NULL DEFAULT 0)""")
conn.commit()
db_lock=threading.RLock()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
class Handler(BaseHTTPRequestHandler):
    server_version="PortfolioJobFormAPI/1.0"
    def log_message(self,fmt,*args):
        print(now(),self.address_string(),fmt%args,flush=True)
    def send(self,code,obj):
        b=json.dumps(obj,ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type","application/json; charset=utf-8")
        self.send_header("Cache-Control","no-store")
        self.send_header("Content-Length",str(len(b)))
        self.end_headers();self.wfile.write(b)
    def do_GET(self):
        if self.path=="/health":
            return self.send(200,{"ok":True,"service":"portfolio-job-form-api"})
        if self.path=="/stats":
            with db_lock:
                jobs=conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
                unique=conn.execute("SELECT COALESCE(SUM(attempts),0) FROM delivery_attempts").fetchone()[0]
            return self.send(200,{"jobs_created":jobs,"transient_attempts":unique})
        if self.path=="/jobs":
            with db_lock:
                rows=conn.execute("SELECT external_id,title,city,language,employment_type,pay,work_date,source,created_at FROM jobs ORDER BY created_at ASC").fetchall()
            fields=["external_id","title","city","language","employment_type","pay","work_date","source","created_at"]
            return self.send(200,{"jobs":[dict(zip(fields,r)) for r in rows]})
        return self.send(404,{"error":"not_found"})
    def do_POST(self):
        if self.path!="/jobs":return self.send(404,{"error":"not_found"})
        length=int(self.headers.get("Content-Length","0") or "0")
        if length<1 or length>20000:return self.send(413,{"error":"invalid_payload_size"})
        try:
            data=json.loads(self.rfile.read(length).decode("utf-8"))
        except Exception:return self.send(400,{"error":"invalid_json"})
        if not isinstance(data,dict):return self.send(400,{"error":"expected_job_object"})
        external_id=data.get("external_id")
        title=data.get("title")
        city=data.get("city")
        if not isinstance(external_id,str) or not (3<=len(external_id)<=200):
            return self.send(422,{"error":"external_id_required"})
        if not isinstance(title,str) or not (3<=len(title.strip())<=180):
            return self.send(422,{"error":"title_required"})
        if not isinstance(city,str) or not (2<=len(city.strip())<=100):
            return self.send(422,{"error":"city_required"})
        if data.get("test_retry") is True:
            with db_lock:
                prev=conn.execute("SELECT attempts FROM delivery_attempts WHERE external_id=?",(external_id,)).fetchone()
                n=(prev[0] if prev else 0)+1
                conn.execute("INSERT INTO delivery_attempts(external_id,attempts) VALUES (?,?) ON CONFLICT(external_id) DO UPDATE SET attempts=excluded.attempts",(external_id,n))
                conn.commit()
            if n==1:return self.send(503,{"error":"simulated_transient_failure","retryable":True})
        vals=(
            external_id,title.strip(),city.strip(),
            str(data.get("language") or ""),str(data.get("employment_type") or ""),
            str(data.get("pay") or ""),str(data.get("work_date") or ""),
            str(data.get("source") or "waha"),now())
        with db_lock:
            cur=conn.execute("""INSERT OR IGNORE INTO jobs
            (external_id,title,city,language,employment_type,pay,work_date,source,created_at)
            VALUES(?,?,?,?,?,?,?,?,?)""",vals)
            conn.commit()
        duplicate=cur.rowcount==0
        return self.send(200 if duplicate else 201,{"status":"duplicate" if duplicate else "created",
            "external_id":external_id,"duplicate":duplicate,"stored":True})
def main():
    server=ThreadingHTTPServer(("127.0.0.1",PORT),Handler)
    print("PORTFOLIO_DEMO_API_READY",f"http://127.0.0.1:{PORT}","DB",DB,flush=True)
    try:server.serve_forever(poll_interval=0.3)
    finally:
        server.server_close();conn.close()
if __name__=="__main__":main()
