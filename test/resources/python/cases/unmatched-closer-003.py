fr = focused_story.wait(10)
print(fr['status'], fr['exit'])
print('\n'.join(line for line in fr['out'].splitlines() if 'Test Files' in line or 'Tests ' in line or 'FAIL ' in line or ' ui.stories.tsx (' in line or 'humanInput.stories.tsx (' in line)[-30:]))