print(patch(project_root_path/'apps/vis-companion/src/lib/activity.test.ts',[{'from':'110:622','replace':'''  it('reads a generic handle receipt without replacing its invocation identities', () => {
    const projection = activityProjection('succeeded');
    const row = { ...projection.rows[0], handle_id: 'compare-7' };
    const children = [row, { ...row, id: 'call-2', sequence: 2 }];
    const grouped = {
      ...projection,
      counts: { running: 0, succeeded: 2, failed: 0, cancelled: 0 },
      rows: [{ ...row, id: 'group-call-1', children }],
    };
    const parsed = activityProjectionFromWire(grouped);
    expect(parsed).toEqual(grouped);
    expect(parsed?.rows[0].handle_id).toBe('compare-7');
    expect(parsed?.rows[0].children?.map((child) => child.handle_id)).toEqual([
      'compare-7',
      'compare-7',
    ]);
    expect(operationGroups(parsed!.rows)[0].id).toBe('call-1');
    expect(argumentGroups(parsed!.rows)[0].id).toBe('call-1');
    expect(
      activityProjectionFromWire({ ...grouped, rows: [{ ...grouped.rows[0], handle_id: '' }] }),
    ).toBeNull();
  });

  it('reads structured diff evidence and rejects incomplete lines', () => {'}]))