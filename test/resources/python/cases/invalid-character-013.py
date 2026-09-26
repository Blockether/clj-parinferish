« = None
Lp3=Path(p).read_text().split("\n")
for rng in [(1710,1732),(4678,4692),(4793,4805),(4820,4850),(4890,4900)]:
    print("---")
    print("\n".join(f"{i+1}: {Lp3[i]}" for i in range(rng[0],rng[1])))
