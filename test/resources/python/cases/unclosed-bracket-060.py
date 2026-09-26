root=Path(session['workspace']['root'])
reads=await gather(
 cat(root/'apps/vis-companion/src/components/LiveArtifact.tsx',1,260),
 cat(root/'apps/vis-companion/src/components/LiveArtifact.test.tsx',1,430),
 grep({'query':['interruptLive','interrupt_live','live/interrupt','onInterrupt','artifact'], 'paths':[str(root/'apps/vis-companion/src'),str(root/'src/com/blockether/vis/internal')]}),
 grep({'query':['append-event!','sink','artifact-path','artifact_path','live-result'], 'paths':[str(root/'src/com/blockether/vis/internal/human_input.clj')]})
print('\n---COMPONENT---\n',reads[0])
print('\n---TESTS---\n',reads[1])
print('\n---CALLS---\n',reads[2])
print('\n---ENGINE---\n',reads[3])