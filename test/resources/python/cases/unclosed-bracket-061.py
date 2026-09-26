root=Path(session['workspace']['root'])
reads=await gather(
 cat(root/'src/com/blockether/vis/internal/human_input.clj',1700,2050),
 cat(root/'src/com/blockether/vis/internal/human_input.clj',2440,2520),
 cat(root/'src/com/blockether/vis/internal/human_input/live_sink.clj',1,280),
 grep({'query':['liveInterrupt','interruptLive','live-view-interrupt','interrupt-live','live/interrupt'], 'paths':[str(root/'apps/vis-companion/src/lib'),str(root/'apps/vis-companion/src')]}),
 grep({'query':['settle-live','interrupt-live','live-interrupt','interrupt!'], 'paths':[str(root/'src/com/blockether/vis')]})
for i,x in enumerate(reads): print(f'\n---{i}---\n{x}')