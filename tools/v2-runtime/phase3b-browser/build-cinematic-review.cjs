#!/usr/bin/env node
'use strict';

// Local review artifact only. Serve the review directory, never its WordPress-containing parent.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const assert = require('node:assert/strict');

const repository = path.resolve(__dirname, '../../..');
const theme = path.join(repository, 'wordpress-theme/skyyrose-flagship-2');
const artifacts = path.join(repository, '.artifacts/v2-visual-recovery-20260905');
const review = path.join(artifacts, 'review');
const media = path.join(review, 'media');
const manifest = JSON.parse(fs.readFileSync(path.join(theme, 'data/approved-scroll-world-scenes.json')));
const widths = [390, 768, 1440];
const surfaces = ['home', 'signature', 'black-rose', 'love-hurts', 'kids', 'shop', 'pdp', 'navigation', 'search'];
const labels = {home:'Home', signature:'Signature', 'black-rose':'Black Rose', 'love-hurts':'Love Hurts', kids:'The Heir / Kids', shop:'Shop', pdp:'Product page', navigation:'Navigation', search:'Search', scenes:'Nine approved scenes', skyy:'Ask Skyy', cards:'Paid product cards'};
const escape = value => String(value).replace(/[&<>"']/g, character => ({'&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'}[character]));
const digest = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const linked = new Set();

function ensureDirectory(directory) {
  fs.mkdirSync(directory, {recursive:true});
  assert(fs.lstatSync(directory).isDirectory() && !fs.lstatSync(directory).isSymbolicLink(), `Refusing symlink directory: ${directory}`);
}

function linkMedia(source, name, expectedHash) {
  assert(/^[A-Za-z0-9_.-]+\.(?:png|jpe?g|webp|mp4|webm)$/.test(name), 'Only exact image/video filenames may be exposed');
  const real = fs.realpathSync(source);
  assert(real.startsWith(artifacts + path.sep) || real.startsWith(path.join(theme, 'assets') + path.sep), 'Review source escapes authorized evidence roots');
  assert(fs.statSync(real).isFile(), 'Review source must be a file');
  if (expectedHash) assert.equal(digest(fs.readFileSync(real)), expectedHash, `Approved reference hash mismatch: ${name}`);
  const destination = path.join(media, name);
  if (fs.existsSync(destination) || fs.lstatSync(destination, {throwIfNoEntry:false})) {
    assert(fs.lstatSync(destination).isSymbolicLink(), `Preserving unexpected existing file: ${name}`);
    assert.equal(fs.realpathSync(destination), real, `Preserving unexpected existing link: ${name}`);
  } else {
    fs.symlinkSync(real, destination);
  }
  linked.add(name);
  return `media/${name}`;
}

function screenshot(name, title, description = '') {
  const source = path.join(artifacts, name);
  if (!fs.existsSync(source)) return `<figure class="missing"><figcaption>${escape(title)}</figcaption><p>Not captured at this viewport/state. No evidence is inferred.</p>${description ? `<p>${escape(description)}</p>` : ''}</figure>`;
  const src = linkMedia(source, name);
  return `<figure><figcaption>${escape(title)}</figcaption><a href="${src}" target="_blank" rel="noopener"><img src="${src}" loading="lazy" decoding="async" alt="${escape(title)}"></a><p class="file">${escape(name)}</p>${description ? `<p>${escape(description)}</p>` : ''}</figure>`;
}

function section(system, width, heading, body, extra = '') {
  return `<section data-system="${escape(system)}" data-width="${width}"><h2>${escape(heading)} <small>${width}px</small></h2>${extra}<div class="comparison">${body}</div></section>`;
}

function build() {
  ensureDirectory(review);
  ensureDirectory(media);
  assert.equal(Object.keys(manifest.scenes).length, 9, 'Review requires exactly nine canonical scenes');
  let sections = '';
  for (const width of widths) {
    for (const surface of surfaces) {
      const body = screenshot(`A-${surface}-${width}.png`, 'A · Recovered source — local reconstruction', surface === 'pdp' ? 'Historical media/data resolution is incomplete in this synthetic fixture; this does not prove that the original staging PDP lacked media.' : '')
        + screenshot(`B-${surface}-${width}.png`, 'B · Repaired Phase 3B foundation — rejected visual direction')
        + screenshot(`D-${surface}-${width}.png`, 'D · Integrated + optimized candidate — founder review required');
      sections += section(surface, width, labels[surface], body);
    }
    for (const scene of Object.values(manifest.scenes)) {
      assert.equal(scene.approval_status, 'APPROVED FINAL — IMPLEMENT', 'Unapproved scene cannot enter reference viewer');
      const poster = scene.required_runtime_assets.find(asset => asset.role === 'poster');
      const movie = scene.required_runtime_assets.find(asset => asset.role === (width === 390 ? 'mobile' : 'desktop'));
      assert(poster && movie, 'Approved reference assets missing');
      const posterUrl = linkMedia(path.join(theme, poster.path), `reference-${scene.scene_id.toLowerCase()}-poster${path.extname(poster.path)}`, poster.sha256);
      const movieUrl = linkMedia(path.join(theme, movie.path), `reference-${scene.scene_id.toLowerCase()}-${movie.role}.mp4`, movie.sha256);
      const reference = `<figure><figcaption>Approved final reference · ${escape(scene.scene_id)}</figcaption><a href="${posterUrl}" target="_blank" rel="noopener"><img src="${posterUrl}" loading="lazy" decoding="async" alt="Approved reference for ${escape(scene.label)}"></a><p class="file">Poster SHA-256: ${escape(poster.sha256)}</p><details><summary>Play approved source film · ${escape(movie.role)}</summary><video controls playsinline preload="none" poster="${posterUrl}" src="${movieUrl}"><a href="${movieUrl}">Open source film</a></video><p>Source film uses native controls and never autoplays in this viewer.</p></details></figure>`;
      const id = scene.scene_id.toLowerCase();
      const candidate = screenshot(`D-scene-image-${id}-${width}.png`, 'D · Integrated image composition') + screenshot(`D-scene-${id}-${width}.png`, 'D · Integrated scene and native product links');
      const warning = scene.scene_id === 'LH-COMMERCE-1' ? '<p class="warning">Known source-film concern: models walk off frame in LH-COMMERCE-1. Review the full approved source film and integrated behavior. Candidate still needs work; this viewer does not approve a replacement edit.</p>' : '';
      sections += section('scenes', width, `${scene.scene_id} · ${scene.label}`, reference + candidate, warning);
    }
    const cardShots = ['signature','black-rose','love-hurts'].filter(collection => fs.existsSync(path.join(artifacts, `D-${collection}-cards-${width}.png`)));
    if (cardShots.length) sections += section('cards', width, 'Approved card system · integrated candidate', cardShots.map(collection => screenshot(`D-${collection}-cards-${width}.png`, `D · ${labels[collection]} card treatment`)).join(''));
    const skyyShots = fs.readdirSync(artifacts).filter(name => /^D-skyy[a-z0-9-]*\.png$/i.test(name) && (name.endsWith(`-${width}.png`) || !/-\d+\.png$/.test(name))).sort();
    const gaitShots = ['walk', 'idle'].map(state => screenshot(`cinematic-integration-skyy-gait-${width}-${state}.png`, `D · Home 3D ${state} · actual hardware render`)).join('');
    const gaitMovie = `D-skyy-home-walkon-${width}.webm`;
    const gaitVideo = fs.existsSync(path.join(artifacts, gaitMovie)) ? `<figure><figcaption>NEW UPGRADE · actual Home walk-on recording</figcaption><video controls playsinline preload="none" src="${linkMedia(path.join(artifacts, gaitMovie), gaitMovie)}"></video><p>Recorded browser output on Apple M5 Metal. Existing character and materials; newly derived joint motion. This is a local candidate, not cinematic-quality certification.</p></figure>` : '<p>Home walk-on video has not been captured.</p>';
    sections += section('skyy', width, 'Home · physical 3D walk-on', gaitShots + gaitVideo);
    sections += section('skyy', width, 'Ask Skyy · character, conversation and walk-in evidence', skyyShots.length ? skyyShots.map(name => screenshot(name, `D · ${name.replace(/^D-/, '').replace(/\.png$/, '').replace(/-/g, ' ')}`)).join('') : '<p>No matching Skyy state has been captured at this viewport.</p>', '<p>NEW UPGRADE: optimized 3D delivery, conversational controls and walk-in integration are engineering changes around the approved character. State screenshots do not prove animation timing; use the separate runtime verification evidence.</p>');
  }
  const css = `:root{color-scheme:dark;font:16px/1.5 system-ui,sans-serif;background:#101216;color:#f3f4f6}*{box-sizing:border-box}body{margin:0;padding:24px}a{color:#add6ff}a:focus-visible,button:focus-visible,select:focus-visible,summary:focus-visible{outline:3px solid #fff;outline-offset:4px}header{max-width:1200px}h1{font-size:clamp(1.7rem,4vw,2.6rem);line-height:1.15}h2{font-size:1.35rem}small{color:#c4cedb;font-size:.85rem}p{max-width:100ch}.status,.warning{border-left:4px solid #edc072;background:#2a2115;padding:12px 16px}.controls{position:sticky;top:0;z-index:2;display:flex;flex-wrap:wrap;gap:16px;background:#18202cf5;border:1px solid #637083;padding:12px;margin-top:24px}.controls label{display:flex;gap:10px;align-items:center}select{font:inherit;color:inherit;background:#202d40;padding:8px;min-height:44px;border:1px solid #97abc6}section{padding:24px 0;border-bottom:1px solid #586375}.comparison{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}figure{margin:0;min-width:0;background:#191e27;border:1px solid #465064;padding:12px}figcaption{font-weight:700;padding-bottom:12px}img,video{width:100%;height:auto;display:block;background:#08090b}figure p{font-size:.85rem}.file{overflow-wrap:anywhere;color:#b9c9df}details{margin-top:16px}summary{cursor:pointer;padding:12px;min-height:44px}video{margin-top:12px}.missing{border-style:dashed;color:#c5cfdd}[hidden]{display:none!important}noscript{display:block;padding:12px}footer{padding:24px 0;color:#c4cedb}@media(max-width:850px){body{padding:14px}.comparison{grid-template-columns:1fr}.controls{position:static}.controls label{flex-wrap:wrap}}`;
  const js = `const viewport=document.getElementById('viewport');const system=document.getElementById('system');const count=document.getElementById('count');function filter(){let visible=0;document.querySelectorAll('section[data-width]').forEach(section=>{const show=section.dataset.width===viewport.value&&(system.value==='all'||section.dataset.system===system.value);section.hidden=!show;if(show)visible++;});count.textContent=visible+' comparison groups shown';}viewport.addEventListener('change',filter);system.addEventListener('change',filter);filter();`;
  const hash = text => crypto.createHash('sha256').update(text).digest('base64');
  const csp = `default-src 'none'; img-src 'self'; media-src 'self'; style-src 'sha256-${hash(css)}'; script-src 'sha256-${hash(js)}'; base-uri 'none'; form-action 'none'`;
  const html = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="${escape(csp)}"><title>SkyyRose V2 · Founder visual comparison</title><style>${css}</style></head><body><header><h1>SkyyRose V2 · Founder visual comparison</h1><p class="status"><strong>NEEDS_MORE_WORK · FOUNDER_REVIEW_REQUIRED</strong><br>Local integration candidate. Mobile performance gate remains open. This evidence viewer does not certify creative acceptance, production readiness or permission to deploy.</p><p><strong>A</strong> is the exact recovered theme reconstructed locally with synthetic fixture data and current plugins; it is not an original staging screenshot. <strong>B</strong> is the repaired Phase 3B engineering foundation whose creative direction was rejected. <strong>D</strong> is the integrated and optimized candidate.</p><p><strong>Approved source</strong> means the exact nine-scene reference poster/film selection bound by the canonical manifest and approval records. <strong>NEW UPGRADE</strong> means implementation, loading, responsive delivery or interface work layered around approved assets; it does not create new visual approval.</p><p>A's product page has an unresolved historical media/data fixture dependency. No A Bag screenshot is shown: A used a direct Cart link, so a B-style Bag overlay comparison is not applicable. Missing viewports and states remain visibly marked as uncaptured. Click any image to open its original capture.</p><p>The existing BR-COMMERCE-3 lounge is part of the approved nine. The separate final Town Line Pre-Order experience remains preserved for later implementation.</p></header><nav class="controls" aria-label="Review filters"><label for="viewport">Viewport<select id="viewport">${widths.map(width => `<option value="${width}">${width}px</option>`).join('')}</select></label><label for="system">System<select id="system"><option value="all">All systems</option>${Object.entries(labels).map(([value,label]) => `<option value="${value}">${escape(label)}</option>`).join('')}</select></label><span id="count" role="status" aria-live="polite"></span></nav><noscript>Filters require JavaScript. Every available comparison is shown below.</noscript><main>${sections}</main><footer>Generated from exact local image and approved media paths. Only the dedicated review directory should be served; its parent contains local WordPress configuration and must remain private. Re-run the review builder after final captures to refresh evidence.</footer><script>${js}</script></body></html>\n`;
  const target = path.join(review, 'index.html');
  assert(!fs.lstatSync(target, {throwIfNoEntry:false})?.isSymbolicLink(), 'Refusing symlink index');
  fs.writeFileSync(target, html);
  console.log(JSON.stringify({status:'BUILT_LOCAL_REVIEW_NOT_APPROVED',index:target,linked_media:linked.size,viewports:widths,scene_references:9,html_sha256:digest(html),serve_directory:review}, null, 2));
}

try { build(); } catch (error) { console.error(`Cinematic review: ${error.message}`); process.exitCode = 1; }
