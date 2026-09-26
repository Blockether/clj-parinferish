valid_work=bench/'autoone'; valid_work.mkdir(); (valid_work/'README.md').write_text('# auto one\n',encoding='utf-8')
try:
 probe=await run_instrumented_turn('validprobe',1,prompt1,marker_mode='none',work_dir=valid_work)
 print({'ok':probe['summary']['result'],'system':[x['sha256'][:12] for x in probe['fingerprints'][0]['system']})
except Exception as e: print(type(e).__name__,str(e)[:2000])