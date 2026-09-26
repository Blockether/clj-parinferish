print(patch(root/'apps/vis-companion/scripts/touch-density.test.mjs', [{'from':'178:76d','to':'190:a6f','replace':'''  it('keeps the smallest type step compact and refuses overrides', () => {
    expect(typeSteps(readFileSync(join(src, 'index.css'), 'utf8'))[0]).toEqual({
      name: 'text-chip',
      size: 8,
      lineHeight: 14,
    });
    expect(overridesLeading('<p className="text-chip leading-snug" />')).toEqual(['leading-snug']);
    expect(overridesLeading('<p className="sm:leading-5 text-[13px]" />')).toEqual([
      'sm:leading-5',
      'text-[13px]',
    ]);
    expect(overridesLeading('<p className="text-chip tracking-wider" />')).toEqual([]);
  });'''}])))