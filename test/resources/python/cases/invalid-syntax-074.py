> 
# 3. shell.test.ts
sp=base+"src/lib/shell.test.ts"; t=open(sp).read()
i=t.index("  it('pairs from Preferences and gives Machines a way back'")
t=t[:i]+"""  // Regression, user report ("it should be this search more subtle and looking more
  // connected to our designs"): the field was a hand-rolled white-filled rounded box,
  // taller and louder than every 32px flat control beside it. It is `SearchField` now —
  // the app's own control, on `Button`'s exact metrics, paper at rest.
  it('wears the app\\'s own search control, on the button rhythm', () => {
    expect(appSource).toContain('<SearchField');
    expect(appSource).not.toMatch(/<label className="mx-3 flex h-8/);
  });

"""+t[i:]
t=t.replace("""expect(appSource).toContain('import { Button, IconButton } from "./components/ui";');""","""expect(appSource).toContain('import { Button, SearchField } from "./components/ui";');""")
t=t.replace("""expect(appSource).toContain('aria-label="Search sessions on every machine"');""","""expect(appSource).toContain('label="Search sessions on every machine"');""")
open(sp,"w").write(t)

# 4. header-layout.test.mjs
edit(base+"scripts/header-layout.test.mjs", [
 ("""    const search = app.indexOf('aria-label="Search sessions on every machine"');""",
  """    const search = app.indexOf('label="Search sessions on every machine"');"""),
 ("""    expect(classes(openingTag(app, 'Search sessions on every machine'))).toContain(
      'flex-1',
    );""",
  """    // The field is the app's own `SearchField` now, so the call site may only
    // POSITION it — the face (Button's box, paper at rest) belongs to the component.
    expect(app).toContain('<SearchField');
    expect(app).toContain('className="mx-3 flex-1"');"""),
])

# 5. ui.test.tsx
tp=base+"src/components/ui.test.tsx"; x=open(tp).read().rstrip()+"""

// Regression, user report ("it should be this search more subtle and looking more
// connected to our designs"): the search box was rounder, taller and whiter than the
// controls it sat beside — a white slab on paper that carries no other box at rest.
describe('SearchField', () => {
  const field = uiSource.slice(uiSource.indexOf("export const SearchField"));

  it('wears Button\\'s own face and only lights up when focused', () => {
    expect(uiSource).toContain('export const SearchField');
    // Same box as `Button`: flat corners, its 32px face, its type step.
    expect(field).toContain('rounded-none');
    expect(field).toContain('h-8');
    expect(field).toContain('mouse:h-6');
    expect(field).not.toContain('rounded ');
    // Paper at rest; the input surface and the ring arrive with the caret.
    expect(field).toContain('bg-transparent');
    expect(field).toContain('focus-within:bg-input');
    expect(field).toContain('focus-within:border-accent');
  });
});
"""
open(tp,"w").write(x)
print("tests done")