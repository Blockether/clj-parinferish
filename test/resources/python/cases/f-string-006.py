h = await shell(f"cd {APP} && git show HEAD:src/components/ui.tsx | grep -n 'pageCount}' | head -20")
print(out(h,60))
