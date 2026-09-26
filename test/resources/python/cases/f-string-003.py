sh2 = await shell(f"cd {companion} && npm run test:storybook 2>&1 | grep 'color-contrast' | sed 's/ · {.*//' | sort | uniq -c | sort -rn | head -20")
print(sh2.wait(900).logs(-30)["out"][-2500:])
