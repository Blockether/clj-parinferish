import urllib.request, json as _json

def gh(url):
    req = urllib.request.Request(url, headers={"User-Agent": "vis-diag", "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=30) as f:
        return _json.loads(f.read().decode())

try:
    latest = gh("https://api.github.com/repos/Blockether/vis/releases/latest")
    print("latest release tag:", latest["tag_name"], "| name:", latest.get("name"))
    names = [a["name"] for a in latest.get("assets", [])]
    print("companion assets:", [n for n in names if "companion" in n] or "NONE")
    print("asset count:", len(names))
except Exception as e:
    print("latest error:", type(e).__name__, e)

try:
    rels = gh("https://api.github.com/repos/Blockether/vis/releases?per_page=15")
    print("\nrecent releases (tag | prerelease | companion dmg assets):")
    for rel in rels:
        comp = [a["name"] for a in rel.get("assets", []) if "vis-companion" in a["name"] and a["name"].endswith(".dmg")]
        print(f"  {rel['tag_name']:<28} pre={rel['prerelease']!s:<5} {comp}")
except Exception as e:
    print("list error:", type(e).__name__, e)