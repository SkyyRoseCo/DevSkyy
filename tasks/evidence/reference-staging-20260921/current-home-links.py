import json,urllib.request,urllib.parse,concurrent.futures,datetime
from html.parser import HTMLParser
from pathlib import Path
base='https://staging-7e48-skyyrose.wpcomstaging.com/'
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=set();self.ids=set()
 def handle_starttag(self,t,a):
  d=dict(a)
  if d.get('id'):self.ids.add(d['id'])
  if t=='a' and d.get('href'):self.links.add(d['href'])
html=urllib.request.urlopen(base,timeout=20).read().decode()
assert 'sr2-editorial-hero' in html and 'sr2-editorial-products' in html
p=Links();p.feed(html);urls=[];local=[]
for link in sorted(p.links):
 u=urllib.parse.urlparse(urllib.parse.urljoin(base,link))
 if link.startswith('#'):
  local.append({'href':link,'exists':link[1:] in p.ids});continue
 if u.scheme not in ('http','https'):continue
 keys=urllib.parse.parse_qs(u.query,keep_blank_values=True)
 assert not set(keys)&{'add-to-cart','remove_item','wc-ajax','action'},link
 assert 'logout' not in u.path,link
 urls.append(urllib.parse.urlunparse(u._replace(fragment='')))
def check(url):
 try:
  req=urllib.request.Request(url,method='HEAD')
  with urllib.request.urlopen(req,timeout=15) as r:return {'url':url,'status':r.status,'final_url':r.url}
 except Exception as e:return {'url':url,'error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:results=list(pool.map(check,sorted(set(urls))))
out={'date':datetime.datetime.now(datetime.timezone.utc).isoformat(),'target':base,'identity':'editorial hero and featured-products section present','authentication':'PUBLIC_READ_ONLY','fragments':local,'links':results}
path=Path('/Users/theceo/.codex/worktrees/abe0/DevSkyy/tasks/evidence/reference-staging-20260921/current-home-links.json');path.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'checked':len(results),'fragments':local,'failures':[x for x in results if x.get('status')!=200]},indent=2))
