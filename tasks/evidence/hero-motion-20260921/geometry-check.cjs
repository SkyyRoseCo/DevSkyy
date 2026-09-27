const { chromium } = require('/Users/theceo/DevSkyy/node_modules/playwright');
const fs = require('node:fs');
const target = process.argv[2] || 'https://staging-7e48-skyyrose.wpcomstaging.com/';
const out = process.argv[3] || '/tmp/skyyrose-hero-motion';
(async () => {
 const browser = await chromium.launch({headless:true});
 const result = {target,checkedAt:new Date().toISOString(),checks:[]};
 for (const mode of [{width:320},{width:390},{width:768},{width:1440},{width:390,reducedMotion:'reduce'},{width:390,javaScriptEnabled:false},{width:1440,reducedMotion:'reduce'},{width:1440,javaScriptEnabled:false},{width:720,textZoom:true}]) {
  const page = await browser.newPage({viewport:{width:mode.width,height:1000},reducedMotion:mode.reducedMotion||'no-preference',javaScriptEnabled:mode.javaScriptEnabled!==false});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(target,{waitUntil:'domcontentloaded'});
  await page.evaluate(()=>document.fonts.ready);
  if(mode.textZoom)await page.addStyleTag({content:'html {font-size:200% !important}'});
  await page.waitForTimeout(1100);
  const data=await page.evaluate(()=>{
   const h=document.querySelector('#sr2-archive-title'), hero=document.querySelector('.sr2-editorial-hero');
   const r=h.getBoundingClientRect(),hr=hero.getBoundingClientRect();
   const a=[...hero.querySelectorAll('.sr2-archive-scene__actions a')].map(e=>({text:e.textContent.trim(),href:e.getAttribute('href'),r:e.getBoundingClientRect().toJSON()}));
   const chars=[...h.querySelectorAll('span')].map(e=>({text:e.textContent,opacity:getComputedStyle(e).opacity,transform:getComputedStyle(e).transform}));
   const film=hero.querySelector('[data-home-model-loop]').getBoundingClientRect(),copy=hero.querySelector('.sr2-editorial-hero__copy').getBoundingClientRect();
   return {film:film.toJSON(),copy:copy.toJSON(),text:h.textContent.replace(/\s+/g,''),accessible:h.getAttribute('aria-label'),centerError:Math.abs(r.x+r.width/2-innerWidth/2),h1:r.toJSON(),hero:hr.toJSON(),scrollWidth:document.documentElement.scrollWidth,width:innerWidth,actions:a,chars,animations:h.getAnimations({subtree:true}).map(a=>({name:a.animationName,state:a.playState,frames:a.effect.getKeyframes(),timing:a.effect.getTiming()}))};
  });
  data.mode=mode;data.errors=errors;
  data.pass=errors.length===0&&(data.accessible||data.text).toUpperCase()==='SKYYROSE'&&data.centerError<2&&data.scrollWidth<=mode.width&&data.h1.right<=mode.width&&data.h1.left>=0&&data.actions.every(a=>a.r.width>0&&a.r.left>=0&&a.r.right<=mode.width);
  if(mode.width<768)data.pass=data.pass&&data.film.top>=data.copy.bottom-1&&data.film.width>=mode.width-40;
  if(mode.reducedMotion)data.pass=data.pass&&data.animations.length===0&&data.chars.every(c=>Number(c.opacity)===1);
  await page.screenshot({path:`${out}/hero-${mode.width}${mode.reducedMotion?'-reduced':mode.javaScriptEnabled===false?'-nojs':mode.textZoom?'-textzoom':''}.png`});
  if(mode.width===1440&&!mode.reducedMotion&&mode.javaScriptEnabled!==false){
   data.frameIntervals=await page.evaluate(()=>new Promise(resolve=>{const times=[];let last;function tick(t){if(last!==undefined)times.push(t-last);last=t;if(times.length===90)resolve(times);else requestAnimationFrame(tick)}requestAnimationFrame(tick)}));
  }
  result.checks.push(data);await page.close();
 }
 await browser.close();fs.writeFileSync(`${out}/verification.json`,JSON.stringify(result,null,2));
 console.log(JSON.stringify(result.checks.map(c=>({mode:c.mode,pass:c.pass,centerError:c.centerError,width:c.scrollWidth,animationCount:c.animations.length,errors:c.errors}))));
 if(result.checks.some(c=>!c.pass))process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});
