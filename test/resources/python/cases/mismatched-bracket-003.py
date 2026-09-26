print(patch(project_root_path/'apps/vis-companion/src/screens/sessions/SessionProjectGroups.test.tsx, [{'from':'684:952','replace':"    await user.clear(field);\n    await user.type(field, 'Existing{Enter}');"}, {'from':'660:a6f','replace':'''  });

  it('saves an inline group rename when the field loses focus', async () => {
    let current = WALLET_GROUP;
    const client = machine({
      listSessionGroups: vi.fn(async () => wall([current])),
      updateSessionGroup: vi.fn(async (_id: string, change: { name: string }) => {
        current = { ...current, ...change };
        return current;
      }),
    });
    const { user } = mount(client);
    await band('Wallet work');
    await user.click(screen.getByRole('button', { name: 'Actions for Wallet work' }));
    await user.click(within(sheet(`Groups in ${ROOT}`)).getByText('Rename group'));
    const field = screen.getByRole('textbox', { name: 'Rename Wallet work' });
    await user.clear(field);
    await user.type(field, 'Invoices');
    await user.tab();
    await waitFor(() => expect(client.updateSessionGroup).toHaveBeenCalledWith(WALLET, { name: 'Invoices' }));
    expect(await screen.findByRole('button', { name: 'Collapse Invoices' })).toBeVisible();
  });'''}, {'from':'811:85b','replace':'''  it('keeps inline move choices visible and retryable after a failed filing', async () => {
    const assignSessionGroup = vi.fn()
      .mockRejectedValueOnce(new Error('Offline'))
      .mockImplementation(async (sid: string, gid: string) => ({ ...LOOSE, id: sid, group_id: gid }));
    const { user } = mount(machine({ assignSessionGroup }));
    const wallet = await band('Wallet work');
    await user.click(within(strip(wallet.closest('[data-project-root]') as HTMLElement, LOOSE.id)).getByText('Move to...'));
    const choices = screen.getByRole('group', { name: `Move ${LOOSE.title} to group` });
    await user.click(within(choices).getByRole('button', { name: 'Wallet work' }));
    expect(await within(choices).findByRole('status')).toHaveTextContent('Try again.');
    expect(screen.queryByRole('dialog', { name: `Groups in ${ROOT}` })).toBeNull();
    await user.click(within(choices).getByRole('button', { name: 'Wallet work' }));
    await waitFor(() => expect(assignSessionGroup).toHaveBeenCalledTimes(2));
    await waitFor(() => expect(screen.queryByRole('group', { name: `Move ${LOOSE.title} to group` })).toBeNull());
  });

  // More than one destination remains an inline choice, not another sheet.'''}]))