root=Path(session['workspace']['root']); c=root/'apps/vis-companion'; async def run(cn,timeout=180):
 h=await shell(cn,cwd=str(c)); return await h.wait(timeout)
res=await gather(run('npm run lint',180),run('npm run build',180)); print(res)