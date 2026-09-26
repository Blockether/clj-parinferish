root=Path(session['workspace']['root']); cp=root/'apps/vis-companion/src/lib/artifacts.test.ts'; sp=root/'test/com/blockether/vis/internal/gateway/state_test.clj'; r1=await patch(cp,[{'from':'251:a6f│   });','replace':'''  });

  // Regression, session 00000000-0000-4000-8000-000000000023: host Activity receipts
  // filled the produced-artifacts gallery even though they belong inside execution traces.
  it("keeps host Activity receipts out of the produced-artifacts gallery", () => {
    const activity = {
      index: 7,
      iteration_id: "activity-iteration",
      filename: "activity.live.ndjson",
      media_type: LIVE_ARTIFACT_MEDIA,
      classification: "activity",
      turn: 2,
    };
    const transcript = [{
      id: "activity-turn",
      iterations: [{ id: "activity-iteration", attachments: [activity] }],
    }] as TranscriptTurn[];

    expect(collectArtifacts(transcript)).toEqual([]);
    expect(artifactsFromIndex([activity])).toEqual([]);
  });'''}]); r2=await patch(sp,[{'from':'1029:652│                           (att {:filename "late.png"','to':'1033:274│                                 :version 3})])','replace':'''                          ;; Host Activity is durable transcript state, not a produced artifact.
                           (att {:filename "activity.live.ndjson"
                                 :classification :activity
                                 :media-type "application/vnd.vis.live+ndjson"
                                 :turn-soul-id "soul-2"
                                 :iteration-id "i9"
                                 :tool-call-id "call_activity"})
                           (att {:filename "late.png"
                                 :turn-soul-id "soul-2"
                                 :iteration-id "i9"
                                 :tool-call-id "call_D"
                                 :version 3})])'}]); print(r1); print(r2)