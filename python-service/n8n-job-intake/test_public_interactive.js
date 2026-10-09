const vm=require('node:vm');
const assert=require('node:assert/strict');
const base='https://mrwanahmedx.github.io/python-service/n8n-job-intake/';
async function get(url){
 const response=await fetch(url,{cache:'no-store'});
 if(!response.ok)throw Error('HTTP '+response.status+' '+url);
 return await response.text();
}
async function main(){
 const html=await get(base);
 assert.match(html,/<title>n8n Bilingual Job Intake/);
 const match=html.match(/<script>\s*([\s\S]*?)\s*<\/script>/i);
 assert.ok(match&&match[1].length>200,'Inline interactive code missing');
 const controls={};
 for(const id of ['msg','output','status','example-en','example-ar','example-invalid','run']){
  controls[id]={id,textContent:'',value:'',listeners:{},
   addEventListener(ev,fn){this.listeners[ev]=fn;},
   click(){assert.ok(this.listeners.click,'No click handler '+id);this.listeners.click();}};
 }
 controls.msg.value='Hiring a freelance Camera Operator in Dubai on 15/10/2026. Pay AED 800.';
 const ctx={
  document:{getElementById:(id)=>controls[id]},
  fetch:async(relative,opt)=>{
   const url=new URL(relative,base).toString();
   const text=await get(url);
   return {ok:true,status:200,json:async()=>JSON.parse(text)};
  },
  Function,console
 };
 vm.runInNewContext(match[1],ctx,{timeout:2000});
 let waited=0;
 while(!controls.status.textContent && waited<80){
  await new Promise(r=>setTimeout(r,100));waited++;
 }
 const result=()=>JSON.parse(controls.output.textContent);
 const en=result();
 assert.equal(en.state,'ready');assert.equal(en.job.city,'Dubai');assert.equal(en.job.title,'Camera Operator');
 controls['example-ar'].click();
 const ar=result();
 assert.equal(ar.state,'ready');assert.equal(ar.job.city,'Sharjah');assert.equal(ar.job.language,'ar');
 controls['example-invalid'].click();
 const missing=result();
 assert.equal(missing.state,'needs_review');
 assert.ok(missing.missing_fields.includes('UAE_city'));
 controls['example-en'].click();
 const again=result();
 assert.equal(again.job.city,'Dubai');
 console.log('PUBLIC_INTERACTIVE_4_OF_4_PASS');
 console.log('PAGE',base);
 console.log('CODE_SOURCE',base+'workflow_n8n.json');
 console.log('OUTPUT_STATES',JSON.stringify([en.state,ar.state,missing.state,again.state]));
}
main().catch(e=>{console.error('FAILED_PUBLIC_INTERACTIVE',e);process.exit(1);});
