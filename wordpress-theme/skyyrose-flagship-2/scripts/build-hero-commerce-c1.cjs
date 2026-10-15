'use strict';
// Candidate assembly only. No tests, new generation, approval, or deployment.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const sharp = require('/Users/theceo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const root = '/Users/theceo/DevSkyy-product-card-approved';
const theme = path.join(root, 'wordpress-theme/skyyrose-flagship-2');
const receiptDir = path.join(root, 'Comfy/receipts/hero-commerce-compositions-c1');
const relativeDir = 'generated-candidates/hero-commerce-c1';
const assetDir = path.join(theme, 'assets/scroll-world', relativeDir);
const input = {"brPath":"/Users/theceo/.codex/generated_images/01a06754-0168-7511-b86e-81c60b86a401/exec-bb8cc022-fb20-4e2a-a508-ec07255c0e5f.png","sig2Path":"/Users/theceo/.codex/generated_images/01a06754-0168-7511-b86e-81c60b86a401/exec-fee73ed8-1659-43d0-99df-0a9f491181eb.png","prompts":[{"scene_id":"BR-COMMERCE-2","prompt":"Create ONE landscape fashion-commerce scene candidate at the first reference's 1672x941 composition. EDIT the first supplied moonlit Bay Bridge terrace environment by adding TWO NEW ADULT campaign models in exact clothing guided by the three subsequent physical garment photos. Preserve this selected environment's nocturnal black/silver character, Bay Bridge towers/cables, single moon, black left wall, wet pavement, and empty round plinth on right. No new logo sculpture or background text. New human models are replacement casting candidates, not supposed to reproduce a previously approved person. Put male centered near x=510 and female x=940, on the same foreground ground plane, heads around y=140, feet around y=830; both confidently front-facing with slight natural contrapposto, full heads and shoes visible, hands relaxed and away from chest and shorts details. Adult male dark-brown skin, short natural curls, calm editorial expression, athletic ordinary human proportions. Adult woman warm-brown skin, natural shoulder-length curls, assured expression, realistic proportions, no engagement/couple touching pose. Their clothing and faces dominate, architecture remains clearly recognizable. MALE CLOTHING from reference 2 BR-005: near-black cotton hoodie, white drawstrings, small light rose/cloud mark ONLY on wearer's RIGHT chest (viewer left), a large light rose/cloud composition on LOWER SIDE-BODY panel at wearer's LEFT (viewer right) extending beside kangaroo pocket toward hem, NOT a sleeve print. Keep sleeves predominantly black; do not move lower-side art to sleeve or center chest. Physical reference controls artwork, material and placements. Reference 3 BR-007 shorts: black tonal rose-pattern mesh, wide white waistband, large white OAKLAND tackle-twill block letters spanning front, white mesh side panels bounded by angular black-and-white striped trim, exact Love Hurts script and side marks as shown in physical photo, black hem with thin white trim, correct pocket openings. Shorts naturally knee-adjacent athletic length, do not turn into pants or solid unpatterned shorts. Preserve visible construction, white waistband and separate upper/lower leg panels. Hoodie's hem must not hide all waistband or front OAKLAND lettering; stage it naturally at hip without inventing cropped hoodie. Neutral black low-top sneakers, no invented shoe marks. FEMALE CLOTHING reference4 BR-004: oversized black longline hoodie with centered large white/gray rose bouquet and cloud graphic exactly following supplied product photo, black drawstrings, kangaroo pocket, black cuffs and hem. Long relaxed hoodie silhouette to upper thigh as long-hoodie presentation, plain unbranded black shorts underneath if needed for coverage, neutral black ankle boots. Do NOT give her BR005 small-chest/lower-side artwork or male shorts. Ground both models on rain-wet pavement with plausible foot contact, compact contact shadows and subtle broken floor reflections. Match cool moonlit edges and soft neutral face fill to environment without tinting black products blue. Realistic fabric weave, mesh, embroidery/applique versus print distinctions, skin and hands, no floating, no white outlines, no mannequins. No extraneous text, labels, title, watermark or frame. ONE completed scene, not a grid or reference board. Keep right-hand stone monument base empty and far-right background unblocked. Garment-photo backgrounds, hanger and couch are not scene elements. This is a new REVIEW CANDIDATE; prioritize garment reference fidelity over generic fashionable substitutions.","references":["/Users/theceo/DevSkyy-product-card-approved/Comfy/receipts/hero-themed-environments-b1/assets/BR-COMMERCE-2-HERO-ENVIRONMENT-B1.png","/Users/theceo/DevSkyy-product-card-approved/wordpress-theme/skyyrose-flagship/assets/images/products/br-005-signature-hoodie.jpeg","/Users/theceo/DevSkyy-product-card-approved/wordpress-theme/skyyrose-flagship/assets/images/products/br-007.jpg","/Users/theceo/DevSkyy-product-card-approved/wordpress-theme/skyyrose-flagship/assets/images/products/br-004-black-rose-hoodie.jpeg"]},{"scene_id":"SIG-COMMERCE-2","prompt":"Create ONE landscape 1672x941 Signature fashion scene candidate. EDIT the first reference environment, the founder-selected Golden Gate lateral stepped terrace, adding exactly ONE NEW ADULT FEMALE model wearing the exact mint/lavender hoodie from reference 2. Keep entire LEFT HALF of the image, x0 through approximately900, unoccupied and usable: an existing approved male model will be composited separately there, DO NOT generate any man. Woman stands in RIGHT THIRD, center x1290, head around y115, shoes around y810, body about 680 pixels high, complete head and full shoes in frame with room around. Find a physically supportable landing on the right foreground terrace; contact shadows, foot angles and gold-lit steps must make her visibly stand on real stone rather than float. Preserve reference architecture, blue-gray dusk, bay fog, Golden Gate bridge behind, black stepped platforms and fine recessed gold lights, dark wet paving, open coastal setting. Do not redesign into a studio or change bridge/location. New female adult casting candidate with medium-deep brown skin, shoulder-length natural curls, oval face, calm assured editorial expression, normal human anatomy. Front-facing upright relaxed stance, subtle weight shift, arms naturally away from torso, hands visible without obstructing chest art, no walking pose or romantic pose. ONLY requested branded garment is SG-006 from physical reference: soft MINT GREEN pullover hoodie, same slightly elongated relaxed silhouette, matching mint ribbed cuffs and bottom hem, mint hood, TWO WHITE drawstrings, large centered lavender-purple rose bouquet and pale lavender/gray CLOUD printed graphic exactly as in reference, FRONT KANGAROO POCKET with angled openings below artwork. Preserve physical photo's graphic composition, scale, cloud silhouette, three-rose arrangement and lavender coloring; NO invented text, extra chest badge, tiny rose embroidery substitute, zipper or hoodie color blocking. Product is mint fabric with lavender artwork, not half-lavender sleeves or a two-tone patchwork hoodie. Do not crop the garment. Unbranded plain dark charcoal fitted straight trousers and neutral clean white sneakers, no logos on pants or shoes, no invented mint/lavender pants SKU for her. Photographic cotton texture, natural fabric weight/folds, accurate skin, fingers and proportions. Match cool soft dusk ambient with slight warm gold edge reflection from terrace lights, but keep garment a clear accurate mint and artwork lavender; not gray, cyan or neon. Realistic contact and subdued reflection without white cutout halo. Leave backdrop and landings on left/middle completely empty for the separately preserved male foreground, no additional people/reflections shaped like extra people. Do not insert any SR monument, signage, lettering, labels, price text, border, collage or watermarks. The garment photo's white background is not a scene element. This is a replacement casting and garment REVIEW CANDIDATE, not an approved exact-product claim.","references":["/Users/theceo/DevSkyy-product-card-approved/Comfy/receipts/hero-themed-environments-b1/assets/SIG-COMMERCE-2-HERO-ENVIRONMENT-B1.png","/Users/theceo/DevSkyy-product-card-approved/wordpress-theme/skyyrose-flagship/assets/images/products/sg-006-mint-lavender-hoodie.png"]}]};
const hash = data => crypto.createHash('sha256').update(data).digest('hex');
const write = (file, data) => { fs.mkdirSync(path.dirname(file), {recursive:true}); fs.writeFileSync(file, data, {flag:'wx'}); };
const json = (file, value) => write(file, JSON.stringify(value, null, 2) + '\n');
const log = value => fs.appendFileSync(path.join(receiptDir, 'ledger.jsonl'), JSON.stringify({timestamp:new Date().toISOString(), ...value}) + '\n');
const sourceRoot = path.join(theme, 'assets/scroll-world/generated-candidates/founder-commerce-scenes-v1/protected-model-layers');
const scenes = [
  {id:'LH-COMMERCE-2', collection:'love-hurts', label:'The Rose Side Chapel',
   copy:'Love Hurts takes the foreground inside the crimson cathedral.',
   skus:['lh-003'], background:path.join(root,'Comfy/receipts/hero-themed-environments-b1/assets/LH-COMMERCE-2-HERO-ENVIRONMENT-B1.png'),
   foreground:'/Users/theceo/.codex/worktrees/stage-06-lh-commerce-2/DevSkyy/Comfy/quarantine/LH-COMMERCE-2/LH-COMMERCE-2-PROTECTED-FOREGROUND-A1.png',
   foregroundHash:'0a0d43fdedf5d35aef536d856b91958053000baad2f072e7fad311ff546e3a44',
   invertAlpha:true, placement:{left:1050,top:85,height:790}, sourceScope:'FOUNDER_APPROVED_FRONT_VIEW',
   alt:'Love Hurts front-view model wearing LH-003 basketball shorts in the rose cathedral side chapel.',
   review:'Approved front-view source, newly composed. Final scene review pending; no side or back claim.'},
  {id:'BR-COMMERCE-2', collection:'black-rose', label:'The Moonlit Waterfront',
   copy:'The Black Rose looks share the Bay Bridge waterfront.',
   skus:['br-005','br-007','br-004'], background:input.brPath,
   sourceScope:'NEW_REPLACEMENT_CAST_AND_PRODUCT_CANDIDATE',
   alt:'Two models on the moonlit Bay Bridge terrace: one wears the BLACK Rose Hoodie — Signature Edition with BLACK Rose x Love Hurts Basketball Shorts, and the other wears the BLACK Rose Hoodie as a longline look.',
   review:'New model and garment candidates. Identity and product-fidelity approval pending.'},
  {id:'SIG-COMMERCE-1', collection:'signature', label:'The Golden Gate Overlook',
   copy:'The Sherpa and Signature Beanie meet the gold-lit overlook.',
   skus:['sg-009','sg-007'], background:path.join(root,'Comfy/receipts/hero-themed-environments-b1/assets/SIG-COMMERCE-1-HERO-ENVIRONMENT-B1.png'),
   foreground:path.join(sourceRoot,'sig-commerce-1-sherpa-beanie-generated-protected-v2.png'),
   foregroundHash:'4d92d83e825ffdec4a6a6fa6981b100d8726f24711c8f886c5526bfa207d368a',
   placement:{left:580,top:60,height:790}, sourceScope:'EXISTING_REVIEWED_SHERPA_BEANIE_SOURCE',
   alt:'Signature male model wearing The Sherpa Jacket and black Signature Beanie at the Golden Gate overlook.',
   review:'Existing reviewed Sherpa and Beanie source, newly composed. Final scene review pending.'},
  {id:'SIG-COMMERCE-2', collection:'signature', label:'The Lateral Terrace',
   copy:'Mint and lavender meet on the stepped Golden Gate terrace.',
   skus:['sg-013','sg-014','sg-006'], background:input.sig2Path,
   foreground:path.join(sourceRoot,'sig-commerce-2-male-mint-set-generated-protected-v2.png'),
   foregroundHash:'eb8cfbd99c4a963223cf094551dcc62bb022573f46b17f9c819561b1a4794a16',
   placement:{left:495,top:70,height:775}, sourceScope:'PRESERVED_MALE_WITH_NEW_FEMALE_HOODIE_CANDIDATE',
   alt:'Two models on the Golden Gate terrace: one wears the Mint & Lavender Crewneck with matching Sweatpants, and the other wears the Mint & Lavender Hoodie as a longline look with white sneakers.',
   review:'Male source preserved. New female identity and hoodie candidate require approval; final scene review pending.'}
];

