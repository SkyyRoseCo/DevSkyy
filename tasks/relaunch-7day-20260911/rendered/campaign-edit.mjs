import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
const root='/home/user/campaign';
export default async ({project,media,text,rect})=>{
 const cfg=JSON.parse(fs.readFileSync(root+'/config.json','utf8'));
 const titles={sg:'SIGNATURE',br:'BLACK ROSE',lh:'LOVE HURTS',kids:'KIDS CAPSULE'};
 const colors={sg:'#D4AF37',br:'#C0C0C0',lh:'#DC143C',kids:'#B76E79'};
 const frames={sg:'frameSG',br:'frameBR',lh:'frameLH',kids:'frameKC'};
 const copy={sg:['CHOOSE YOUR\nEXPRESSION.','Signature.\nA new chapter\nis coming.'],br:['THE TOWN.\nYOUR STORY.','Meet Black Rose.\nA new chapter\nis coming.'],lh:['A NAME WITH\nA BLOODLINE.','Love Hurts.\nThe story carries on.'],kids:['LUXURY RUNS\nIN THE FAMILY.','Named after a daughter.\nBuilt by a father.']};
 const paths=Object.fromEntries(cfg.assets.map(a=>[a.id,root+'/assets/'+a.id+'.'+a.path.split('.').pop()]));
 for(const g of cfg.generated)paths[g.id]=root+'/assets/'+g.id+(g.id[0]==='G'?'.mp4':'.png');
 async function makeP(id,H,W=1080){
  const dir=root+'/projects/'+id,p=await project({dir,size:W+'x'+H,fps:24,background:'#090909'});
  const doc=JSON.parse(fs.readFileSync(dir+'/project.json','utf8'));fs.mkdirSync(dir+'/fonts',{recursive:true});
  for(const f of cfg.fontFaces){fs.copyFileSync(root+'/fonts/'+f.file,dir+'/fonts/'+f.file);doc.assets.push({id:crypto.randomUUID(),name:'fonts/'+f.file,kind:'font',mimeType:'font/woff2',byteSize:fs.statSync(dir+'/fonts/'+f.file).size,duration:null,width:null,height:null,fontFace:{family:f.family,weight:String(f.weight),style:'normal'},uri:'fs:fonts/'+f.file,hash:null});}
  fs.writeFileSync(dir+'/project.json',JSON.stringify(doc));
  return p;
 }
 async function handles(p){const h={};for(const [k,v]of Object.entries(paths))if(!['G1','G2','G3'].includes(k))h[k]=await p.add(v);return h;}
 const tx=(s,x,y,w,size,fam='Archivo',color='#eee8e8',extra={})=>text(s,{x,y,width:w,fontFamily:fam,fontSize:size,fontWeight:fam==='Archivo'?900:400,color,lineHeight:1.13,...extra});
 function brand(h,W,H){return [media({file:h.logo,x:64,y:H>1500?105:55,width:155,height:100,fit:'contain'}),tx('SKYYROSE',250,H>1500?130:80,W-310,42,'Archivo','#eee8e8',{letterSpacing:4})];}
 function bg(h,key,W,H){return [media({file:h[key],x:0,y:0,width:W,height:H,fit:'cover'}),rect({x:0,y:0,width:W,height:H,fill:'#000000',opacity:.42})];}
 function portal(h,key,W,H,id){
  const story=H>1500,fw=story?685:630,fh=fw*1620/970,fx=story?197:418,fy=story?365:183,accent=colors[key];
  let n=[...bg(h,key==='br'?'I2':'I1',W,H),...brand(h,W,H)];
  n.push(media({file:h[key],x:fx+fw*.28,y:fy+fh*.205,width:fw*.44,height:fh*.465,fit:'contain'}),media({file:h[frames[key]],x:fx,y:fy,width:fw,height:fh,fit:'contain'}));
  n.push(tx('EXPLORE',fx+fw*.22,fy+fh*.785,fw*.56,story?27:24,'Anton',accent,{align:'center',letterSpacing:1}));
  n.push(tx(titles[key],fx+fw*.20,fy+fh*.823,fw*.60,story?29:25,'Cinzel','#eee6e1',{align:'center'}));
  if(story){
   const variant=id.endsWith('03')?'THE STORY CARRIES ON.':id.endsWith('04')?'FIND YOUR WORLD.':titles[key];
   n.push(tx(variant,100,248,810,variant.length>21?45:56,'Archivo','#eee8e8',{align:'center'}));
   const sentence=id==='V1'?'CHOOSE YOUR WORLD':id==='V2'?'EXPLORE BLACK ROSE':key==='kids'?'Named after a daughter. Built by a father.':key==='lh'?'A name with a bloodline.':'Choose what speaks to you.';
   n.push(tx(sentence,105,1560,805,id==='V1'||id==='V2'?42:32,id==='V1'||id==='V2'?'Anton':'Hanken Grotesk','#d4c5cb',{align:'center'}));
  }else{
   n.push(tx(copy[key][0],64,320,325,(key==='sg'||key==='lh')?40:55));
   n.push(rect({x:68,y:625,width:80,height:3,fill:accent}));
   n.push(tx(copy[key][1],64,677,315,32,'Hanken Grotesk','#d2c6cc'));
   n.push(tx(titles[key],64,1050,340,30,'Anton',accent));
  }
  n.push(tx('LUXURY GROWS FROM CONCRETE.',64,H-88,W-128,23,'Anton','#c6a8af',{align:'center',letterSpacing:2}));
  return n;
 }
 function scene(h,train,W,H,id){
  const wide=W>H,story=H>1500;const n=[rect({x:0,y:0,width:W,height:H,fill:'#080808'}),...brand(h,W,H)];
  const headline=train?'THE TOWN LINE.':id==='D1-E03'?'FOUR WORLDS.\nONE NAME.':'A NEW CHAPTER\nIN THE TOWN.';
  n.push(tx(headline,80,wide?205:story?265:220,W-170,wide?74:70,'Archivo','#eee6e8',{align:'left'}));
  const py=wide?365:story?670:495, pw=W-128,ph=pw*941/1672;
  n.push(media({file:h[train?'train':'bridge'],x:64,y:py,width:pw,height:ph,fit:'contain'}));
  n.push(rect({x:80,y:py+ph+55,width:95,height:3,fill:'#B76E79'}));
  n.push(tx(train?'JERSEY SERIES. A CLOSER LOOK IS COMING.':'THE WEBSITE RELAUNCH IS COMING.',80,py+ph+90,W-180,wide?34:31,'Anton','#e6ccd2'));
  n.push(tx(train?'Explore the Jersey Series':id==='V1'?'CHOOSE YOUR WORLD':'Follow the reveal',80,wide?930:story?1460:1195,W-180,wide?41:38,'Anton','#f5e9ed'));
  return n;
 }
 function pdp(h,W,H){
  return [...bg(h,'I2',W,H),...brand(h,W,H),tx('BLACK ROSE',64,205,W-128,70),media({file:h.br,x:64,y:335,width:545,height:860,fit:'contain'}),tx('SEE THE\nDETAILS.',640,410,350,59),tx('Black Rose\nHoodie',642,600,330,33,'Hanken Grotesk','#d4c5ca'),media({file:h.brflat,x:640,y:750,width:320,height:290,fit:'contain'}),tx('EXPLORE BLACK ROSE',640,1100,345,32,'Anton','#ddb0bd')];
 }
 const manifest=process.env.RESUME_FILMS ? cfg.deliverables.filter(d=>d.kind==='still').map(d=>({id:d.id,kind:'still',width:d.ratio==='16:9'?1920:1080,height:d.ratio==='16:9'?1080:d.ratio==='4:5'?1350:1920,file:d.id+'.png',status:'RENDERED_REVIEW_CANDIDATE'})).concat([{id:'V1',kind:'video',width:1080,height:1920,duration:12,file:'V1.mp4',status:'RENDERED_PRELAUNCH_REVIEW_VARIANT'}]):[];
 for(const d of (process.env.RESUME_FILMS?[]:cfg.deliverables.filter(d=>d.kind==='still'))){
  const W=d.ratio==='16:9'?1920:1080,H=d.ratio==='16:9'?1080:d.ratio==='4:5'?1350:1920,p=await makeP(d.id,H,W),h=await handles(p),key=d.assets[0];
  const nodes=d.id==='D7-E02'?pdp(h,W,H):key==='bridge'||key==='train'?scene(h,key==='train',W,H,d.id):portal(h,key,W,H,d.id);
  p.compose(nodes,{at:0,dur:1,name:d.id+' exact-source review creative'});
  const report=await p.frame(0,'renders/'+d.id+'.png');fs.copyFileSync(root+'/projects/'+d.id+'/renders/'+d.id+'.png',root+'/exports/'+d.id+'.png');
  manifest.push({id:d.id,kind:'still',width:W,height:H,file:d.id+'.png',status:'RENDERED_REVIEW_CANDIDATE',diagnostics:report.diagnostics});
 }
 const films=[['V1',12,'G1'],['V2',10,'G2'],['V3',12,'G3']];
 for(const [id,dur,g]of films){
  if(process.env.RESUME_FILMS && id==='V1')continue;
  const p=await makeP(id,1920),h=await handles(p),clip=await p.add(paths[g]);
  if(id==='V1'){
   p.cut(clip,{from:0,dur:5,at:0});
   p.compose([...brand(h,1080,1920),tx('A NEW CHAPTER\nIN THE TOWN.',100,280,820,74)],{at:0,dur:5,name:'House reveal'});
   for(const [i,key]of ['sg','br','lh','kids'].entries())p.compose(portal(h,key,1080,1920,'V1'),{at:5+i,dur:1,name:key+' exact source'});
   p.compose(scene(h,false,1080,1920,'V1'),{at:9,dur:3,name:'Prelaunch end card'});
   
  }else if(id==='V2'){
   p.compose(portal(h,'br',1080,1920,'V2'),{at:0,dur:3,name:'Exact Black Rose portrait'});
   p.compose([...bg(h,'I2',1080,1920),...brand(h,1080,1920),tx('SEE THE DETAILS.',100,260,820,69),media({file:h.brflat,x:150,y:470,width:750,height:780,fit:'contain'}),tx('EXPLORE BLACK ROSE',120,1523,780,43,'Anton','#e9c1ce',{align:'center'})],{at:3,dur:2,name:'Exact source product detail'});
   const n=[media({file:clip,x:0,y:0,width:1080,height:1920,fit:'cover',trimStart:0,muted:true}),...portal(h,'br',1080,1920,'V2').slice(2)];p.compose(n,{at:5,dur:3,name:'Static garment over atmosphere'});
   p.compose(portal(h,'br',1080,1920,'V2'),{at:8,dur:2,name:'Black Rose closing'});
   
  }else{
   p.cut(clip,{from:0,dur:5,at:0});p.compose([...brand(h,1080,1920),tx('THE TOWN LINE.',100,285,820,78),tx('JERSEY SERIES',100,1390,820,44,'Anton','#ddbd9f')],{at:0,dur:5,name:'Town Line motion'});
   p.compose(scene(h,true,1080,1920,'V3'),{at:5,dur:7,name:'Canonical branded train reveal'});
  }
  for(const t of [0,3,5,8,dur-.1])await p.frame(t,'renders/'+id+'-'+t+'.png');
  await p.render('renders/'+id+'.mp4',{bitrate:8000000,concurrency:2,shards:2});
  fs.copyFileSync(root+'/projects/'+id+'/renders/'+id+'.mp4',root+'/exports/'+id+'.mp4');
  manifest.push({id,kind:'video',width:1080,height:1920,duration:dur,file:id+'.mp4',status:'RENDERED_PRELAUNCH_REVIEW_VARIANT'});
 }
 fs.writeFileSync(root+'/exports/export-manifest.json',JSON.stringify(manifest,null,2));
};
