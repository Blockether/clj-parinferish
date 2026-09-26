root=Path(session['workspace']['root']); p=root/'apps/vis-companion/src/screens/SessionScreen.tsx'; out=await patch(p,[{'from':'2686:c51│     const RESUME_AT_END_AFTER_MS = 60_000;','to':'2695:a6f│     });','replace':'''    const RESUME_AT_END_AFTER_MS = 60_000;
    let wakeGeometryFrame: number | null = null;
    const reconcileWakeGeometry = () => {
      wakeGeometryFrame = null;
      const viewport = scrollRef.current;
      if (!viewport) return;
      // WebKit can emit a scroll while its background viewport is collapsed, then
      // restore the exact bottom before foregrounding without emitting the matching
      // scroll. Geometry is authoritative on wake: never leave a stale “Latest”
      // offer pointing at the pixel already under the reader.
      if (isAtBottom(viewport)) {
        followingRef.current = true;
        aimedEndRef.current = viewport.scrollHeight;
        correctedTopRef.current = viewport.scrollTop;
        forgetReadingPosition(sid);
      }
      syncJump();
    };
    const stopWake = onWake(({ awayMs }) => {
      inflightSince = null;
      subscriptions.resync();
      reconcileWakeGeometry();
      // Native resume can precede WebKit's final viewport restoration by one paint.
      // Measure once more after that paint rather than trusting the suspended box.
      if (wakeGeometryFrame !== null)
        window.cancelAnimationFrame(wakeGeometryFrame);
      wakeGeometryFrame = window.requestAnimationFrame(reconcileWakeGeometry);
      if (awayMs >= RESUME_AT_END_AFTER_MS) {
        resumePinRef.current = true;
        pinToEnd();
      }
      void reconcile();
    });''},{'from':'2759:48b│     return () => {','to':'2764:f5e│     };','replace':'''    return () => {
      cancelled = true;
      window.clearInterval(timer);
      if (wakeGeometryFrame !== null)
        window.cancelAnimationFrame(wakeGeometryFrame);
      stopWake();
      stopReady();
    };'''},{'from':'2765:bca│   }, [','to':'2773:24f│   ]);','replace':'''  }, [
    client,
    sid,
    loadTranscript,
    subscriptions,
    pinToEnd,
    syncJump,
    acceptQueueBacklog,
    adoptRunningTurn,
  ]);'''}]); print(out)