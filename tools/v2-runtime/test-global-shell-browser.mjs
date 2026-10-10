/** Isolated Phase3 browser regression. Never targets staging or production. */
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
const require = createRequire(path.resolve(process.env.V2_QA_MODULES || '.artifacts/v2-phase3-20260905/qa/package.json'));
const { chromium } = require('playwright');
const { default: AxeBuilder } = require('@axe-core/playwright');
const base = 'http://127.0.0.1:18303';
const out = path.resolve('.artifacts/v2-phase3-20260905');
const browser = await chromium.launch({headless:true});
const context = await browser.newContext({viewport:{width:1440,height:1000}});
const blockedExternal=new Set();
await context.route('**/*',route=>{const url=route.request().url();if(new URL(url).origin===base||url.startsWith('data:'))return route.continue();blockedExternal.add(url);return route.abort();});
await context.addInitScript(()=>{
 window.__p3LongTasks=[];
 if(PerformanceObserver.supportedEntryTypes.includes('longtask'))new PerformanceObserver(list=>window.__p3LongTasks.push(...list.getEntries().map(e=>({start:e.startTime,duration:e.duration})))).observe({type:'longtask',buffered:true});
});
const page=await context.newPage();page.setDefaultTimeout(15000);
const evidence={routes:[],responsive:[],a11y:[],console:[],httpErrors:[],requests:0,failures:[],interactions:[]};
page.on('console',msg=>{if(msg.type()==='error')evidence.console.push(msg.text());});
page.on('pageerror',e=>evidence.console.push(e.message));
page.on('request',()=>evidence.requests++);
page.on('response',r=>{if(r.status()>=400)evidence.httpErrors.push({url:r.url(),status:r.status()});});
page.on('requestfailed',r=>evidence.failures.push({url:r.url(),error:r.failure()?.errorText}));
const go=async route=>{const r=await page.goto(base+route,{waitUntil:'load'});assert.equal(r.status(),200,route);await page.evaluate(()=>document.fonts.ready);};
const shot=async name=>{
 await page.waitForFunction(()=>[...document.images].filter(e=>{const r=e.getBoundingClientRect();const s=getComputedStyle(e);return r.width&&r.height&&r.bottom>0&&r.top<innerHeight&&r.right>0&&r.left<innerWidth&&s.visibility!=='hidden'&&s.display!=='none';}).every(e=>e.complete&&e.naturalWidth>0));
 await page.evaluate(async()=>{await document.fonts.ready;await Promise.all([...document.images].filter(e=>e.complete&&e.naturalWidth).map(e=>e.decode().catch(()=>{})));});
 await page.screenshot({path:path.join(out,'final-'+name+'.png'),animations:'disabled'});};
