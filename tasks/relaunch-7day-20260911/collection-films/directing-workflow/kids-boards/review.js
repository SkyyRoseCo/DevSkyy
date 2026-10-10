'use strict';
(() => {
  const data = window.BOARD_DATA;
  const byId = id => document.getElementById(id);
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let routeIndex = Math.max(0, data.routes.findIndex(r => r.id === new URLSearchParams(location.search).get('route')));
  let elapsed = 0, playing = false, last = 0, frame = null;
  const palette = {red:'#b74748', skyy:'#c9a472', purple:'#9a82c7'};
  const poses = {
    rest:[[-38,-164],[-41,-106],[38,-164],[41,-106]],
    leftHip:[[-60,-167],[-30,-145],[38,-164],[41,-106]],
    rightHip:[[-38,-164],[-41,-106],[60,-167],[30,-145]],
    bothHip:[[-60,-167],[-30,-145],[60,-167],[30,-145]],
    lookLeft:[[-38,-164],[-41,-106],[38,-164],[41,-106]],
    lookRight:[[-38,-164],[-41,-106],[38,-164],[41,-106]],
    seated:[[-36,-149],[-37,-109],[36,-149],[37,-109]]
  };
  const current = () => data.routes[routeIndex];
  const duration = () => current().shots.reduce((n,s) => n+s.seconds,0);
  const stamp = value => `00:${String(Math.floor(value)).padStart(2,'0')}`;
  const escape = str => String(str).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  function locate(time) {
    let start = 0;
    for(let i=0;i<current().shots.length;i++) {
      const s = current().shots[i];
      if(time<start+s.seconds || i===current().shots.length-1) return {shot:s,index:i,start,progress:Math.min(1,(time-start)/s.seconds)};
      start+=s.seconds;
    }
  }
  const mix=(a,b,t)=>a+(b-a)*t;
  function interpolate(previous,target,t) {
    if(!previous || previous.hidden || target.hidden) return {...target};
    return {...target,x:mix(previous.x,target.x,t),y:mix(previous.y,target.y,t),scale:mix(previous.scale,target.scale,t),arms:poses[target.pose].map((p,i)=>p.map((v,j)=>mix(poses[previous.pose][i][j],v,t)))};
  }
  function figure(p) {
    if(p.hidden) return '';
    const color=palette[p.id], mascot=p.id==='skyy', arms=p.arms||poses[p.pose];
    const eyes=p.gaze!==undefined?p.gaze*7:p.pose==='lookLeft'?-7:p.pose==='lookRight'?7:0;
    const hair=mascot?Array.from({length:9},(_,i)=>{const a=(i*25+170)*Math.PI/180;return `<circle cx="${Math.cos(a)*30}" cy="${-269+Math.sin(a)*27}" r="11"/>`;}).join(''):'<path d="M-26-271 Q-20-301 0-297 Q25-297 27-273"/>';
    const legs=p.pose==='seated'?'<path d="M-19-99 L-43-58 L-43 0 M19-99 L43-58 L43 0"/>':'<path d="M-18-102 L-22-51 L-24 0 M18-102 L22-51 L24 0"/>';
    return `<g transform="translate(${p.x} ${p.y}) scale(${p.scale})" fill="none" stroke="${color}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"><ellipse cy="4" rx="55" ry="10" fill="#000" stroke="none" opacity=".22"/><g fill="#20272b" stroke-width="3">${hair}<ellipse cy="-270" rx="27" ry="31"/></g><path d="M-29-223 Q0-235 29-223 L34-111 Q0-98-34-111Z" fill="${color}" fill-opacity=".18"/><path d="M-29-217 L${arms[0][0]} ${arms[0][1]} L${arms[1][0]} ${arms[1][1]} M29-217 L${arms[2][0]} ${arms[2][1]} L${arms[3][0]} ${arms[3][1]}"/>${legs}<path d="M-24 0 h-13 M24 0 h13"/><g stroke="#ded5c4" stroke-width="3"><path d="M${eyes-10}-272 h2 M${eyes+8}-272 h2"/></g></g>`;
  }
  function svgFor(shot,index,progress=1,motion=false) {
    const previous=index>0?current().shots[index-1]:null;
    const tween=motion&&!reduced&&!shot.cut?Math.min(1,Math.max(0,progress*shot.seconds/1.05)):1;
    const smooth=tween*tween*(3-2*tween);
    const figures=shot.figures.map(p=>interpolate(previous?.figures.find(q=>q.id===p.id),p,smooth));
    const camera=shot.camera;
    const shift=shot.piers&&!reduced?(progress*80):0;
    const seat=shot.seat?'<g stroke="#82715c" fill="#22282b" stroke-width="4"><path d="M196 643V397Q197 329 270 283Q343 329 344 397V643Z"/><path d="M182 653H358V695H182Z M199 695V744 M341 695V744"/><path d="M213 596V407Q218 366 270 329Q322 366 327 407V596" fill="none"/></g>':'';
    const piers=shot.piers?`<g fill="#15191d" opacity=".85"><rect x="${85-shift}" y="175" width="70" height="340"/><rect x="${430-shift}" y="175" width="70" height="340"/></g>`:'';
    const floorDots=shot.figures.filter(p=>!p.hidden).map(p=>`<circle cx="${180+p.x*.33}" cy="${876+(p.y-650)*.2}" r="5" fill="${palette[p.id]}"/>`).join('');
    return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${camera.join(' ')}" aria-hidden="true"><rect width="540" height="960" fill="#171d21"/><g stroke="#596368" fill="none" stroke-width="2"><path d="M32 650V234Q45 134 270 66Q495 134 508 234V650 M64 646V251Q80 164 270 101Q460 164 476 251V646"/><path d="M64 518H476 M64 595H476 M172 145V519 M368 145V519"/><path d="M0 825L140 650H400L540 825 M75 960L183 650 M465 960L357 650"/></g><g fill="#27373e"><path d="M68 254Q91 197 168 166V514H68Z"/><path d="M177 162Q219 139 270 118Q321 139 363 162V514H177Z"/><path d="M373 166Q449 197 472 254V514H373Z"/></g><g stroke="#64727a" opacity=".6" fill="none"><path d="M68 437H472 M70 463L150 416L215 454L305 398L379 432L472 388"/></g>${piers}${seat}${figures.slice().sort((a,b)=>a.y-b.y).map(figure).join('')}<g opacity=".75"><rect x="171" y="863" width="200" height="46" rx="4" fill="#0e1316" stroke="#596368"/>${floorDots}<path d="M270 919l-7 12h14z" fill="#b7bdbe"/></g></svg>`;
  }
  function render() {
    const {shot,index,progress}=locate(elapsed);
    byId('screen').innerHTML=svgFor(shot,index,progress,true);
    const blind=byId('blind').checked;
    byId('screen').setAttribute('aria-label',blind?`Schematic sequence ${current().id}, shot ${index+1}`:`${shot.name}. ${shot.action}`);
    byId('shot-counter').textContent=`SHOT ${String(index+1).padStart(2,'0')} / ${current().shots.length}`;
    byId('clock').textContent=`${stamp(elapsed)} / ${stamp(duration())}`;
    byId('scrub').value=String(elapsed);
    byId('beat-id').textContent=`${current().id}${index+1} · ${shot.seconds} SECONDS`;
    byId('beat-name').textContent=shot.name;
    byId('action').textContent=shot.action;
    byId('why').textContent=shot.why;
    byId('product').textContent=shot.fronts?`Planned front-reading interval: ${shot.fronts.join(' + ')}. Exact fidelity remains untested.`:'Story action. Product readability must be checked in the finished frame.';
    document.querySelectorAll('.shot-card').forEach((card,i)=>card.setAttribute('aria-current',String(i===index)));
  }
  function stop() {playing=false;if(frame!==null)cancelAnimationFrame(frame);frame=null;byId('play').textContent='Play animatic';}
  function tick(now) {
    if(!playing)return;
    elapsed=Math.min(duration(),elapsed+(now-last)/1000);last=now;
    if(elapsed>=duration())stop();
    render();if(playing)frame=requestAnimationFrame(tick);
  }
  function seek(time) {stop();elapsed=Math.max(0,Math.min(duration(),time));render();}
  function select(index) {
    stop();routeIndex=index;elapsed=0;
    const r=current();byId('route-title').textContent=r.title;byId('mechanism').textContent=`ROUTE ${r.id} / ${r.mechanism}`;byId('question').textContent=r.question;byId('risk').textContent=r.risk;byId('scrub').max=String(duration());byId('movie-link').href=`exports/Kids-Route-${r.id}-rough-board.mp4`;
    document.querySelectorAll('#routes button').forEach((b,i)=>b.setAttribute('aria-pressed',String(i===index)));
    byId('strip').replaceChildren();let start=0;
    r.shots.forEach((s,i)=>{const at=start;const b=document.createElement('button');b.className='shot-card';b.setAttribute('aria-label',`Inspect shot ${i+1}`);b.innerHTML=svgFor(s,i)+`<span class="shot-copy"><small>${r.id}${i+1} · ${stamp(start)}–${stamp(start+s.seconds)}</small><strong>${escape(s.name)}</strong></span>`;b.addEventListener('click',()=>seek(at));byId('strip').append(b);start+=s.seconds;});
    render();
  }
  data.routes.forEach((r,i)=>{const b=document.createElement('button');b.dataset.route=r.id;b.innerHTML=`<small>ROUTE ${r.id} · ${r.shots.reduce((n,s)=>n+s.seconds,0)} SEC</small><span class="route-name">${escape(r.title)}</span>`;b.addEventListener('click',()=>select(i));byId('routes').append(b);});
  byId('play').addEventListener('click',()=>{if(playing){stop();render();return;}if(elapsed>=duration())elapsed=0;playing=true;byId('play').textContent='Pause';last=performance.now();frame=requestAnimationFrame(tick);});
  byId('restart').addEventListener('click',()=>seek(0));
  byId('scrub').addEventListener('input',e=>seek(Number(e.target.value)));
  byId('previous').addEventListener('click',()=>{const {index,start}=locate(elapsed);seek(elapsed>start+.1?start:current().shots.slice(0,Math.max(0,index-1)).reduce((n,s)=>n+s.seconds,0));});
  byId('next').addEventListener('click',()=>{const {index,start,shot}=locate(elapsed);seek(index===current().shots.length-1?duration():start+shot.seconds);});
  byId('blind').addEventListener('change',e=>{document.body.classList.toggle('blind',e.target.checked);render();});
  if(new URLSearchParams(location.search).get('blind')==='1'){byId('blind').checked=true;document.body.classList.add('blind');}
  const labels={'skyy-master':'Skyy / identity master','kids-red-model':'Kids red / product-card identity','kids-purple-model':'Kids purple / alternate card identity','kids-red-product':'Kids red / garment source','kids-purple-product':'Kids purple / garment source','kids-red-archive':'Red archive / wardrobe corrections required','kids-purple-archive':'Purple archive / wardrobe corrections required','kids-hero':'Kids hero / architecture only','train':'Train / exterior only'};
  for(const asset of window.SOURCE_DATA?.assets||[]) {
    const f=document.createElement('figure');f.className='source-card';const a=document.createElement('a');a.href=new URL(`file://${asset.path}`).href;const img=document.createElement('img');img.src=a.href;img.alt=labels[asset.id]||asset.id;img.loading='lazy';a.append(img);f.append(a);const cap=document.createElement('figcaption');cap.textContent=labels[asset.id]||asset.id;const small=document.createElement('small');small.textContent=`${asset.sku||asset.role} · SHA256 ${asset.sha256.slice(0,12)}…`;cap.append(small);f.append(cap);byId('source-grid').append(f);
  }
  document.addEventListener('visibilitychange',()=>{if(document.hidden&&playing){stop();render();}});
  select(routeIndex);
  // Local inspection interface for reproducible screenshots and export. No network or storage.
  window.boardReview={select,seek,svgFor,getState:()=>({route:current().id,time:elapsed,playing,duration:duration(),shot:locate(elapsed).index+1})};
})();
