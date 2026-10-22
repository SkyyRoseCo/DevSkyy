from pathlib import Path
import json,hashlib
from PIL import Image
from skyyrose.elite_studio.creative.local_composite import AssetRef,Placement,CompositeRequest,LocalCompositeGrant,compose,verify_composite
root=Path.cwd(); p=root/'.artifacts/kids-statue-hero-20261022'
box=json.loads((p/'source-edge-r4.json').read_text())['source_crop']
def ref(path): return AssetRef(str(path.relative_to(root)),hashlib.sha256(path.read_bytes()).hexdigest())
rows=[]
for device,row in json.loads((p/'hero-placement-r5.json').read_text()).items():
 scale=row['source_placement']['scale'];foot=row['character_foot_anchor']
 placement=Placement(round(foot[0]-(512-box[0])*scale),round(foot[1]-(1005-box[1])*scale),scale)
 job='kids-statue-hero-private-'+device+'-r5'; source=ref(p/'skyy-source-rgb-cropped-r4.png')
 request=CompositeRequest(job,source,ref(p/'skyy-source-alpha-cropped-r4.png'),ref(p/('hero-'+device+'-world-r5.png')),placement,str((p/('hero-'+device+'-revealed-r5.png')).relative_to(root)))
 grant=LocalCompositeGrant(job,source.sha256,str(p.relative_to(root)),'Corey left-font/right-graphic hero; tasks/kids-courtyard-hero-20261022/AUTHORITY.json; local only')
 manifest=compose(request,root=root,grant=grant)
 rows.append({'device':device,'manifest':manifest,'verification':verify_composite(request,manifest,root=root)})
 for state in ['concealed','revealed']:
  path=p/('hero-'+device+'-'+state+'-r5.png'); Image.open(path).convert('RGB').save(path.with_suffix('.webp'),quality=91,method=6)
(p/'hero-composites-r5.json').write_text(json.dumps({'source_crop':box,'receipts':rows,'presentation':'HOLD_PRIVATE_VISUAL_REVIEW'},indent=2)+'\n')
print([(r['device'],r['verification']['status']) for r in rows])
