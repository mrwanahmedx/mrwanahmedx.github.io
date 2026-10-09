// Validate the exact embedded n8n Code-node JavaScript and workflow wiring, without a browser.
const fs = require('fs');
const assert = require('assert');
const path = require('path');
const workflow=JSON.parse(fs.readFileSync(path.join(__dirname,'workflow_n8n.json'),'utf8'));
const nameMap=Object.fromEntries(workflow.nodes.map(n=>[n.name,n]));
const expected=['WAHA Incoming Message','Normalize WAHA Payload','Classify and Extract Job',
'Complete Job Details?','Submit to Demo Job API','Prepare Submission Receipt',
'Respond Accepted','Prepare Error Receipt','Respond API Failure','Respond Ignored or Review'];
assert.deepEqual(Object.keys(nameMap).sort(),expected.slice().sort());
assert.equal(new Set(workflow.nodes.map(n=>n.id)).size,10);
let edges=0;for(const [from,n] of Object.entries(workflow.connections)){
 assert.ok(nameMap[from],from);
 for(const outputs of n.main||[])for(const x of outputs){
  assert.ok(nameMap[x.node],x.node);edges++;
 }
}
assert.equal(edges,9); // normalize, extract, 2 IF, 2 request, receipt/error and responses
const func=n=>new Function('$input',nameMap[n].parameters.jsCode);
const normalize=func('Normalize WAHA Payload');
const classify=func('Classify and Extract Job');
const payload=(id,text,chat='123456@g.us',more={})=>({body:{
 event:'message',session:'demo',payload:{id,from:chat,fromMe:false,body:text,...more}}});
function run(v){
 const n=normalize({first:()=>({json:v})})[0].json;
 const result=classify({first:()=>({json:n})})[0].json;
 return {norm:n,result};
}
const en=payload('english-001','Hiring a freelance Camera Operator in Dubai for a shoot on 15/10/2026. Pay AED 800.');
const a=payload('arabic-001','مطلوب مونتير في الشارقة يوم 16/10/2026 الأجر 700 درهم.');
const r1=run(en),r2=run(en);
assert.deepEqual(r1.norm.external_id,r2.norm.external_id);
assert.equal(r1.result.state,'ready');
assert.equal(r1.result.job.title,'Camera Operator');
assert.equal(r1.result.job.city,'Dubai');
assert.equal(r1.result.job.pay,'AED 800');
assert.equal(run(a).result.state,'ready');
assert.equal(run(a).result.job.language,'ar');
assert.equal(run(a).result.job.city,'Sharjah');
assert.equal(run(payload('bad1','Just checking lunch in Dubai')).result.state,'ignored');
assert.equal(run(payload('bad2','Hiring a Video Editor next week')).result.state,'needs_review');
assert.equal(run(payload('bad3','Hiring a Camera Operator in Dubai','private@c.us')).result.reason,'not_group_message');
assert.equal(run(payload('bad4','Hiring a Camera Operator in Dubai','123@g.us',{fromMe:true})).result.reason,'own_message');
const ret=run(payload('retry','Hiring a Production Assistant in Abu Dhabi. AED 500.',undefined,{test_retry:true}));
assert.equal(ret.result.state,'ready');assert.equal(ret.result.job.test_retry,true);
console.log('NODE_CODE_TESTS_PASS: 10 structural nodes; '+edges+' graph edges; English & Arabic extraction; idempotent ID; group-only filtering; missing fields; demo transient retry flag.');
