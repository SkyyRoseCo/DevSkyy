'use strict';
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const sharp=require('/Users/theceo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const root='/Users/theceo/DevSkyy-product-card-approved';
const theme=path.join(root,'wordpress-theme/skyyrose-flagship-2');
const receipts=path.join(root,'Comfy/receipts/hero-commerce-compositions-c1');
const relativeDir='generated-candidates/hero-commerce-c1';
const out=path.join(theme,'assets/scroll-world',relativeDir);
const config={"generated":"/Users/theceo/.codex/generated_images/01a06754-0168-7511-b86e-81c60b86a401/exec-60d45990-facb-49df-b61a-7ce09e3a829c.png","prompt":"EDIT THE FIRST IMAGE IN PLACE. One landscape image 1672x941, same Golden Gate terrace and same adult woman at the same right-hand position. Founder correction: SG-006 is a LONG HOODIE worn AS A HOODIE DRESS. The current black trousers are wrong. REMOVE THE TROUSERS COMPLETELY. Extend the mint hoodie itself with a natural relaxed straight longline silhouette down to LOWER MID-THIGH, approximately 10-14 cm above her knees, with a continuous matching mint ribbed hem there. It must visibly read as a single oversized long pullover HOODIE DRESS, not a short hoodie over a skirt, not a fitted mini dress, no added skirt seam, no shorts or trousers, no leggings or tights. Show natural bare legs from the hoodie hem down to the existing white sneakers. Keep this a dignified adult editorial full-body look, nonsexual, normal standing pose, no hem lifting. Preserve the SAME WOMAN: her face, age as adult, skin tone, natural curly hair, expression, hands, stance and body proportions as closely as possible. Preserve the SAME MINT FABRIC and exact lavender bouquet/cloud chest graphic, WHITE drawstrings, roomy hood and front kangaroo pocket from the physical garment reference 2. Graphic stays centered on upper torso at the same scale and must not be stretched down the extended dress; kangaroo pocket remains below graphic at natural hand level; sleeves remain mint with ribbed cuffs, hem ribbing lies at mid-thigh. Reference2 is garment detail authority, not a white background or a different model. Keep white shoes, realistic knees and calves, and proper stone contact/shadows. Change only hoodie length and removal of trousers with anatomically correct visible lower legs; preserve the whole selected blue-gray dusk scene, Bay Bridge-looking structures MUST remain the existing GOLDEN GATE in this first image, coastal fog, gold-lit black stone steps, all background geometry, lighting, and camera framing. Keep LEFT HALF EMPTY: the existing approved male model will be composited later and must not be generated. No new people, symbols, text, watermarks, collage, crop or borders. This is a founder-requested targeted candidate revision, not a new garment design.","references":["/Users/theceo/.codex/generated_images/01a06754-0168-7511-b86e-81c60b86a401/exec-fee73ed8-1659-43d0-99df-0a9f491181eb.png","/Users/theceo/DevSkyy-product-card-approved/wordpress-theme/skyyrose-flagship/assets/images/products/sg-006-mint-lavender-hoodie.png"]};
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const source=path.join(theme,'assets/scroll-world/generated-candidates/founder-commerce-scenes-v1/protected-model-layers/sig-commerce-2-male-mint-set-generated-protected-v2.png');
const write=(file,bytes)=>{fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,bytes,{flag:'wx'});};
async function main(){
  const bytes=fs.readFileSync(source);
  if(sha(bytes)!=='eb8cfbd99c4a963223cf094551dcc62bb022573f46b17f9c819561b1a4794a16')throw new Error('Male source binding changed');
  const {data,info}=await sharp(bytes).ensureAlpha().raw().toBuffer({resolveWithObject:true});
  let l=info.width,t=info.height,r=-1,b=-1;
  for(let y=0;y<info.height;y++)for(let x=0;x<info.width;x++)if(data[(y*info.width+x)*4+3]>16){l=Math.min(l,x);r=Math.max(r,x);t=Math.min(t,y);b=Math.max(b,y);}
  if(r<l)throw new Error('Male foreground unavailable');
  l=Math.max(0,l-6);t=Math.max(0,t-6);r=Math.min(info.width-1,r+6);b=Math.min(info.height-1,b+6);
  const model=await sharp(data,{raw:{width:info.width,height:info.height,channels:4}}).extract({left:l,top:t,width:r-l+1,height:b-t+1}).resize({height:775,kernel:'lanczos3'}).png().toBuffer({resolveWithObject:true});
  const cx=495+model.info.width*.5,cy=70+model.info.height-8;
  const shadow='<svg width="1672" height="941" xmlns="http://www.w3.org/2000/svg"><defs><filter id="s"><feGaussianBlur stdDeviation="9"/></filter></defs><ellipse cx="'+cx+'" cy="'+cy+'" rx="'+model.info.width*.45+'" ry="13" fill="black" opacity=".48" filter="url(#s)"/><ellipse cx="'+cx+'" cy="'+(cy-2)+'" rx="'+model.info.width*.25+'" ry="5" fill="black" opacity=".48"/></svg>';
  const background=fs.readFileSync(config.generated);
  const master=await sharp(background).resize(1672,941,{fit:'fill'}).composite([{input:Buffer.from(shadow),left:0,top:0},{input:model.data,left:495,top:70}]).png().toBuffer();
  const stem='sig-commerce-2-hero-composed-dress-c2';
  const masterPath=path.join(out,stem+'.png');
  write(masterPath,master);
  const variants=[];
  for(const width of [640,960,1672]){
    const v=await sharp(master).resize({width}).webp({quality:90,effort:5}).toBuffer({resolveWithObject:true});
    const asset=relativeDir+'/'+stem+'-'+width+'w.webp';
    write(path.join(theme,'assets/scroll-world',asset),v.data);
    variants.push({asset,width:v.info.width,height:v.info.height,bytes:v.data.length,sha256:sha(v.data)});
  }
  const stage='/Users/theceo/.codex/worktrees/stage-07-br-signature-rollout/DevSkyy/Comfy/quarantine/SIG-COMMERCE-2/SIG-COMMERCE-2-HERO-COMPOSED-DRESS-C2.png';
  write(stage,master);
  // Targeted requested revision, not an inspection pass or approval.
  const manifestPath=path.join(theme,'data/hero-commerce-scenes-c1.json');
  const manifest=JSON.parse(fs.readFileSync(manifestPath,'utf8'));
  const previous=manifest.scenes['SIG-COMMERCE-2'];
  manifest.scenes['SIG-COMMERCE-2']={...previous,asset:variants[2].asset,variants,master:relativeDir+'/'+stem+'.png',master_sha256:sha(master),
    copy:'Mint and lavender on the Golden Gate terrace: the crewneck set and the long hoodie worn as a dress.',
    alt:'Preserved male mint crewneck and sweatpants look with a new female mint long hoodie dress candidate, bare legs and white sneakers, on the Golden Gate terrace.',
    styling:'SG-006_LONG_HOODIE_WORN_AS_DRESS_NO_TROUSERS',
    source_scope:'PRESERVED_MALE_WITH_FOUNDER_DIRECTED_HOODIE_DRESS_CANDIDATE',
    review_message:'Male source preserved. Female long-hoodie dress follows founder direction; identity, garment fidelity and final scene review remain pending.',
    candidate_id:'SIG-COMMERCE-2-HERO-COMPOSED-DRESS-C2',supersedes:'SIG-COMMERCE-2-HERO-COMPOSED-C1'};
  fs.writeFileSync(manifestPath,JSON.stringify(manifest,null,2)+'\n');
  const gallery=path.join(receipts,'preview.html');
  let html=fs.readFileSync(gallery,'utf8');
  html=html.replaceAll('sig-commerce-2-hero-composed-c1','sig-commerce-2-hero-composed-dress-c2')
    .replace('SIG-COMMERCE-2 / C1','SIG-COMMERCE-2 / Dress C2')
    .replace('Mint and lavender meet on the stepped Golden Gate terrace.','Mint and lavender meet on the stepped Golden Gate terrace; the longer hoodie is worn as a dress.')
    .replace('New female identity and hoodie candidate require approval; final scene review pending.','Founder-directed long hoodie dress, with bare legs instead of trousers. New female candidate and final scene review pending.')
    .replace('with a new female mint hoodie candidate','with a new female mint long hoodie dress candidate')
    .replace('Two built-in replacement generations; no retries.','Two initial built-in replacement generations plus one founder-requested hoodie-dress correction; no automatic retries.');
  fs.writeFileSync(gallery,html);
  const receipt={schema:'skyyrose.hero-commerce-candidate-revision.v1',timestamp:new Date().toISOString(),scene_id:'SIG-COMMERCE-2',
    candidate_id:'SIG-COMMERCE-2-HERO-COMPOSED-DRESS-C2',supersedes:'SIG-COMMERCE-2-HERO-COMPOSED-C1',
    founder_direction:'Signature is a longer hoodie and must be displayed as a dress.',
    correction:'Long mint hoodie dress with bare legs, no trousers. White drawstrings, lavender artwork and sneakers retained as generation constraints.',
    prompt:config.prompt,references:config.references,generated_background:config.generated,generated_background_sha256:sha(background),
    preserved_male_source:source,preserved_male_source_sha256:sha(bytes),master:masterPath,master_sha256:sha(master),stage_import:stage,variants,
    active_record:manifest.scenes['SIG-COMMERCE-2'],local_wiring_authorized:true,independent_review:'NOT_RUN',browser_validation:'NOT_RUN',deployment_authorized:false,state:'NEEDS_REVIEW'};
  write(path.join(receipts,'signature-hoodie-dress-c2.json'),JSON.stringify(receipt,null,2)+'\n');
  fs.appendFileSync(path.join(receipts,'ledger.jsonl'),JSON.stringify({timestamp:receipt.timestamp,event:'founder_requested_dress_revision_wired',candidate_id:receipt.candidate_id,state:'NEEDS_REVIEW',receipt:path.join(receipts,'signature-hoodie-dress-c2.json'),prior_assets_retained:true})+'\n');
  console.log(JSON.stringify({master:masterPath,stage_import:stage,manifest:manifestPath,preview:gallery,variants:variants.map(v=>({width:v.width,bytes:v.bytes})),state:'NEEDS_REVIEW'},null,2));
}
main().catch(e=>{console.error(e);process.exitCode=1;});
