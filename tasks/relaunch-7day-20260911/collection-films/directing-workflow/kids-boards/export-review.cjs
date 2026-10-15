/* Reproduce local board exports and focused browser checks. No provider/network calls. */
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const {pathToFileURL} = require('node:url');
const {spawnSync} = require('node:child_process');
const {chromium} = require('/Users/theceo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root = __dirname;
const out = path.join(root,'exports');
const qa = path.join(root,'qa');
fs.mkdirSync(out,{recursive:true});fs.mkdirSync(qa,{recursive:true});
const run = (cmd,args) => {const r=spawnSync(cmd,args,{encoding:'utf8'});if(r.error)throw r.error;if(r.status!==0)throw new Error(r.stderr);return r.stdout;};
(async()=>{
  const browser=await chromium.launch({headless:true});
  try {
    const page=await browser.newPage({viewport:{width:1440,height:1000}});
    const errors=[];page.on('pageerror',e=>errors.push(e.message));
    await page.goto(pathToFileURL(path.join(root,'preview.html')).href);
    await page.evaluate(()=>document.querySelectorAll('.source-card img').forEach(img=>{img.loading='eager';}));
    await page.waitForFunction(()=>[...document.querySelectorAll('.source-card img')].every(img=>img.complete&&img.naturalWidth>0));
    assert.equal(await page.locator('.source-card').count(),9);
    const routeData=await page.evaluate(()=>window.BOARD_DATA.routes);
    const draw=await browser.newPage({viewport:{width:720,height:1280}});
    const movies=[];
    for(let index=0;index<routeData.length;index++) {
      const route=routeData[index];await page.evaluate(i=>window.boardReview.select(i),index);
      const svgFrames=await page.evaluate(()=>window.BOARD_DATA.routes.find(r=>r.id===window.boardReview.getState().route).shots.map((s,i)=>window.boardReview.svgFor(s,i)));
      const frames=path.join(out,`route-${route.id}-frames`);fs.mkdirSync(frames,{recursive:true});
      let concat='';let start=0;const contact=[];
      for(let shot=0;shot<svgFrames.length;shot++) {
        const svg=svgFrames[shot];
        await draw.setContent(`<style>html,body{margin:0;width:720px;height:1280px;background:#171d21}svg{display:block;width:100%;height:100%}</style>${svg}`);
        const filename=path.join(frames,`${String(shot+1).padStart(2,'0')}.png`);
        await draw.screenshot({path:filename});
        concat+=`file '${filename.replace(/'/g,"'\\''")}'\nduration ${route.shots[shot].seconds}\n`;
        contact.push(`<figure>${svg}<figcaption>${route.id}${shot+1} · ${start}–${start+route.shots[shot].seconds}s</figcaption></figure>`);
        start+=route.shots[shot].seconds;
      }
      concat+=`file '${path.join(frames,`${String(svgFrames.length).padStart(2,'0')}.png`).replace(/'/g,"'\\''")}'\n`;
      const list=path.join(frames,'timing.ffconcat');fs.writeFileSync(list,concat);
      const film=path.join(out,`Kids-Route-${route.id}-rough-board.mp4`);
      run('/opt/homebrew/bin/ffmpeg',['-v','error','-y','-f','concat','-safe','0','-i',list,'-vf','fps=24','-frames:v',String(start*24),'-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart','-an',film]);
      const probe=JSON.parse(run('/opt/homebrew/bin/ffprobe',['-v','error','-show_streams','-show_format','-of','json',film]));
      assert.equal(probe.streams.length,1);assert.equal(probe.streams[0].codec_type,'video');assert.equal(Number(probe.streams[0].nb_frames),start*24);assert.equal(probe.streams[0].width,720);assert.equal(probe.streams[0].height,1280);
      movies.push({route:route.id,path:film,seconds:start,frames:start*24,audio:false,kind:'TIMED_STILL_BOARDS_NOT_GENERATED_MOTION'});
      const sheet=await browser.newPage({viewport:{width:1440,height:1600}});
      await sheet.setContent(`<style>*{box-sizing:border-box}body{margin:0;background:#eee8df;padding:22px;font:14px sans-serif;color:#292320}header{height:90px;display:flex;justify-content:space-between;align-items:center}header strong{font-size:30px;font-weight:400}main{display:grid;grid-template-columns:repeat(4,1fr);gap:15px}figure{margin:0}svg{width:100%;height:auto;display:block}figcaption{padding:10px 0;font:12px monospace}small{font-size:12px}</style><header><strong>Sequence ${route.id} · ${start} seconds</strong><small>SCHEMATIC BOARDS · Red / child card · Gold outline / Skyy · Purple / second child card</small></header><main>${contact.join('')}</main>`);
      await sheet.screenshot({path:path.join(out,`Sequence-${route.id}-contact.png`),fullPage:true});await sheet.close();
    }
    await draw.close();
    await page.evaluate(()=>window.boardReview.select(0));
    await page.evaluate(()=>window.boardReview.seek(6.3));
    const first=await page.locator('#screen').innerHTML();await page.evaluate(()=>window.boardReview.seek(6.3));assert.equal(await page.locator('#screen').innerHTML(),first);
    await page.locator('#play').click();await page.waitForTimeout(300);await page.locator('#play').click();
    const stopped=await page.evaluate(()=>window.boardReview.getState());assert.equal(stopped.playing,false);assert(stopped.time>6.3);
    const pausedSvg=await page.locator('#screen').innerHTML();await page.evaluate(t=>window.boardReview.seek(t),stopped.time);assert.equal(await page.locator('#screen').innerHTML(),pausedSvg);
    const cutPass=await page.evaluate(()=>{const s=window.BOARD_DATA.routes[0].shots[1];return window.boardReview.svgFor(s,1,0,true)===window.boardReview.svgFor(s,1,.5,true);});assert.equal(cutPass,true);
    await page.evaluate(()=>window.boardReview.seek(0));await page.locator('#next').click();assert.equal((await page.evaluate(()=>window.boardReview.getState())).shot,2);await page.locator('#previous').click();assert.equal((await page.evaluate(()=>window.boardReview.getState())).shot,1);
    await page.locator('#blind').check();assert.equal(await page.locator('#director').evaluate(el=>getComputedStyle(el).visibility),'hidden');await page.locator('#blind').uncheck();
    await page.screenshot({path:path.join(qa,'desktop.png'),fullPage:true});
    await page.setViewportSize({width:390,height:844});
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
    await page.screenshot({path:path.join(qa,'mobile.png'),fullPage:true});
    const reduced=await browser.newPage({reducedMotion:'reduce'});await reduced.goto(pathToFileURL(path.join(root,'preview.html')).href);
    const reducedPass=await reduced.evaluate(()=>{window.boardReview.select(2);const s=window.BOARD_DATA.routes[2].shots[2];return window.boardReview.svgFor(s,2,0,true)===window.boardReview.svgFor(s,2,.7,true);});assert.equal(reducedPass,true);await reduced.close();assert.deepEqual(errors,[]);
    const result={status:'PASS_FOCUSED_LOCAL_BROWSER_AND_EXPORT_CHECKS',date:new Date().toISOString(),checks:{source_images_loaded:9,route_durations:movies.map(m=>m.seconds),pause_seek_same_frame:true,explicit_cut:true,reduced_motion:true,next_previous:true,blind_notes_hidden:true,mobile_horizontal_overflow:false,page_errors:errors},exports:movies,limits:['No finished garment/identity fidelity proved by schematics','No live provider or campaign execution','Movies hold schematic endpoint frames for planned shot duration; browser additionally interpolates simple blocking']};
    fs.writeFileSync(path.join(qa,'browser-and-export.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
  } finally {await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
