import urllib.request,json,asyncio
urls={k:v for k,v in [('multi','https://huggingface.co/api/models/fastino/gliner2.5-multi-v1'),('base','https://huggingface.co/api/models/fastino/gliner2.5-base-v1'),('small','https://huggingface.co/api/models/fastino/gliner2.5-small-v1'),('multi-card','https://huggingface.co/fastino/gliner2.5-multi-v1/raw/main/README.md'),('base-card','https://huggingface.co/fastino/gliner2.5-base-v1/raw/main/README.md'),('repo-search','https://api.github.com/search/repositories?q=gliner2.5&per_page=10')]]
def fetch(k,u):
 try:
  with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'vis-research/1.0'}),timeout=20) as f: raw=f.read()
  return k,(json.loads(raw) if k in ('multi','base','small','repo-search') else raw.decode('utf-8'))
 except Exception as e: return k,str(e)
results=dict(await asyncio.gather(*(asyncio.to_thread(fetch,k,u) for k,u in urls.items())))
for k in ('multi','base','small'):
 v=results[k]
 if isinstance(v,dict):print(k,{field:v.get(field) for field in ('id','sha','lastModified','pipeline_tag','tags','cardData')},'files',[(x['rfilename'],x.get('size')) for x in v.get('siblings',[])][:30])
 else:print(k,v)
for k in ('multi-card','base-card'):print(k,results[k][:15000])
v=results['repo-search'];print('repo-search',[(x['full_name'],x['html_url'],x['description']) for x in v.get('items',[])[:10]] if isinstance(v,dict) else v)