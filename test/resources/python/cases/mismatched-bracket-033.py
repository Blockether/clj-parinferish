time.sleep(3)
app5=await run_instrumented_turn('appauto',5,prompt5,app_sid,'none',work)
print({'tokens':app5['summary']['result']['tokens'],'raw_usage':app5['usages'][-1]['raw_usage'],'stable':[x['sha256'][:12] for x in app5['fingerprints'][0]['system'],'markers':app5['fingerprints'][0]['body']['cache_markers']})