async function prepareForeground(scene) {
  const bytes = fs.readFileSync(scene.foreground);
  const digest = hash(bytes);
  // Source binding is an ingestion guard, not final-scene visual certification.
  if (digest !== scene.foregroundHash) throw new Error('Source binding changed for ' + scene.id);
  const {data, info} = await sharp(bytes).ensureAlpha().raw().toBuffer({resolveWithObject:true});
  if (scene.invertAlpha) {
    // Original Comfy mask is inverse and quantized to 254. Change alpha only.
    for (let p=3; p<data.length; p+=4) data[p]=255-Math.min(255,Math.round(data[p]*255/254));
    const corrected = await sharp(data,{raw:{width:info.width,height:info.height,channels:4}}).png().toBuffer();
    const correctedPath = path.join(assetDir,'lh-commerce-2-alpha-normalized-c1.png');
    write(correctedPath,corrected);
    json(path.join(receiptDir,'lh-alpha-normalization.json'),{
      source:scene.foreground,source_sha256:digest,output:correctedPath,output_sha256:hash(corrected),
      operation:'alpha=255-min(255,round(original_alpha*255/254))',
      color_operation:'None: loop modifies alpha channel only. Color resampling occurs later during placement.',
      source_issue:'Source alpha preserves studio background and hides subject; its old PASS receipt is not used as masking authority.',
      original_source_retained:true,regeneration:false,independent_review:'NOT_RUN'
    });
  }
  let left=info.width,top=info.height,right=-1,bottom=-1;
  for(let y=0;y<info.height;y++) for(let x=0;x<info.width;x++) if(data[(y*info.width+x)*4+3]>16){
    if(x<left)left=x;if(x>right)right=x;if(y<top)top=y;if(y>bottom)bottom=y;
  }
  if(right<left)throw new Error('No usable foreground for '+scene.id);
  left=Math.max(0,left-6);top=Math.max(0,top-6);right=Math.min(info.width-1,right+6);bottom=Math.min(info.height-1,bottom+6);
  const rendered=await sharp(data,{raw:{width:info.width,height:info.height,channels:4}})
    .extract({left,top,width:right-left+1,height:bottom-top+1})
    .resize({height:scene.placement.height,kernel:'lanczos3'}).png().toBuffer({resolveWithObject:true});
  return {buffer:rendered.data,width:rendered.info.width,height:rendered.info.height,source_sha256:digest,alpha_crop:{left,top,width:right-left+1,height:bottom-top+1}};
}

