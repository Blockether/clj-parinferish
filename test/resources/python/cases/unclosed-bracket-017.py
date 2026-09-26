root = Path(session["workspace"]["root"])
nav = await patch(root/"apps/vis-companion/src/components/SessionNavigator.tsx", [
 {"from":"42:075", "replace":"/** The session list's pull gesture takes over the app bar with the action a release would take. */"},
 {"from":"50:aa3", "replace":"      className={`pointer-events-none fixed inset-x-0 top-[env(safe-area-inset-top)] z-40 flex min-h-12 items-center justify-center gap-2 border-b border-dialog-edge font-mono text-meta transition-[translate] duration-150 motion-reduce:transition-none ${"}
        isShown ? 'translate-y-0' : '-translate-y-full'\n      } ${isArmed ? 'bg-accent-surface text-accent-ink' : 'bg-level-project text-dialog-hint'}`}"}
])
screen = await patch(root/"apps/vis-companion/src/screens/SessionsScreen.tsx", [
 {"from":"2153:18a", "to":"2154:17d", "replace":"        {/* The pull reports itself where the search door lives: it takes over the app bar\n            until the finger releases, instead of inserting a new band above the list. */"}
])
story = await patch(root/"apps/vis-companion/src/components/ui.stories.tsx", [
 {"from":"744:6cb", "replace":"          <div className=\"relative h-16 w-full transform-gpu overflow-hidden bg-level-project\">"}
])
print(str(nav)+"\n"+str(screen)+"\n"+str(story))