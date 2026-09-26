print(await council.publish('Native build completed exit 0 in 5m33s; target/vis.jar and target/vis are ready (pinned CE25.3.4.1, stamp54534fb-dirty). Starting native attachment+draft checkpoint, linked-report and goal helper tests now; they read binary only, do not rewrite jar. Companion contrast correction/rerun is also active. You can inspect/freeze jar, but my checks still consume CPU briefly. No dependency/audit edits by me; new deps pin will not be represented in this already-built image.', kind='informational', ping=['00000000-0000-4000-8000-000000000015','00000000-0000-4000-8000-000000000016'], thread_id=1798))
native_results = await gather(
    run_tests({'language':'clojure','aliases':['test-native'],'ns':'com.blockether.vis.native-binary-test/native-attachment-review-capability-test'}),
    run_tests({'language':'clojure','aliases':['test-native'],'ns':'com.blockether.vis.native-binary-test/native-linked-report-delivery-test'}),
    run_tests({'language':'clojure','aliases':['test-native'],'ns':'com.blockether.vis.native-binary-test/native-goal-continuation-test'})
)
for label, result in zip(['attachment and draft', 'linked report', 'goal helper'], native_results):
    print(label, result)
ui_sections = re.split(r'(?=^--- (?:a/|/dev/null))', ui_review_payload['patch'], flags=re.M)
print('\n'.join(s for s in ui_sections if any('+++ b/apps/vis-companion/src/'+p+'\n' in s for p in ['lib/diff.ts','lib/artifacts.ts','lib/types.ts','lib/gallery.tsx']))))