const metrics=()=>page.evaluate(()=>({width:innerWidth,height:innerHeight,scrollWidth:document.documentElement.scrollWidth,h1:document.querySelectorAll('main h1').length,broken:[...document.images].filter(e=>e.complete&&!e.naturalWidth&&e.getAttribute('src')).map(e=>e.getAttribute('src')),longTasks:window.__p3LongTasks}));
const axe=async (name,include)=>{let a=new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa','wcag22aa']);if(include)a=a.include(include);const r=await a.analyze();evidence.a11y.push({name,violations:r.violations.map(v=>({id:v.id,impact:v.impact,description:v.description,nodes:v.nodes.map(n=>({target:n.target,summary:n.failureSummary}))}))});};
try {
 for(const width of [1440,768,390]){
  await page.setViewportSize({width,height:width<768?844:1000});
  for(const [name,url] of [['home','/'],['pdp','/product/sg-005/'],['approved-pdp','/product/br-006/'],['rejected-pdp','/product/br-003/'],['missing-pdp','/product/br-002/'],['account','/my-account/'],['search-results','/?s=rose']]){
   await go(url);await shot(name+'-'+width);const m=await metrics();evidence.routes.push({name,...m});assert.equal(m.width,width);assert.equal(m.scrollWidth,width,name+' overflow');await shot(name+'-'+width);
   if(width===390&&['account','search-results'].includes(name))await axe(name);
  }
  await go('/');
  await page.locator('[data-sr2-menu]').click();await page.waitForFunction(()=>document.body.classList.contains('sr2-nav-open'));await shot('nav-'+width);await axe('nav-'+width,'[data-site-header]');
  await page.locator('[data-sr2-nav] [data-search-open]').click();assert(await page.locator('#sr2-search-dialog').evaluate(e=>e.open));assert.equal(await page.locator('dialog[open]').count(),1);await shot('search-'+width);await axe('search-'+width,'#sr2-search-dialog');await page.keyboard.press('Escape');assert(await page.locator('[data-sr2-menu]').evaluate(e=>e===document.activeElement));
  await page.locator('[data-bag-open]').click();await shot('bag-empty-'+width);await axe('bag-empty-'+width,'#sr2-bag-dialog');await page.keyboard.press('Escape');
  await page.locator('.sr2-house-footer').scrollIntoViewIfNeeded();await shot('footer-'+width);await axe('footer-'+width,'.sr2-house-footer');
 }
 await go('/');
 for(const width of [320,360,375,390,414,768,1024,1280,1440,1728]){
  await page.setViewportSize({width,height:width<768?844:1000});
  for(const state of ['home','nav','search','bag']){
   if(state==='nav')await page.locator('[data-sr2-menu]').click();
   if(state==='search')await page.locator('[data-sr2-nav] [data-search-open]').click();
   if(state==='bag'){await page.keyboard.press('Escape');await page.locator('[data-bag-open]').click();}
   const m=await metrics();assert.equal(m.width,width);assert.equal(m.scrollWidth,width,state+' overflow');
   const dialog=await page.locator('dialog[open]').evaluateAll(es=>es.map(e=>({id:e.id,width:e.getBoundingClientRect().width,scroll:e.scrollWidth,client:e.clientWidth})));
   assert(dialog.every(d=>d.scroll<=d.client+1),state+' internal overflow');evidence.responsive.push({state,width,height:m.height,scrollWidth:m.scrollWidth,dialog});
  }
  await page.keyboard.press('Escape');assert.equal(await page.evaluate(()=>document.body.style.position),'');
 }
 // Real native Woo variation -> mini-cart -> cart -> checkout; never submit payment.
 await page.setViewportSize({width:390,height:844});await go('/product/sg-005/');
 await page.getByRole('combobox',{name:'Size',exact:true}).selectOption('M');
 const variation=await page.locator('input.variation_id').inputValue();assert(Number(variation)>0);
 await page.getByRole('button',{name:'Add to cart',exact:true}).click();await page.waitForLoadState('load');
 await page.locator('[data-bag-open]').click();await page.locator('#sr2-bag-dialog .woocommerce-mini-cart-item').waitFor();
 const item=await page.locator('#sr2-bag-dialog .woocommerce-mini-cart-item').innerText();assert.match(item,/Shirt - M/);assert.match(item,/1 × \$25.00/);
 for(const width of [390,768,1440]){await page.setViewportSize({width,height:width<768?844:1000});await shot('bag-'+width);}
 await axe('bag-populated','#sr2-bag-dialog');
 await page.getByRole('link',{name:'View Bag',exact:true}).click();await page.waitForLoadState('load');
 const cart=await page.locator('main').innerText();assert.match(cart,/M/);assert.match(cart,/\$25.00/);assert.equal(await page.locator('input.qty').inputValue(),'1');await shot('cart-1440');
 await go('/checkout/');for(const width of [390,768,1440]){await page.setViewportSize({width,height:width<768?844:1000});await shot('checkout-'+width);await axe('checkout-'+width);}
 const checkout=await page.locator('#order_review').innerText();assert.match(checkout,/M/);assert.match(checkout,/25.00/);assert.equal(await page.locator('main h1').count(),1);
 evidence.commerce={variation,sku:'sg-005',size:'M',quantity:1,unitPrice:'25.00',cart,checkout,paymentSubmitted:false};
 await go('/product/sg-005/');await page.locator('[data-bag-open]').click();await page.locator('#sr2-bag-dialog .remove').click();await page.locator('.woocommerce-mini-cart__empty-message').waitFor();
 await page.waitForFunction(()=>document.querySelector('[data-bag-status]').textContent.includes('removed'));
 assert.equal(await page.evaluate(()=>document.activeElement?.getAttribute('aria-label')),'Close bag');evidence.removal=await page.locator('[data-bag-status]').textContent();await page.keyboard.press('Escape');
 // Scroll restoration, rapid toggles, resize/orientation, keyboard wrapping, GET and history.
 await go('/');await page.evaluate(()=>window.scrollTo({top:600,behavior:'instant'}));await page.waitForFunction(()=>scrollY===600);const y=await page.evaluate(()=>scrollY);
 await page.locator('[data-sr2-menu]').focus();await page.locator('[data-sr2-menu]').click();await page.setViewportSize({width:844,height:390});await page.keyboard.press('Escape');const restoredY=await page.evaluate(()=>scrollY);evidence.scrollRestore={before:y,after:restoredY};assert(Math.abs(restoredY-y)<2);evidence.interactions.push('scroll/orientation restore');
 await page.evaluate(()=>window.scrollTo(0,0));
 for(let i=0;i<6;i++){await page.locator('[data-sr2-menu]').click();await page.keyboard.press('Escape');}assert.equal(await page.evaluate(()=>document.body.style.position),'');evidence.interactions.push('six rapid open/Escape cycles');
 await page.locator('[data-sr2-menu]').click();await page.locator('[data-sr2-menu]').focus();await page.keyboard.press('Shift+Tab');assert(await page.locator('[data-site-header]').evaluate(e=>e.contains(document.activeElement)));await page.keyboard.press('Escape');
 await page.locator('[data-sr2-menu]').click();await page.locator('[data-sr2-nav] [data-search-open]').click();await page.getByRole('searchbox',{name:'Search SkyyRose',exact:true}).fill('rose');await page.locator('#sr2-search-dialog button[type=submit]').last().click();await page.waitForURL('**/?s=rose');evidence.interactions.push('native GET search preserved');await page.goBack();assert.equal(await page.evaluate(()=>document.body.style.position),'');
 await page.emulateMedia({reducedMotion:'reduce'});await go('/');await page.locator('[data-sr2-menu]').click();await shot('nav-reduced-844');evidence.reduced=await page.evaluate(()=>({matches:matchMedia('(prefers-reduced-motion: reduce)').matches,normal:getComputedStyle(document.documentElement).getPropertyValue('--sr2-normal'),videos:[...document.querySelectorAll('video')].map(e=>({paused:e.paused,autoplay:e.autoplay}))}));await page.keyboard.press('Escape');
 await page.keyboard.press('Escape');await go('/cart/');assert.equal(await page.locator('main h1').count(),1,'empty cart heading');await shot('cart-empty-844');
 await go('/about/');await page.locator('[data-sr2-menu]').click();assert.match(await page.locator('[data-sr2-nav] a[aria-current="page"]').textContent(),/About/);await page.keyboard.press('Escape');evidence.interactions.push('fallback current-route semantics');
 const nojs=await browser.newContext({javaScriptEnabled:false,viewport:{width:390,height:844}});await nojs.route('**/*',r=>new URL(r.request().url()).origin===base?r.continue():r.abort());const plain=await nojs.newPage();await plain.goto(base);assert(await plain.locator('[data-sr2-nav]').isVisible());assert.match(await plain.locator('[data-bag-open]').getAttribute('href'),/cart/);await nojs.close();evidence.interactions.push('no-JS navigation and real bag URL');
 const touch=await browser.newContext({hasTouch:true,isMobile:true,viewport:{width:390,height:844}});await touch.route('**/*',r=>new URL(r.request().url()).origin===base?r.continue():r.abort());const coarse=await touch.newPage();await coarse.goto(base);await coarse.locator('[data-sr2-menu]').tap();assert(await coarse.locator('[data-sr2-nav]').isVisible());await coarse.locator('[data-sr2-menu]').tap();assert.equal(await coarse.evaluate(()=>document.body.style.position),'');await touch.close();evidence.interactions.push('touch/coarse-pointer open-close');
 assert(evidence.routes.every(r=>r.broken.length===0),'broken route images');
 assert(evidence.a11y.every(r=>r.violations.length===0),'axe violations');
 assert.equal(evidence.console.length,0,'browser console/page errors');
 assert.equal(evidence.httpErrors.length,0,'HTTP errors');
 // Chromium aborts deferred image fetches when the test navigates away. Loaded images are independently decoded/asserted above.
 evidence.navigationAborts=evidence.failures.filter(r=>r.error==='net::ERR_ABORTED');
 evidence.isolationBlockedExternal=[...blockedExternal];
 assert(evidence.failures.every(r=>r.error==='net::ERR_ABORTED'||blockedExternal.has(r.url)),'unexpected request failures');
 evidence.status='PASS';
} catch(error){evidence.status='FAIL';evidence.error=error.stack;await shot('failure').catch(()=>{});throw error;}
finally {await fs.writeFile(path.join(out,'browser-certification.json'),JSON.stringify(evidence,null,2));await browser.close();}
console.log(JSON.stringify({status:evidence.status,routes:evidence.routes.length,responsive:evidence.responsive.length,a11yViolations:evidence.a11y.filter(x=>x.violations.length).map(x=>({name:x.name,count:x.violations.length})),console:evidence.console,http:evidence.httpErrors}));
