// Capture a genuine n8n editor canvas from an isolated ephemeral GitHub Actions instance.
// Never label a login/setup screen or synthetic diagram as an n8n workflow screenshot.
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require('playwright-core');

(async () => {
  const roots = ['/usr/bin/google-chrome','/usr/bin/google-chrome-stable','/usr/bin/chromium','/usr/bin/chromium-browser'];
  const executablePath = roots.find(p => fs.existsSync(p));
  if (!executablePath) throw Error('Chrome/Chromium binary not available on runner');
  const out = '/tmp/n8n-ci-evidence';
  fs.mkdirSync(out, {recursive:true});
  const browser = await chromium.launch({
    executablePath, headless:true,
    args:['--no-sandbox','--disable-dev-shm-usage','--disable-gpu']
  });
  try {
    const context = await browser.newContext({ viewport:{width:1760,height:1000},deviceScaleFactor:1 });
    const page = await context.newPage();
    const base='http://127.0.0.1:5679';
    const login = {
      email:'portfolio.native.demo@example.invalid',
      firstName:'Portfolio',
      lastName:'Demonstration',
      password:'LocalRunnerOnly!2026-Strong'
    };
    const api = await context.request.post(base+'/rest/owner/setup', {data:login, timeout:15000});
    console.log('OWNER_SETUP_HTTP_STATUS',api.status());
    await page.goto(base+'/workflow/portWAHAjobdemo1', {waitUntil:'domcontentloaded',timeout:30000});
    await page.waitForTimeout(5000);
    // Handle first-run login if REST setup returned a logged-out state.
    if (page.url().includes('/signin')) {
      const email = page.locator('input[type="email"]').first();
      const pass = page.locator('input[type="password"]').first();
      if(await email.count() && await pass.count()) {
        await email.fill(login.email);
        await pass.fill(login.password);
        await page.getByRole('button',{name:/sign in|log in/i}).first().click({timeout:10000});
        await page.goto(base+'/workflow/portWAHAjobdemo1',{waitUntil:'domcontentloaded',timeout:20000});
      }
    }
    // n8n's native editor is based on Vue Flow. Explicitly verify actual nodes rendered.
    const nodes=page.locator('.vue-flow__node');
    try {await nodes.first().waitFor({state:'visible',timeout:25000});}
    catch (err) {
      const diagnostics = {
        final_url:page.url(),
        page_title:await page.title(),
        rendered_node_count:await nodes.count(),
        body_excerpt:(await page.locator('body').innerText()).slice(0,600)
      };
      fs.writeFileSync(path.join(out,'editor_capture_diagnostics.json'),JSON.stringify(diagnostics,null,2));
      console.log('EDITOR_NOT_VERIFIED',JSON.stringify(diagnostics));
      throw Error('n8n editor node canvas was not rendered; no editor screenshot claimed');
    }
    const count=await nodes.count();
    console.log('NATIVE_EDITOR_NODES',count);
    if(count!==10)throw Error('Expected 10 actual nodes, got '+count);
    // Dismiss n8n's optional first-run checklist so the diagram is not obscured.
    const title=page.getByText('Production Checklist',{exact:true});
    if(await title.count()) {
      const header=title.first().locator('..');
      const candidates=header.locator('button');
      const n=await candidates.count();
      console.log('PRODUCTION_CHECKLIST_CLOSE_CANDIDATES',n);
      if(n) await candidates.last().click({timeout:3000}).catch(()=>{});
    }
    await page.waitForTimeout(600);
    await page.screenshot({path:path.join(out,'authentic_n8n_editor_10_nodes.png'),animations:'disabled',fullPage:false});
    const evidence={kind:'genuine_n8n_editor_screenshot',n8n_version:'2.42.6',node_count:count,
       generated_at_utc:new Date().toISOString(),isolated_test_environment:true,
       live_whatsapp:false,live_llm:false,production:false};
    fs.writeFileSync(path.join(out,'editor_capture_metadata.json'),JSON.stringify(evidence,null,2));
    console.log('AUTHENTIC_N8N_EDITOR_SCREENSHOT_CAPTURED',count);
  } finally {
    await browser.close();
  }
})().catch(error=>{console.error('NATIVE_EDITOR_CAPTURE_FAILED',error.stack||String(error));process.exitCode=1;});