> 
# richer document pane for D so the desktop split is not half empty
v_d = v_d.replace(
 '<p><b>Plan state.</b> v4 · next task 2 · owner: this session.</p></div></div>',
 '<p><b>Plan state.</b> v4 · next task 2 · owner: this session.</p>'
 '<h4 class="caps" style="margin-top:14px">Spec</h4>'
 '<p>Carry a finished session into a fresh one without losing the transcript, the open files or the running '
 'turn&rsquo;s context. A handover is written when a session ends and read when a new one starts.</p>'
 '<p class="small">Non-goals: cross-account handover, editing a snapshot by hand.</p>'
 '<h4 class="caps" style="margin-top:14px">Decisions</h4>'
 '<p>The snapshot is gateway-side and immutable. Re-running the transcript on restore was rejected for cost and '
 'non-determinism.</p>'
 '<h4 class="caps" style="margin-top:14px">Open questions</h4>'
 '<p><b>Q1</b> Does a handover carry attachments, or only the transcript? <span class="small">task 2</span></p>'
 '<p><b>Q2</b> Who expires a snapshot — gateway or companion? <span class="small">task 4</span></p>'
 '</div></div>')
VARIANTS[3] = VARIANTS[3][:5] + (v_d,)
variants_html = "".join(variant_card(*v) for v in VARIANTS)
page = (HTML.replace("__TOKENS__", TOKENS).replace("__CSSLAB__", CSS_LAB).replace("__CSSAPP__", CSS_APP)
            .replace("__NAV__", nav_html).replace("__TAGS__", tags).replace("__BRIEFCARDS__", briefcards)
            .replace("__VARIANTS__", variants_html).replace("__IVJSON__", IV_JSON).replace("__JS__", JS))
out.write_text(page, encoding="utf-8")
print(len(page))
