print(edit_task_file('apps/vis-companion/src/components/AgentTeam.tsx', [{'from': '161:a99', 'to': '165:b98', 'replace': "        const setting = await client.setting('subagents', controller.signal).catch(() => null);\n        if (controller.signal.aborted) return;\n        setEnabled(setting?.enabled === true);\n        if (setting?.enabled !== true) return;\n        const rows = await client.agents(sid, controller.signal);"}]))
print(edit_task_file('apps/vis-companion/src/components/AgentTeam.test.tsx', [{'from': '145:4f0', 'replace': "    expect(setting).toHaveBeenCalledWith('subagents', expect.any(AbortSignal));\n    setting.mockRejectedValue(new Error('Settings unavailable'));\n    await act(async () => { vi.advanceTimersByTime(5000); });\n    expect(screen.queryByRole('button', { name: /Agents:/ })).toBeNull();\n    expect(agents).toHaveBeenCalledTimes(1);"}]))
print(edit_task_file('apps/vis-companion/src/screens/SettingsScreen.stories.tsx', [{'from': '143:000', 'replace': '''
/** Experimental workflows require a separate, explicit opt-in on each machine. */
export const ExperimentalFeatures: Story = {
  args: { gateways: STORY_GATEWAYS.slice(0, 1) },
  play: async ({ canvasElement }) => {
    const page = within(canvasElement.ownerDocument.body);
    for (const label of ['Subagents', 'Improve', 'Plan before coding']) {
      const toggle = await page.findByRole('switch', { name: `${label}: off` });
      await expect(toggle).not.toBeChecked();
      const row = toggle.closest('.flex.items-center.justify-between')!;
      await expect(within(row as HTMLElement).getByText('Experimental')).toBeVisible();
      await userEvent.click(toggle);
      await waitFor(() => expect(toggle).toBeChecked());
      await userEvent.click(toggle);
      await waitFor(() => expect(toggle).not.toBeChecked());
    }
  },
};
'''}]))
print(cat('test/com/blockether/vis/internal/config/experimental_test.clj', 1, 170))
print(cat('test/com/blockether/vis/internal/gateway/agents_test.clj', 1, 150))
print(grep({'query': ['Improve', 'improve_mode', 'experimental'], 'paths': ['resources/vis-docs'], 'context': 1}))
print(cat('resources/vis-docs/configuration.md', 520, 577))
print(cat('resources/vis-docs/working-with-plans.md', 1, 56))
print(cat('resources/vis-docs/council.md', 1, 36))
print(cat('resources/vis-docs/python-sdk.md', 405, 440))
print(ap ropos('spel'))