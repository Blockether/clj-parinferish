root=Path(session['workspace']['root']); p=root/'.vis/extensions/gh.py'; spec=root/'src/com/blockether/vis/internal/human_input/spec.clj'; la=root/'apps/vis-companion/src/components/LiveArtifact.tsx'
r=await patch(p,[{'from':'509:e64','to':'510:2c0','replace':'''def _tick(since):
    return FAST_TICK_S if since < BACKOFF_AFTER_S else SLOW_TICK_S


def superseded_shape(shape):
    """Settle unfinished snapshot rows when this watch yields to a newer run."""
    settled = dict(shape)
    settled["rows"] = [
        {
            **row,
            "cells": [row["cells"][0], "superseded", row["cells"][2]],
            "tone": "idle",
        }
        if row.get("tone") == "running"
        else row
        for row in shape.get("rows") or []
    ]
    settled["steps"] = [
        {**step, "tone": "idle"} if step.get("tone") == "running" else step
        for step in shape.get("steps") or []
    ]
    settled["active_step_ids"] = []
    settled["score"] = [
        {**stat, "value_text": "0"} if stat.get("id") == "queued" else stat
        for stat in shape.get("score") or []
    ]
    return settled''},{'from':'762:ea1','to':'779:8ff','replace':'''                    if superseded:
                        run_id = str(superseded.get("databaseId") or "?")
                        settled = superseded_shape(shape)
                        push_changes(view, shape, settled)
                        shape = settled
                        view["run"].set(
                            f"Superseded by newer run {run_id}",
                            tone="idle",
                            detail="Stopped watching obsolete work after a newer commit started",
                        )
                        _show_activity(
                            view,
                            [
                                f"– Stopped: newer run {run_id} started for this workflow"
                            ],
                            activity_history,
                        )
                        _show_focus_logs(
                            view, shape, log_of, log_cache, FAILED_TAIL_LINES
                        )
                        target = str(superseded.get("url") or "")
                        if target:
                            view["links"].add("newer-run", "Newer run", target)
                        break''},{'from':'863:48a','to':'863:48a','replace':'        return view.close(reason="superseded" if superseded else None, summary=_summary(shape, superseded))'}]); print(r)
r2=await patch(spec,[{'from':'188:b31','to':'194:bc6','replace':'''(def live-reasons
  "Why a view ended. CLOSED, and the only vocabulary an extension branches on."
  {"completed" :completed
   "interrupted" :interrupted
   "timeout" :timeout
   "undeliverable" :undeliverable
   "failed" :failed
   "superseded" :superseded})'''}]); print(r2)
r3=await patch(la,[{'from':'48:a66','to':'54:f5e','replace':'''const REASON_WORDS: Record<string, string> = {
  completed: "finished",
  interrupted: "stopped by hand",
  timeout: "timed out",
  undeliverable: "lost its surface",
  failed: "failed",
  superseded: "superseded",
};'''}]); print(r3)