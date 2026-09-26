r = await shell(op="run", commands=[f"grep -o 'content-visibility[^};]*' {B}/public/assets/index-ZC9VG1V_.css | sort | uniq -c; grep -o 'contain-intrinsic-size[^};]*' {B}/public/assets/index-ZC9VG1V_.css | sort | uniq -c"])
print(r["commands"][0]["stdout"])
print(await ev("var a=document.querySelector('[aria-label=Transcript] article'); return {cls:a.className, cv:getComputedStyle(a).contentVisibility, cis:getComputedStyle(a).containIntrinsicSize, contain:getComputedStyle(a).contain, h:Math.round(a.getBoundingClientRect().height)};"))
