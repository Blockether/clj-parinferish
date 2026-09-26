print(patch(project_root_path/'apps/vis-companion/src/screens/sessions/SessionProjectGroups.test.tsx',[{'from':'227:981','to':'231:d28','replace':'''    expect(within(groupButton).getByText('Wallet work')).toHaveClass(
      'text-ui', 'font-medium', 'text-dialog-hint',
    );
    expect([...wallet.querySelectorAll('[data-session-id]')].map((row) =>
      row.getAttribute('data-session-id'),
    )).toEqual([ROWS[0].id, ROWS[1].id]);'''}])); print(patch(project_root_path/'apps/vis-companion/src/screens/sessions/SessionProjectGroups.stories.tsx',[{'from':'367:7ce','replace':'''    // The unpaged Groups strip is as tall as Sessions with its own actions.''},{'from':'371:c5a','replace':'''    const projectName = page.getByText(fixture.name);'''},{'from':'376:df2','replace':'''    await expect(
      groupName.getBoundingClientRect().left - projectName.getBoundingClientRect().left,
    ).toBeGreaterThanOrEqual(16);'''},{'from':'388:b59','replace':'''      await expect(getComputedStyle(header).borderBottomColor).toBe(
        getComputedStyle(band).borderTopColor,
      );'''},{'from':'390:7ce','replace':'''    // Keep full-size action targets even when the captions get smaller.'''}]));