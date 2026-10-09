#!/usr/bin/env python3
"""Live end-to-end tests via local n8n webhook and sqlite-backed API (no mock n8n)."""
import json,urllib.request,urllib.error,time,uuid,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
HOST="http://127.0.0.1:5679"
ENDPOINT=HOST+"/webhook/portfolio-waha-jobs-v1"
API="http://127.0.0.1:8767"
def get(url,timeout=8):
    with urllib.request.urlopen(url,timeout=timeout) as r:return json.load(r)
def post(body):
    data=json.dumps(body,ensure_ascii=False).encode("utf-8")
    req=urllib.request.Request(ENDPOINT,method="POST",data=data,headers={"Content-Type":"application/json"})
    try:
        with urllib.request.urlopen(req,timeout=35) as r:
            return r.status,json.load(r)
    except urllib.error.HTTPError as e:
        data=e.read().decode("utf-8","replace")
        try:return e.code,json.loads(data)
        except:return e.code,{"raw":data}
def fixture(mid,text,group="120300011122@g.us",event="message",**extra):
    msg={"id":mid,"from":group,"fromMe":False,"body":text}
    msg.update(extra)
    return {"event":event,"session":"portfolio-demo","payload":msg}
def must(c,err):
    if not c:raise AssertionError(err)
def main():
    for svc in (HOST+"/healthz",API+"/health"):
        try:print("CHECK",svc,get(svc),flush=True)
        except Exception as ex:
            if "healthz" not in svc:raise
            print("NOTE n8n health route",type(ex).__name__,flush=True)
    token=uuid.uuid4().hex[:8]
    english=fixture(f"eng-{token}",
       "We are hiring a freelance Camera Operator in Dubai for a corporate event on 15/10/2026. Pay AED 800 per day.")
    arabic=fixture(f"ar-{token}",
       "مطلوب مونتير في الشارقة لعمل حر يوم 16/10/2026، الأجر 700 درهم.")
    retry=fixture(f"retry-{token}",
       "Hiring a Production Assistant in Abu Dhabi on 17/10/2026. AED 650 per day.",
       test_retry=True)
    personal=fixture(f"personal-{token}",
       "Hello team, just confirming tomorrow's lunch in Dubai")
    incomplete=fixture(f"incomplete-{token}",
       "Hiring a freelance Video Editor. Please apply by email.")
    private=fixture(f"private-{token}",
       "Hiring a Camera Operator in Dubai. Pay AED 900.",group="direct-contact@c.us")
    before=get(API+"/stats")
    checks=[
      ("english_created",english,lambda status,r: r.get("state")=="submitted" and r.get("stored") is True),
      ("english_duplicate",english,lambda status,r: r.get("state")=="duplicate" and r.get("duplicate") is True),
      ("arabic_created",arabic,lambda status,r: r.get("state")=="submitted" and r.get("stored") is True),
      ("retry_503_then_created",retry,lambda status,r: r.get("state")=="submitted" and r.get("stored") is True),
      ("non_job_ignored",personal,lambda status,r:r.get("state")=="ignored"),
      ("missing_city_needs_review",incomplete,lambda status,r:r.get("state")=="needs_review" and "UAE_city" in r.get("missing_fields",[])),
      ("private_chat_ignored",private,lambda status,r:r.get("state")=="ignored" and r.get("reason")=="not_group_message")
    ]
    reports=[]
    for name,payload,check in checks:
        status,result=post(payload)
        ok=check(status,result)
        reports.append({"case":name,"http_status":status,"response":result,"passed":ok})
        print(("PASS" if ok else "FAIL"),name,"HTTP",status,
              json.dumps(result,ensure_ascii=False),flush=True)
    after=get(API+"/stats")
    jobs=get(API+"/jobs")["jobs"]
    tagged=[x for x in jobs if x["external_id"] in {x.get("response",{}).get("external_id") for x in reports}]
    must(all(r["passed"] for r in reports),"one or more end-to-end cases failed")
    must(after["jobs_created"]-before["jobs_created"]==3,
       f"expected 3 inserted jobs, delta={after['jobs_created']-before['jobs_created']}")
    must(after["transient_attempts"]-before["transient_attempts"]>=2,
       "transient 503 retry did not happen")
    must(any(x["language"]=="ar" and x["city"]=="Sharjah" for x in tagged),
       "Arabic Sharjah extraction absent")
    assert len(reports)==7
    evidence={"date_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
      "mode":"REAL n8n workflow POST -> Code -> IF -> HTTP Request -> SQLite API",
      "run_token":token,"test_count":7,"passed_count":7,"tests":reports,
      "before":before,"after":after,"jobs_this_run":tagged}
    (ROOT/"evidence").mkdir(exist_ok=True)
    out=ROOT/"evidence"/"integration_test_results.json"
    out.write_text(json.dumps(evidence,indent=2,ensure_ascii=False),encoding="utf-8")
    print("LIVE_E2E_7_OF_7_PASS",out,flush=True)
if __name__=="__main__":
    try:main()
    except Exception as e:
        print("LIVE_E2E_FAILED",repr(e),flush=True)
        sys.exit(1)
