print(patch(project_root_path/'apps/vis-companion/src/screens/sessions/SessionProjectGroups.tsx,[{'from':'1314:fb3','to':'1316:53b','replace':'''    } catch {
      setMoveFailure('That did not reach the machine. Try again.');
      requestAnimationFrame(() => moveChoicesRef.current?.querySelector('button')?.focus());
    } finally {'''},{'from':'1372:c7c','to':'1375:f4f','replace':'''        moveToGroup: (session: Session) => {
          if (moving.current) return;
          setMoveFailure(null);
          setMovingId((held) => (held === session.id ? null : session.id));
        },'''},{'from':'1380:345','to':'1383:22f','replace':'''  // The project's only group is the one this row is under, so there is no other
  // destination to choose: Ungroup acts directly. A refused move leaves the row put.'''} ,{'from':'1442:fa0','replace':'''            }}
            onBlur={(event) => {
              if (!moving.current && !event.currentTarget.contains(event.relatedTarget)) {
                setMovingId(null);
              }
            }}'''}]))