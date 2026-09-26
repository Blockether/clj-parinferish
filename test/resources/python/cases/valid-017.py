r65_program=r'''from pathlib import Path
import hashlib,json,os,pwd,grp,re,shutil,socket,subprocess,tempfile,time,uuid
source=Path(SOURCE)
account=pwd.getpwnam('nobody'); group=grp.getgrgid(account.pw_gid)
assert account.pw_uid != 0
base=Path(tempfile.mkdtemp(prefix='vis-sdk-guide-t65-',dir='/var/tmp'))
base.chmod(0o755)
unit='vis-sdk-guide-t65-'+uuid.uuid4().hex[:10]+'.service'
before=subprocess.check_output(['systemctl','show','vis-sandbox.service','-p','MainPID','--value'],text=True).strip()
started=False
try:
 bundle=base/'bin'; shutil.copytree(source,bundle)
 for p in [bundle,*bundle.rglob('*')]:
  if p.is_dir(): p.chmod(0o755)
  elif p.is_file(): p.chmod(0o755 if p.stat().st_mode & 0o111 else 0o644)
 binary=bundle/'vis-agent-native'
 assert hashlib.sha256(binary.read_bytes()).hexdigest()=='7a882f61994b00520719ea821f9b71ac4f2cfb36ba9492066a6de44dff670457'
 print('NATIVE_STAMP', (bundle/'vis-agent-native.build').read_text().strip(),flush=True)
 home=base/'home'; home.mkdir(mode=0o700); os.chown(home,account.pw_uid,account.pw_gid)
 work=base/'project'; work.mkdir(mode=0o700); os.chown(work,account.pw_uid,account.pw_gid)
 cfg=home/'.vis'; cfg.mkdir(mode=0o700); os.chown(cfg,account.pw_uid,account.pw_gid)
 config=cfg/'config.yml'; config.write_text('{"toggles":{"council":false}}'); config.chmod(0o600); os.chown(config,account.pw_uid,account.pw_gid)
 with socket.socket() as s:
  s.bind(('127.0.0.1',0)); port=s.getsockname()[1]
 wrapper=str(bundle/'vis-agent')
 text=re.search(r'```ini\n(.*?)\n```',Path(DOC).read_text(),re.S)
 # Extract literal fenced unit without changing its policy.
 if text is None:
  text=Path(DOC).read_text().split('```ini\n'.replace('\\n','\n')) if False else None
 document=Path(DOC).read_text()
 unit_text=document.split('```ini\n'.replace('\\n','\n'),1) if False else document.split('```ini
',1)[1].split('
```',1)[0]
 unit_text=unit_text.replace('User=visgw','User='+account.pw_name).replace('Group=visgw','Group='+group.gr_name).replace('/srv/vis-project',str(work)).replace('/home/visgw',str(home))
 unit_text=unit_text.replace(str(home)+'/.local/bin/vis-agent',wrapper+' -Duser.home='+str(home)).replace('--port 7890','--port '+str(port))
 path=base/unit; path.write_text(unit_text+'\n'.replace('\\n','\n'))
 checked=subprocess.run(['systemd-analyze','verify',str(path)],capture_output=True,text=True)
 print('UNIT_VERIFY',checked.returncode,checked.stderr[-1000:],flush=True); assert checked.returncode==0
 cmd=['systemd-run','--unit='+unit,'--collect','--property=Type=simple','--property=User='+account.pw_name,'--property=Group='+group.gr_name,'--property=WorkingDirectory='+str(work),'--property=Restart=on-failure','--property=RestartSec=5','--property=TimeoutStopSec=60','--property=UMask=0077','--setenv=HOME='+str(home),'--setenv=VIS_HOME='+str(cfg),'--setenv=PATH='+str(bundle)+':/usr/local/bin:/usr/bin:/bin',wrapper,'-Duser.home='+str(home),'gateway','start','--host','127.0.0.1','--port',str(port),'--require-token']
 result=subprocess.run(cmd,capture_output=True,text=True); assert result.returncode==0,result.stderr; started=True
 for _ in range(120):
  try:
   with socket.create_connection(('127.0.0.1',port),timeout=0.2): break
  except OSError: time.sleep(1)
 else: raise AssertionError('gateway listener timeout')
 status=subprocess.check_output(['systemctl','show',unit,'-p','MainPID','-p','NRestarts','-p','ActiveState','-p','User','-p','Group'],text=True)
 print(status.strip(),flush=True)
 assert 'ActiveState=active' in status and 'NRestarts=0' in status
 pid=int(re.search(r'^MainPID=(\d+)$'.replace('\\d','\d'),status,re.M)[1])
 uids=next(line for line in Path('/proc',str(pid),'status').read_text().splitlines() if line.startswith('Uid:')).split()[1:]
 assert all(int(v)==account.pw_uid for v in uids); print('PROCESS_UIDS',uids,flush=True)
 command=['runuser','-u',account.pw_name,'--','env','-i','HOME='+str(home),'VIS_HOME='+str(cfg),'PATH='+str(bundle)+':/usr/local/bin:/usr/bin:/bin',wrapper,'-Duser.home='+str(home),'gateway','status']
 result=subprocess.run(command,capture_output=True,text=True,timeout=40)
 print('CANONICAL_STATUS_EXIT',result.returncode,flush=True); assert result.returncode==0
 token=cfg/'gateway.token'; assert token.exists() and token.stat().st_uid==account.pw_uid and token.stat().st_mode & 0o777 == 0o600
 owned=[p for p in cfg.rglob('*') if p.is_file()]
 assert owned and all(p.stat().st_uid==account.pw_uid for p in owned)
 print('STATE_FILES_OWNED_BY_NONROOT',len(owned),'TOKEN_MODE_0600',True,flush=True)
finally:
 if started:
  stopped=subprocess.run(['systemctl','stop',unit],capture_output=True,timeout=90); assert stopped.returncode==0
 state=subprocess.run(['systemctl','is-active',unit],capture_output=True,text=True)
 print('TEMPORARY_UNIT_FINAL',state.stdout.strip(),flush=True); assert state.returncode!=0
 left=[]
 for p in Path('/proc').iterdir():
  if not p.name.isdigit(): continue
  try:
   if str(base) in os.readlink(p/'exe') or str(base) in os.readlink(p/'cwd'): left.append(p.name)
  except OSError: pass
 print('REMAINING_TEMP_PROCESSES',left,flush=True); assert not left
 after=subprocess.check_output(['systemctl','show','vis-sandbox.service','-p','MainPID','--value'],text=True).strip()
 print('PRODUCTION_PID_UNCHANGED',before==after,after,flush=True); assert before==after
 shutil.rmtree(base)
 print('DISPOSABLE_DIRECTORY_REMOVED',not base.exists(),flush=True)
'''
# Keep the harness literal and avoid any interpretation of document escapes.
r65_program=r65_program.replace('SOURCE',repr(r54_stage+'/bin')).replace('DOC',repr(r64_stage+'/source/resources/vis-docs/gateway-service.md'))
compile(r65_program,'nonroot-service-check','exec')
r65_start=await start_remote_release_check('sdk-agent-nonroot-service-t65','python3 -c '+shlex.quote(r65_program))
print(r65_start.stdout)