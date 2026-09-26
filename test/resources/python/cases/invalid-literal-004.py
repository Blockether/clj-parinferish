print(patch(project_root_path/'apps/vis-companion/src/screens/sessions/SessionProjectGroups.stories.tsx,[{'from':'612:78c','replace':'// The next project takes both sticky levels away and shows Groups even with no bands.'},{'from':'655:828','replace':'''    const nextGroups = within(next as HTMLElement).getByText('Groups').parentElement!;
    const nextSessions = within(next as HTMLElement).getByText('Sessions').parentElement!;'''},{'from':'696:8c7','to':'697:c2c','replace':'''    await expect(nextGroups.getBoundingClientRect().top).toBeCloseTo(nextProject.getBoundingClientRect().bottom, 0);
    await expect(nextSessions.getBoundingClientRect().top).toBeGreaterThan(nextProject.getBoundingClientRect().bottom);
    pane.scrollTop += nextSessions.getBoundingClientRect().top - nextProject.getBoundingClientRect().bottom + 40;
    await frame();
    await expect(nextSessions.getBoundingClientRect().top).toBeCloseTo(nextProject.getBoundingClientRect().bottom, 0);'''}]))