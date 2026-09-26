r=await patch(str(wt/'deps.edn'),[{'from':'71:1a1','replace':'   :git/sha "3051a9cf7a3a69a69f8e82394afe01fcb98ec310"}])
print(r)