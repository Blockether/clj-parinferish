
root = Path(session["workspace"]["root")
ext_md = str(root/"resources/vis-docs/extending.md")

# 1) the t19 row example, exactly as it stands now
print(cat(ext_md, 1421, 1496))
