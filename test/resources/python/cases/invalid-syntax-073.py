> /dev/null
# 3. language_surface.clj run-tests: unwrap the run-outside-tool-wall call
pp=Path(R+"src/com/blockether/vis/internal/foundation/language_surface.clj"); L=pp.read_text().split("\n")
print("\n".join(f"{i+1}: {L[i]}" for i in range(1017, 1032)))
