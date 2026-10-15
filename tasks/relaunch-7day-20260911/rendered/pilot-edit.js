export default async ({project,media,text,rect}) => {
 for(const H of [1350,1920]){
  const p=await project({dir:'/home/user/p'+H,size:'1080x'+H,fps:24,background:'#090909'});
  const br=await p.add('/home/user/assets/br.webp'), frame=await p.add('/home/user/assets/frameBR.webp'), bg=await p.add('/home/user/assets/bg.png'), logo=await p.add('/home/user/assets/logo.webp');
  const isStory=H===1920, fw=isStory?770:635, fh=fw*1620/970, fx=isStory?155:420, fy=isStory?305:125;
  const nodes=[media({file:bg,x:0,y:0,width:1080,height:H,fit:'cover'}),rect({x:0,y:0,width:1080,height:H,fill:'#000000',opacity:0.48}),
   media({file:logo,x:70,y:isStory?105:56,width:175,height:110,fit:'contain'}),
   text('SKYYROSE',{x:280,y:isStory?137:78,width:700,fontFamily:'Archivo',fontSize:47,fontWeight:900,letterSpacing:5,color:'#ede9e7'}),
   media({file:br,x:fx+fw*.28,y:fy+fh*.205,width:fw*.44,height:fh*.465,fit:'contain'}),
   media({file:frame,x:fx,y:fy,width:fw,height:fh,fit:'contain'}),
   text('BLACK ROSE',{x:fx+fw*.2,y:fy+fh*.79,width:fw*.6,fontFamily:'Cinzel',fontSize:isStory?32:25,fontWeight:700,align:'center',color:'#d8d3cc'})];
  if(isStory){
   nodes.push(text('CHOOSE WHAT SPEAKS TO YOU.',{x:100,y:250,width:860,fontFamily:'Anton',fontSize:32,align:'center',letterSpacing:2,color:'#d0cbca'}));
   nodes.push(text('Explore Black Rose',{x:120,y:1680,width:800,fontFamily:'Anton',fontSize:42,align:'center',color:'#f6eded'}));
  }else{
   nodes.push(text('THE TOWN.\nYOUR STORY.',{x:64,y:315,width:410,fontFamily:'Archivo',fontSize:73,fontWeight:900,lineHeight:0.98,color:'#f4eeee'}));
   nodes.push(rect({x:68,y:575,width:86,height:3,fill:'#B76E79'}));
   nodes.push(text('Meet Black Rose.\nA new chapter\nis coming.',{x:64,y:625,width:345,fontFamily:'Hanken Grotesk',fontSize:37,lineHeight:1.25,color:'#d7cbce'}));
   nodes.push(text('EXPLORE\nBLACK ROSE',{x:64,y:1000,width:340,fontFamily:'Anton',fontSize:34,lineHeight:1.2,color:'#e4bcc6'}));
  }
  nodes.push(text('LUXURY GROWS FROM CONCRETE.',{x:64,y:H-85,width:940,fontFamily:'Anton',fontSize:24,letterSpacing:2,align:'center',color:'#c5a5ad'}));
  p.compose(nodes,{at:0,dur:1,name:'Black Rose exact-source editorial'});
  await p.frame(0,'renders/poster.png');
 }
};
