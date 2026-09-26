async def gh(*args):
    sh = await shell("gh " + " ".join(args))
    buf = []
    for _ in range(120):
        lines = await sh.logs()
        if lines:
            buf.append(lines)
        st = sh.status
        if isinstance(st, str) or (isinstance(st, dict) and st.get("done")):
            break
        await sh.wait(1)
    return "".join(buf)

print(await gh("issue view 157 --repo Blockether/vis --json number,title,state,body,labels"))