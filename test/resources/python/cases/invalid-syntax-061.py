> 
idx = [i for i,l in enumerate(win) if re.search(r"(Exception|error|FAIL|Syntax|Caused)", strip(l))]
print("first fail idx:", idx[:5])
print("\n".join(f"{i}| {strip(win[i])[:220]}" for i in range(max(0,idx[0]-25), min(len(win), idx[0]+40))))