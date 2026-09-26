print(defs(pattern='network')); def summarize_network(start_s, end_s):
    """Aggregate CDP wire lengths by endpoint without retaining request metadata."""
    stream=spel.sci(res.id,'{:requests @network-requests :finished @network-finished :data @network-data}').data['result']
    reqs=[json.loads(v) for v in stream['requests']]; fin={v['requestId']:v for s in stream['finished'] for v in [json.loads(s)]}; chunks=Counter()
    for s in stream['data']:
        v=json.loads(s); chunks[v['requestId']]+=v.get('encodedDataLength',0)
    out=collections.defaultdict(lambda:[0,0,0]); total=0
    for v in reqs:
        if not start_s <= v['timestamp'] <= end_s: continue
        rid=v['requestId']; url=urlsplit(v['request']['url']); path=re.sub(r'/[0-9a-f]{8}-[0-9a-f-]{27,}', '/:session',url.path); key=(url.netloc,path)
        transfer=fin[rid].get('encodedDataLength',0) if rid in fin else chunks[rid]
        out[key][0]+=1; out[key][1]+=round(transfer); out[key][2]+=(rid in fin); total+=round(transfer)
    return {'total_bytes':total,'request_count':sum(v[0] for v in out.values()),'by_endpoint':dict(sorted(out.items(),key=lambda kv:-kv[1][1]))}
for label in ['transcript-sustained-up','list-sustained-scroll','switch-to-older-session']:
 p=raw_profiles[label]; n=summarize_network(p['startTime']/1e6,p['endTime']/1e6); print(label,n)
print('monitor event count',spel.sci(res.id,'[(count @network-requests) (count @network-finished) (count @network-data)]').data['result'])