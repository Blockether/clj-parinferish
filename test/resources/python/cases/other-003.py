print(patch(project_root_path/'apps/vis-companion/src/components/SessionNavigator.tsx,[{'from':'61:07d','replace':''}])); print(patch(project_root_path/'apps/vis-companion/src/screens/SessionsScreen.pullToSearch.test.tsx,[{'from':'34:5b8','to':'47:a6f','replace':'''  // Regression: an idle hint anchored below the iPhone safe area used to peek
  // through it, painting an opaque strip beside the island.
  it('clips the idle hint at the top of the app bar', async () => {
    const view = fleet(() => {});
    try {
      await listOf(view);
      const hint = view.getByText('Pull to search');
      expect(hint).toHaveClass('-translate-y-full');
      expect(hint.parentElement).toHaveClass('overflow-hidden');
      expect(hint.parentElement).toHaveClass('top-[env(safe-area-inset-top)]');
    } finally {
      view.restore();
      view.unmount();
    }
  });'''},{'from':'68:a6f','to':'69:b00','replace':'''  });

  it('opens the search page when the pull is released', async () => {'''},{'from':'96:20c','to':'97:9f7','replace':'''      expect(hint().parentElement?.className).toContain('fixed');
      expect(hint().parentElement?.className).toContain('top-[env(safe-area-inset-top)]');'''}])); print(patch(project_root_path/'apps/vis-companion/src/lib/pull-to-search.ts',[{'from':'115:82f','to':'118:820','replace':''' * POSITION IS THE WHOLE REVEAL: the overlay frame around the band is
 * `overflow-hidden` at the safe-area edge, so a band parked one height up is
 * clipped instead of covering the iPhone status area. Fading it in as well
 * only lays a ghost of the header under the band coming down to cover it.'''}]))