async function main() {
  fs.mkdirSync(assetDir,{recursive:true});
  const records={}, evidence=[];
  for (const scene of scenes) {
    const background=fs.readFileSync(scene.background);
    const overlays=[];
    let foreground=null;
    if(scene.foreground){
      foreground=await prepareForeground(scene);
      const p=scene.placement, cx=p.left+foreground.width*.5, cy=p.top+foreground.height-8;
      const shadow='<svg width="1672" height="941" xmlns="http://www.w3.org/2000/svg"><defs><filter id="s"><feGaussianBlur stdDeviation="9"/></filter></defs><ellipse cx="'+cx+'" cy="'+cy+'" rx="'+(foreground.width*.45)+'" ry="13" fill="black" opacity=".48" filter="url(#s)"/><ellipse cx="'+cx+'" cy="'+(cy-2)+'" rx="'+(foreground.width*.25)+'" ry="5" fill="black" opacity=".48"/></svg>';
      overlays.push({input:Buffer.from(shadow),left:0,top:0});
      overlays.push({input:foreground.buffer,left:p.left,top:p.top});
    }
    const master=await sharp(background).resize(1672,941,{fit:'fill'}).composite(overlays).png().toBuffer();
    const stem=scene.id.toLowerCase()+'-hero-composed-c1';
    const masterPath=path.join(assetDir,stem+'.png');
    write(masterPath,master);
    const variants=[];
    for(const width of [640,960,1672]){
      const result=await sharp(master).resize({width}).webp({quality:90,effort:5}).toBuffer({resolveWithObject:true});
      const asset=relativeDir+'/'+stem+'-'+width+'w.webp';
      write(path.join(theme,'assets/scroll-world',asset),result.data);
      variants.push({asset,width:result.info.width,height:result.info.height,bytes:result.data.length,sha256:hash(result.data)});
    }
    const stage=scene.collection==='love-hurts'?'stage-06-lh-commerce-2':'stage-07-br-signature-rollout';
    const stagePath='/Users/theceo/.codex/worktrees/'+stage+'/DevSkyy/Comfy/quarantine/'+scene.id+'/'+scene.id+'-HERO-COMPOSED-C1.png';
    write(stagePath,master);
    const record={collection:scene.collection,label:scene.label,copy:scene.copy,alt:scene.alt,product_bindings:scene.skus,
      asset:variants[2].asset,width:1672,height:941,variants,master:relativeDir+'/'+stem+'.png',master_sha256:hash(master),
      source_scope:scene.sourceScope,local_wiring_authorized:true,founder_final_visual_approval:false,
      generation_state:'LOCAL_WIRED_COMPOSITION_CANDIDATE_NEEDS_REVIEW',review_message:scene.review,deployment_authorized:false};
    records[scene.id]=record;
    const item={scene_id:scene.id,candidate_id:scene.id+'-HERO-COMPOSED-C1',master:masterPath,master_sha256:hash(master),stage_import:stagePath,
      background:scene.background,background_sha256:hash(background),foreground:scene.foreground||null,
      foreground_sha256:foreground?.source_sha256||null,placement:scene.placement||null,alpha_crop:foreground?.alpha_crop||null,
      protected_foreground_method:foreground?'Existing source RGB; alpha normalization only where declared; deterministic crop/scale/over composition; no garment regeneration.':null,
      generated_candidate_content:scene.id==='BR-COMMERCE-2'?'New dual cast and reference-guided garments':scene.id==='SIG-COMMERCE-2'?'New female and SG-006 candidate in background; existing male overlay':'None',
      variants,independent_review:'NOT_RUN',runtime_browser_validation:'NOT_RUN',state:'NEEDS_REVIEW'};
    evidence.push(item);log({event:'composition_imported',...item});
  }
  const manifest={schema:'skyyrose.hero-commerce-candidates.v1',task_id:'HERO-COMMERCE-C1',created_at:new Date().toISOString(),
    scope:'User-authorized local model/product composition and wiring; candidate state never asserts final product fidelity.',local_wiring_authority:'Current user request plus explicit replacement-candidate direction.',deployment_authorized:false,
    original_hero_loops_changed:false,prior_environment_candidates_retained:true,scenes:records};
  json(path.join(theme,'data/hero-commerce-scenes-c1.json'),manifest);
  json(path.join(receiptDir,'contract.json'),manifest);
  json(path.join(receiptDir,'prompts.json'),{provider:'builtin-imagegen',automatic_retry:false,requests:input.prompts});
  json(path.join(receiptDir,'evidence.json'),{task_id:'HERO-COMMERCE-C1',state:'NEEDS_REVIEW',builtin_generation_calls:2,runway_calls:0,higgsfield_calls:0,fashn_calls:0,independent_review:'NOT_RUN',tests:'NOT_RUN',browser_validation:'NOT_RUN',deployment:'NOT_PERFORMED',assets:evidence});
  const css='.sr2-world.sr2-world--hero-composed{display:flex;flex-direction:column;height:auto;min-height:0;aspect-ratio:auto;overflow:hidden;background:#10100f;color:#f4eee4}.sr2-hero-commerce__frame{position:relative;flex:0 0 auto;width:100%;margin:0;aspect-ratio:1672/941;overflow:hidden;background:#10100f}.sr2-hero-commerce__frame img{position:static;display:block;width:100%;height:100%;object-fit:contain;transform:none;animation:none;filter:none}.sr2-hero-commerce__details{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.2fr);gap:clamp(20px,3vw,48px);padding:clamp(20px,3vw,42px);border-top:1px solid rgba(191,154,111,.3);background:linear-gradient(125deg,#191714,#10100f 65%)}.sr2-hero-commerce__story h3{margin:8px 0 12px;font:inherit;font-family:var(--font-display,"Cormorant Garamond",Georgia,serif);font-size:clamp(26px,2.6vw,42px);line-height:1.1}.sr2-hero-commerce__story>p{max-width:50ch;line-height:1.6}.sr2-hero-commerce__review{font-size:11px;color:#c3bbae}.sr2-hero-commerce__products h4{margin:0 0 12px;font-size:11px;font-weight:500;letter-spacing:.12em;text-transform:uppercase}.sr2-hero-commerce__products ul{margin:0;padding:0;list-style:none}.sr2-hero-commerce__products li{border-top:1px solid rgba(255,255,255,.14)}.sr2-hero-commerce__products a{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:8px 16px;align-items:center;min-height:64px;padding:14px 0;color:inherit;text-decoration:none}.sr2-hero-commerce__products a>span{font-size:13px}.sr2-hero-commerce__products a>small{font-size:12px}.sr2-hero-commerce__products a>em{grid-column:1/-1;font-size:11px;font-style:normal;color:#cfb18b}.sr2-hero-commerce__products li>span{display:block;padding:16px 0;font-size:12px}.sr2-hero-commerce__products a:focus-visible{outline:2px solid #cfb18b;outline-offset:4px}@media(max-width:767px){.sr2-hero-commerce__details{grid-template-columns:minmax(0,1fr);gap:20px;padding:20px}.sr2-world.sr2-world--hero-composed{min-height:0}}\n';
  write(path.join(theme,'assets/css/hero-commerce-scenes.min.css'),css);
  const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const cards=Object.entries(records).map(([id,s])=>{
    const image=path.relative(receiptDir,path.join(theme,'assets/scroll-world',s.asset));
    return '<article id="'+id+'"><p class="eyebrow">'+id+' / C1</p><h2>'+esc(s.label)+'</h2><a href="'+esc(path.relative(receiptDir,path.join(theme,'assets/scroll-world',s.master)))+'"><img src="'+esc(image)+'" width="1672" height="941" loading="lazy" decoding="async" alt="'+esc(s.alt)+'"></a><p>'+esc(s.copy)+'</p><p class="skus">'+s.product_bindings.join(' / ').toUpperCase()+'</p><p class="review">'+esc(s.review)+'</p><a class="button" href="/tools/v2-theme-preview.php?route='+s.collection+'#world">Open wired V2 collection &rarr;</a></article>';
  }).join('');
  write(path.join(receiptDir,'preview.html'),'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SkyyRose / Hero commerce C1</title><style>*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse at top right,#e6d8c2,transparent 55%),#f1eee7;color:#24221e;font-family:"Avenir Next",Avenir,"Trebuchet MS",sans-serif}main{max-width:1500px;margin:auto;padding:55px 5vw}header{border-top:2px solid #24221e;padding-top:24px;margin-bottom:50px}h1,h2{font-family:Palatino,"Book Antiqua",Georgia,serif;font-weight:400}h1{font-size:clamp(40px,6vw,80px);letter-spacing:-.04em;line-height:1.05;margin:16px 0}h2{font-size:30px;margin:10px 0 18px}.eyebrow,.skus{font-size:11px;letter-spacing:.13em;text-transform:uppercase}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:46px 28px}article{min-width:0;border-bottom:1px solid #cbbfae;padding-bottom:30px}img{display:block;width:100%;height:auto}p{line-height:1.6}a{color:inherit}.review{font-size:12px;color:#6b6050}.button{display:inline-block;padding:12px 0;font-size:12px;text-underline-offset:5px}nav{display:flex;gap:25px;flex-wrap:wrap;font-size:12px}footer{margin-top:40px;border-top:2px solid #24221e;padding-top:20px;font-size:12px;line-height:1.7}@media(max-width:800px){main{padding:30px 20px}.grid{grid-template-columns:1fr}}</style></head><body><main><header><p class="eyebrow">SkyyRose / Hero-world commerce / C1 local candidates</p><h1>The collection.<br>Inside its world.</h1><p>Four compositions with models and products, wired into local V2 collection chapters. New replacement looks remain explicitly marked as candidates.</p><nav><a href="contract.json">Runtime contract</a><a href="evidence.json">Asset receipts</a><a href="prompts.json">Replacement prompts</a></nav></header><section class="grid">'+cards+'</section><footer>Original hero videos and B1 environment masters are unchanged. No FASHN, Runway or Higgsfield calls. Two built-in replacement generations; no retries. Local assembly and wiring only. No independent visual QA, browser validation, final product approval or deployment was performed.</footer></main></body></html>');
  log({event:'local_wiring_handoff',state:'NEEDS_REVIEW',manifest:path.join(theme,'data/hero-commerce-scenes-c1.json'),review_gallery:path.join(receiptDir,'preview.html'),deployment_authorized:false});
  console.log(JSON.stringify({manifest:path.join(theme,'data/hero-commerce-scenes-c1.json'),preview:path.join(receiptDir,'preview.html'),scenes:evidence.map(s=>({id:s.scene_id,master:s.master,stage:s.stage_import,webp_bytes:s.variants.map(v=>({width:v.width,bytes:v.bytes}))})),state:'NEEDS_REVIEW'},null,2));
}
main().catch(error=>{log({event:'assembly_failure',state:'BLOCKED',message:error.message});console.error(error);process.exitCode=1;});
