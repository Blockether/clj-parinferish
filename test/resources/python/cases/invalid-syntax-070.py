> 
# fleet.ts
ft=Path("/home/user/vis/apps/vis-companion/src/lib/fleet.ts").read_text()
old="""/** Hand the order to the name dialog, WITH the machine the fork happens on. */"""
new="""/**
 * Take that answer back: the machine question again, with the order still open and
 * every other answer in it untouched.
 */
export function startFlowUnpick(flow: StartFlow): StartFlow {
  return flow.step === 'menu' ? { ...flow, on: null } : flow;
}

/** Hand the order to the name dialog, WITH the machine the fork happens on. */"""
assert ft.count(old)==1
Path("/home/user/vis/apps/vis-companion/src/lib/fleet.ts").write_text(ft.replace(old,new))

# App.tsx
ap="/home/user/vis/apps/vis-companion/src/App.tsx"
at_=Path(ap).read_text()
a=at_.split("\n")
print("\n".join(f"{i:5} {a[i-1]}" for i in range(948,965)))