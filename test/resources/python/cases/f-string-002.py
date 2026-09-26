print(patch(lanterna_path/'src/test/java/com/googlecode/lanterna/terminal/html/HtmlTerminalRendererTest.java',[{'from':'31:e31','replace':'''        terminal.newTextGraphics().putString(0, 2, "VISIBLE");
        terminal.newTextGraphics().putString(0, 20, "OUTSIDE");
        String html = terminal.renderHtml(12);
        assertTrue(html.contains("VISIBLE"));
        assertFalse(html.contains("OUTSIDE"));
        assertTrue(html.contains("<textarea id=\\"input\\" disabled tabindex=\\"-1\\""));
        assertTrue(html.contains("role=\\"region\\""));'''}]))
print(await repl_eval({'language':'clojure','id':'nrepl:~/vis/apps/vis-tui','code':f'''(do (require '[com.blockether.vis.tui.capture :as cap])
(cap/shot! {{:cols 40 :rows 20 :trim false
:paint! (fn [{{:keys [screen]}}] (com.blockether.vis.tui.html-backend-test/paint-activity-review! screen (com.blockether.vis.tui.html-backend-test/activity-review-rows "failed") {{}}))
:out {json.dumps(str(review_dir21/'native.png'))}}))'''}))
await design_browser('set viewport 393 852',quiet=True)
await design_browser('open "http://127.0.0.1:6006/iframe.html?id=components-doc-frame--opened&viewMode=story"',quiet=True)
await design_browser('wait iframe',quiet=True)
print(await design_js('''(()=>{const bytes=Uint8Array.from(atob('''+json.dumps(base64.b64encode(review_bytes21).decode())+'''),c=>c.charCodeAt(0));window.__STORYBOOK_ADDONS_CHANNEL__.emit('updateStoryArgs',{storyId:'components-doc-frame--opened',updatedArgs:{url:URL.createObjectURL(new Blob([bytes],{type:'text/html'})),name:'activity-tui.html'}});return true;})()'''))
await design_browser('wait --fn '+shlex.quote('document.querySelector("iframe")?.title === "activity-tui.html"'),quiet=True)
await design_browser('screenshot '+shlex.quote(str(review_dir21/'viewer-phone.png')),quiet=True)
print(attach(review_dir21/'native.png',filename='viewer-native.png',audience='model'))