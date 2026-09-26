sh1 = await shell(proof_chain(320, 700, "narrow.png"), cwd=str(companion))
o1 = await sh1.wait(180); print("320:", o1['out'][-460:])
sh2 = await shell(proof_chain(1440, 600, "desktop.png"), cwd=str(companion))
o2 = await sh2.wait(180); print("1440:", o2['out'][-460:])
collapse = " && ".join([spel_cmd(S,"open http://127.0.0.1:4177"), spel_cmd(S,"set viewport 390 320"),
  spel_cmd(S, f"eval-js {shlex.quote(mount_js(TEXT, b64))}"),
  spel_cmd(S, 'find first "[data-speech-header] button[aria-label=Play]" click'),
  spel_cmd(S, f"eval-js {shlex.quote(sleep_js)}"),
  spel_cmd(S, 'find first "[data-disclosure-toggle]" click'),
  spel_cmd(S, f"screenshot {shlex.quote(str(out_dir/'mobile-collapsed.png'))}"),
  spel_cmd(S, f"eval-js {shlex.quote(metrics_js.replace('const p=sec.querySelector(','const p=sec.querySelector('))}")}"])
sh3 = await shell(collapse, cwd=str(companion)); o3 = await sh3.wait(180); print("collapsed:", o3['out'][-460:])