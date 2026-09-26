g = await git({"commands":[["diff","--","apps/vis-companion/src/screens/SessionScreen.tsx","src/com/blockether/vis/internal/loop.clj"],
                          ["diff","--","src/com/blockether/vis/internal/foundation/mcp/core.clj","test/com/blockether/vis/internal/foundation/acp_test.clj","apps/vis-companion/src/lib/reader-gesture.ts","apps/vis-companion/src/components/ChatContent.tsx"]])
print(g["commands"][0]["stdout"][:3000])
print("=========FOREIGN=========")
print(g["commands"][1]["stdout"][:3000])