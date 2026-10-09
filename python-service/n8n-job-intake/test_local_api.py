import urllib.request,json,uuid
base='http://127.0.0.1:8767'
def get(path):
 with urllib.request.urlopen(base+path,timeout=6) as r:return json.load(r)
def post(obj):
 data=json.dumps(obj).encode('utf-8')
 req=urllib.request.Request(base+'/jobs',data=data,method='POST',headers={'Content-Type':'application/json'})
 try:
  with urllib.request.urlopen(req,timeout=6) as r:return r.status,json.load(r)
 except urllib.error.HTTPError as e:return e.code,json.load(e)
token='api-only-'+uuid.uuid4().hex[:12]
obj=dict(external_id=token,title='Demo Camera Operator',city='Dubai',language='en',employment_type='freelance',pay='AED 300',source='local-test')
a=post(obj);b=post(obj)
assert a[0]==201 and a[1]['stored'] and not a[1]['duplicate']
assert b[0]==200 and b[1]['duplicate']
other=dict(obj,external_id=token+'retry',test_retry=True)
c=post(other);d=post(other)
assert c[0]==503 and d[0]==201
print('API_UNIT_4_OF_4_PASS','HEALTH',get('/health'),'STATS',get('/stats'),'DUPLICATE',b[1],'RETRY',c[1],flush=True)
