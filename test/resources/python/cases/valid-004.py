ui = (ROOT/"src/components/ui.tsx").read_text().split("\n")
print("\n".join(f"{i+1}: {ui[i]}" for i in range(script_start:=760, 790)))
print("...")
print("\n".join(f"{i+1}: {ui[i]}" for i in range(830, 872)))