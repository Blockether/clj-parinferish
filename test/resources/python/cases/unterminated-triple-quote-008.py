renames = await gather(
    patch(str(loop_test_path), [{"from": "907:6f3", "to": "907:6f3", "replace": "  session-provider-kickoff-headers-test"}]),
    patch(str(loop_path), [{"from": "6854:6ca", "to": "6856:8d4", "replace": """  \"Decorate one immutable router snapshot with session-scoped provider headers.
   Configured and credential-derived headers are retained; a provider kickoff hook
   owns any same-named key it contributes. The shared process router is never mutated.\"""}]),
)
print("\n".join(renames))