auto_v1=await run_guidance_variant_sequence('autov1','none')
print(tabulate(auto_v1['metrics'],headers=['turn','iter','input','cache','reusable','continuity'],tablefmt='github'))
r4=auto_v1['runs'][3]
print({'markers':[f['body']['cache_markers'] for f in r4['fingerprints']], 't4_usage':[r4['usages'][i+1]['raw_usage'] for i in range(0,len(r4['usages']),2)], 'stable':[x['sha256'][:12] for x in r4['fingerprints'][0]['system']})