prompt_path = root / "src" / "com" / "blockether" / "vis" / "internal" / "prompt.clj"
prompt_patch = patch(
    prompt_path,
    [{
        "from": "336:1f9",
        "to": "337:2e3",
        "replace": """    \"- Code: `grep` locates unknown code: `grep({\\\"query\\\": [needles], \\\"paths\\\": [scopes], \\\"context\\\": 4})`.\\n\"
    \"  It ORs terms and answers anchored TEXT, never a map. `context` counts surrounding lines on EACH side of a match\\n\"
    \"  (`1` means one before and one after; default 4). A hit IS a `patch` argument.\\n\""" 
    }],
)
print(prompt_patch)