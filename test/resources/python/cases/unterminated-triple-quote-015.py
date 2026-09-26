updates = await gather(
 patch(str(test_root / "foundation/rewind_test.clj"), [
   {"from":"720:c6d", "to":"722:6af", "replace":"""             (it \"exports op hooks for foundation-core\"
                 (expect (seq rw/op-hooks)))"""}
 ]),
 patch(str(root / "src/com/blockether/vis/internal/foundation/shell.clj"), [
   {"from":"2:98b", "to":"5:f7a", "replace":"""  \"Foundation-core's shell implementation. Bound only when the user-owned `shell`
   toggle is ON (default ON; flip it OFF in Settings or in `vis.yml` via
   `toggles: {shell: false}` to drop the tools). The OS process jail is the
   containment layer while active."""},
   {"from":"59:3c7", "to":"62:5b3", "replace":"""   The `shell` toggle is registered HERE and owned by Vis core. It closes the
   MODEL's door only: an installed extension keeps its own trusted process boundary
   (`vis.shell`, `subprocess`), which the toggle does not gate.\"""}
 ])
)
for x in updates: print(x)