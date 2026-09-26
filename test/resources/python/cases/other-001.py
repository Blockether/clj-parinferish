print(patch(project_root_path/'apps/vis-companion/src/screens/sessions/SessionProjectGroups.stories.tsx,[{'from':'372:013','replace':''},{'from':'377:d3e','to':'379:77e','replace':'''    await expect(
      projectName.getBoundingClientRect().left - projectChevron.getBoundingClientRect().left,
    ).toBe(16);
    await expect(groupChevron.getBoundingClientRect().left).toBe(projectName.getBoundingClientRect().left);
    await expect(groupName.getBoundingClientRect().left - groupChevron.getBoundingClientRect().left).toBe(
      16,
    );'''}]))