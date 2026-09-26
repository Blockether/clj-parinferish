res=await gather(
 patch(str(root/'src/com/blockether/vis/internal/theme.clj'),[
  {'from':'505:156','replace':'   :ai-role-fg [93 109 0]'},
  {'from':'506:d46','replace':'   :status-ok [93 109 0]'},
  {'from':'526:432','replace':'   :code-success-fg [93 109 0]'},
  {'from':'560:276','replace':'   :footer-spinner-fg [93 109 0]'},
  {'from':'571:1be','replace':'   :close-button-hover-fg [239 136 134]'},
  {'from':'601:944','replace':'   :status-bad [239 136 134]'},
  {'from':'616:06c','replace':'   :code-error-fg [239 136 134]'},
  {'from':'651:34a','replace':'   :footer-error-fg [239 136 134]'})
 ]),
 patch(str(app/'src/components/ui.tsx'),[
  {'from':'732:c94','replace':'          className="flex flex-1 items-center justify-center bg-panel-2 font-mono text-meta font-bold uppercase tracking-[0.08em] text-dialog-hint transition-colors duration-150 hover:bg-hover hover:text-fg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-accent/60 motion-reduce:transition-none"'}
 ])
)
print('\n'.join(map(str,res)))
print(await run('clojure -X:companion-themes',secs=180,tail=12,cwd=str(root)))