> 
s = re.sub(r'\^Context ', '', s)
s = re.sub(r'\^Value ', '', s)
s = s.replace("(instance? Value ", "(fn? ")
print([l for l in s.split("\n") if "Value" in l or "Context/" in l or "Engine" in l][:20])
