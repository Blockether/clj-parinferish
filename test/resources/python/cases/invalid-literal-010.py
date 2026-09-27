replacement = '''  it('justifies reasoning on each side of an authored line break', async () => {
    const first = 'I am looking at how the Python and Clojure extensions report activity so a reader can see the right message as it runs';
    const second = 'and the next thought continues here with enough words to fill the narrow column without losing this line break.';
    const view = render(<ThinkingBand>{`${first}\\n${second}`}</ThinkingBand>);
    await settle();
    const lines = [...view.container.querySelectorAll('section p')];
    expect(lines).toHaveLength(2);
    expect(lines.map((line) => line.hasAttribute('data-justice'))).toEqual([true, true]);
    expect(lines.map((line) => line.textContent)).toEqual([first, second]);
  });'''
print(patch(project_root_path/'apps/vis-companion/src/components/JustifiedProse.test.tsx,[{'from':'130:5ae','to':'142:a6f','replace':replacement}]))