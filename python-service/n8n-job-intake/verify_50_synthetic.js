// Offline verification of the actual embedded n8n Code nodes on 50 original synthetic messages.
// This does NOT prove the native n8n webhook or WhatsApp integration works.
const fs=require('fs'),path=require('path'),assert=require('assert');
const root=__dirname,wf=JSON.parse(fs.readFileSync(path.join(root,'workflow_n8n.json'),'utf8'));
const byName=Object.fromEntries(wf.nodes.map(n=>[n.name,n]));
const norm=new Function('$input',byName['Normalize WAHA Payload'].parameters.jsCode);
const extract=new Function('$input',byName['Classify and Extract Job'].parameters.jsCode);
const messages=[
['en01','Hiring Camera Operator in Dubai. AED 800.', 'ready','Dubai','en'],
['en02','Need a Video Editor in Abu Dhabi, AED 500 per day.', 'ready','Abu Dhabi','en'],
['en03','We are looking for a Production Assistant in Sharjah.', 'ready','Sharjah','en'],
['en04','Seeking Photographer in Ajman for an event.', 'ready','Ajman','en'],
['en05','Hiring Sound Engineer in Al Ain today.', 'ready','Al Ain','en'],
['en06','Need a Videographer in Ras Al Khaimah for a shoot.', 'ready','Ras Al Khaimah','en'],
['en07','Job opening: Event Coordinator in Dubai.', 'ready','Dubai','en'],
['en08','Hiring Lighting Technician in Abu Dhabi.', 'ready','Abu Dhabi','en'],
['en09','We are looking for Motion Graphics Designer in Dubai.', 'ready','Dubai','en'],
['en10','Casting crew: need a cameraman in Sharjah.', 'ready','Sharjah','en'],
['en11','Hiring freelance Film Editor in Dubai.', 'ready','Dubai','en'],
['en12','Need a production runner in Ajman.', 'ready','Ajman','en'],
['en13','Seeking audio engineer in Abu Dhabi.', 'ready','Abu Dhabi','en'],
['en14','Hiring a gaffer in Dubai.', 'ready','Dubai','en'],
['en15','Looking for an event assistant in Sharjah.', 'ready','Sharjah','en'],
['en16','Hiring a camera person in Dubai AED 2k/day.', 'ready','Dubai','en'],
['en17','Looking for a photographer in Dubai, 2k/day.', 'ready','Dubai','en'],
['ar01','مطلوب مونتير في دبي', 'ready','Dubai','ar'],
['ar02','مطلوب مصور في أبو ظبي', 'ready','Abu Dhabi','ar'],
['ar03','فرصة عمل لمساعد إنتاج في الشارقة', 'ready','Sharjah','ar'],
['ar04','نبحث عن مهندس صوت في عجمان', 'ready','Ajman','ar'],
['ar05','مطلوب مصور فيديو في العين', 'ready','Al Ain','ar'],
['ar06','مطلوب مونتير في رأس الخيمة', 'ready','Ras Al Khaimah','ar'],
['ar07','وظيفة منسق فعاليات في دبي', 'ready','Dubai','ar'],
['ar08','محتاجين مصور في الشارقة', 'ready','Sharjah','ar'],
['ar09','توظيف مهندس صوت في دبي', 'ready','Dubai','ar'],
['ar10','نبحث عن مونتير في ابوظبي', 'ready','Abu Dhabi','ar'],
['ar11','مطلوب مساعد انتاج في عجمان', 'ready','Ajman','ar'],
['ar12','مطلوب مصور كاميرا مان في دبي', 'ready','Dubai','ar'],
['ar13','فرصة عمل لمونتير في العين', 'ready','Al Ain','ar'],
['ar14','مطلوب مصور في رأس الخيمة', 'ready','Ras Al Khaimah','ar'],
['ar15','نبحث عن منسق فعاليات في الشارقة', 'ready','Sharjah','ar'],
['ar16','مطلوب مونتير بدبي الأجر ٢٠٠٠ درهم', 'ready','Dubai','ar'],
['ar17','مطلوب مصور في دبي أجر 2k/day', 'ready','Dubai','ar'],
['no01','Good morning team everyone', 'ignored','','en'],
['no02','صباح الخير للجميع', 'ignored','','ar'],
['no03','No job openings this week Dubai', 'ignored','','en'],
['no04','Looking for an apartment for rent in Dubai', 'ignored','','en'],
['no05','إعلان بيع سيارة في دبي', 'ignored','','ar'],
['no06','Anyone know a photographer in Dubai?', 'ignored','','en'],
['no07','Hiring lunch catering? Just checking lunch in Dubai', 'ignored','','en'],
['no08','غير مطلوب موظفين الآن', 'ignored','','ar'],
['rv01','Hiring videographer for tomorrow', 'needs_review','','en'],
['rv02','مطلوب مونتير بشكل عاجل', 'needs_review','','ar'],
['rv03','Hiring crew in Dubai next week', 'needs_review','Dubai','en'],
['rv04','نبحث عن موظفين في دبي', 'needs_review','Dubai','ar'],
['rv05','Need camera operator', 'needs_review','','en'],
['rv06','مطلوب مصور سريعاً', 'needs_review','','ar'],
['rv07','Hiring video editor in UAE', 'needs_review','','en'],
['rv08','مطلوب عامل تصوير بدبي', 'needs_review','Dubai','ar']
];
assert.equal(messages.length,50,'must test exactly fifty messages');
let passed=0; const details=[];
messages.forEach((t,i)=>{
 const [id,message,expectedState,expectedCity,expectedLanguage]=t;
 const incoming={body:{event:'message',session:'portfolio-demo',payload:{id,from:'120300011122@g.us',body:message,fromMe:false}}};
 const n=norm({first:()=>({json:incoming})})[0].json;
 const r=extract({first:()=>({json:n})})[0].json;
 const actualCity=r.job?.city||'';
 const actualLanguage=r.job?.language||r.language||'';
 const problems=[];
 if(r.state!==expectedState)problems.push('state='+r.state+' expected='+expectedState);
 if(expectedState==='ready' && actualCity!==expectedCity)problems.push('city='+actualCity+' expected='+expectedCity);
 if(expectedState!=='ignored' && actualLanguage!==expectedLanguage)problems.push('language='+actualLanguage+' expected='+expectedLanguage);
 if((id==='en16'||id==='en17'||id==='ar17') && !/2k\/day/i.test(r.job?.pay||''))problems.push('2k/day pay not extracted');
 if(id==='ar16' && !/2000/.test(r.job?.pay||''))problems.push('Arabic numerals not normalized');
 const ok=problems.length===0;if(ok)passed++;
 details.push({id,expectedState,actualState:r.state,expectedCity,actualCity,ok,problems,example:['en01','ar02','en16','ar16','no02','rv02'].includes(id)?{input:message,output:r}:undefined});
});
const result={date_utc:new Date().toISOString(),verification_level:'embedded_code_nodes_only_not_native_n8n',synthetic:true,test_count:messages.length,passed,failed:messages.length-passed,failures:details.filter(x=>!x.ok),selected_examples:details.filter(x=>x.example).map(x=>({id:x.id,...x.example}))};
const ev=path.join(root,'evidence');fs.mkdirSync(ev,{recursive:true});
fs.writeFileSync(path.join(ev,'synthetic_50_code_node_results.json'),JSON.stringify(result,null,2));
console.log('EMBEDDED_CODE_50_CASES',passed,'/',messages.length,'PASS');
result.failures.forEach(x=>console.log('FAIL',x.id,x.problems.join('; ')));
if(passed!==messages.length)process.exitCode=1;
