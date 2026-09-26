choice_tests, gateway_region = await gather(
    grep({"query": ["ChoiceCell", "leading action", "panel gutter", "grid-cols-[3rem"], "border-r"], "paths": [str(companion / "src" / "components" / "ui.test.tsx")]}),
    cat(str(companion / "src" / "screens" / "SettingsScreen.tsx"), 1220, 1310),
)
print(choice_tests)
print(gateway_region)