sh = await shell('''cd /home/user/vis && S=diag-review-4 && \
spel --session $S set viewport 1280 800 && \
spel --session $S --content-boundaries open "file:///home/user/vis/apps/vis-companion/.review-dist/settings-diagnostics-review.html" && \
spel --session $S wait --text "Log retention" && \
spel --session $S --content-boundaries snapshot -i -c 2>&1 | sed -n '1,70p'''')
await sh.wait(120)
print(sh.logs(80))
sh.stop()