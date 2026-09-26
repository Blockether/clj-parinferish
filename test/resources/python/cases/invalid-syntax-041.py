> more = [("✓",f"CI (macos-latest) · {n}",OKC) for n in
        ["Set up job","Checkout","Setup GraalVM CE 25.1.3","Cache maven deps","clojure -M:test",
         "Build native image","Smoke test binary","Upload artifact","Post job cleanup","Complete job",
         "Post Setup GraalVM CE 25.1.3","Post Cache maven deps"]]
for mk,lab,col in more:
    if y > SH+60: break
    mono(dA,CX0,y,[(mk+" ",col),(lab,col)],sz=CHIP); y+=LC
print("left now to", y)
