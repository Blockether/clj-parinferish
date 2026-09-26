p=project_root_path/'apps/vis-companion/src/screens/sessions/SessionProjectGroups.tsx'; print(patch(p,[{'from':'12:cf1','replace':"  type ReactNode,\n  type Ref,"},{'from':'173:5af','to':'177:545','replace':'''/**
 * A PLACE THAT TAKES A DRAGGED ROW. It lights while the pointer is over it, so the
 * reader sees where the session lands before letting go. A group's whole area files the
 * row it takes; the ungrouped sessions area takes one back OUT of its group.
 */''},{'from':'194:354','replace':'''      onDragLeave: (event: DragEvent<HTMLElement>) => {
        if (event.currentTarget.contains(event.relatedTarget as Node | null)) return;
        setIsOver(false);
      },'''},{'from':'205:000','replace':'''/** The band, rows and open space of one set all take the same drop. */
function SessionDropArea({
  onDropSession,
  areaRef,
  minHeight,
  children,
}: {
  onDropSession?: (sid: string) => void;
  areaRef?: Ref<HTMLDivElement>;
  minHeight?: number;
  children: (isOver: boolean) => ReactNode;
}) {
  const { isOver, dropProps } = useSessionDrop(onDropSession);
  return (
    <div
      ref={areaRef}
      style={{ minHeight }}
      className={isOver ? 'bg-white/10' : undefined}
      {...dropProps}
    >
      {children(isOver)}
    </div>
  );
}
'''},{'from':'218:fe4','replace':'  isOver = false,'},{'from':'242:5af','to':'249:229','replace':'''  /** Whether the ungrouped set is offering to take a carried row. */
  isOver?: boolean;
}) {'''},{'from':'251:ad5','to':'254:03e','replace':'''    <div className="flex min-h-14 items-center gap-2 border-y border-edge py-1 pl-4 mouse:min-h-10">'''},{'from':'295:229','replace':'  isCreating = false,'},{'from':'311:7a8','to':'320:12f','replace':'''}) {
  return (
    <div className="flex items-stretch border-t border-edge">'''},{'from':'1395:3e0','to':'1397:ac2','replace':'''                return (
                  <SessionDropArea
                    key={band.id}
                    onDropSession={(sid) => dropSession(sid, band.id)}
                  >
                    {() => (
                      <>
                        <GroupBand'''},{'from':'1408:6e3','to':'1412:532','replace':'''                          isCreating={creating?.at === creationKey(base, root, band.id)}
                        />
                        {isBandOpen && held.map(row)}
                      </>
                    )}
                  </SessionDropArea>
                );'''},{'from':'1414:ad5','to':'1423:0f2','replace':'''            <SessionDropArea
              areaRef={sessionSetRef}
              minHeight={
                pageCount > 1 && pageFootprint?.layout === pageLayout
                  ? pageFootprint.height
                  : undefined
              }
              onDropSession={hasGroups ? (sid) => dropSession(sid, null) : undefined}
            >
              {(isOver) => (
                <>
                  {/* A band files into itself; this area takes a session back out. */}'''},{'from':'1432:ea9','to':'1435:3c0','replace':'''                    isOver={isOver}
                  />
                  {listed.map(row)}
                </>
              )}
            </SessionDropArea>'''}]))