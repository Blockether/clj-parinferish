tui_capture_and_picker = await shell(shlex.join(['spel','--session','vis-docs-tui','screenshot',str(capture_dir/'tui-full.png')])+' && spel --session vis-docs-tui press Control+x && spel --session vis-docs-tui press s && spel --session vis-docs-tui snapshot -i -c --max-output 4000')
print(tui_capture_and_picker.wait(10))
print(ios_machine_settings.logs(-10))
ios_machine_ui = await shell('spel --session vis-docs-ios snapshot -i -c')
print(ios_machine_ui.wait(10))
gallery_specs = [
 {'key':'ios','name':'iOS','intro':'Follow the same work from your phone. Captured in the native iOS app on an iPhone simulator.','slides':[
 ('conversation','Follow a conversation','Read the answer, review checks, and keep the goal in view.','Vis on iOS showing a completed search task, its goal, and a table of example checks.'),
 ('sessions','Keep projects together','Find your sessions in a project and pick up where you left off.','Vis on iOS listing three fictional Fieldnotes sessions, with the search task starred.'),
 ('project','Explore a project','Read formatted explanations and tables without leaving the conversation.','Vis on iOS showing a tour of the fictional Fieldnotes project.')]},
 {'key':'desktop','name':'Desktop','Keep your project list beside the conversation. Captured in the desktop-sized Companion web app.','slides':[
 ('conversation','See the whole task','Follow the conversation and its goal beside your project sessions.','Desktop Vis with the Fieldnotes project sidebar and a completed search task.'),
 ('project','Find your way around','Review a project tour with source paths and a clear next step.','Desktop Vis showing a project tour and a table of fictional source directories.'),
 ('release','Plan the next step','Switch sessions to turn a release into a focused checklist.','Desktop Vis showing a fictional release checklist with verify, review, and publish steps.')]},
 {'key':'tui','name':'TUI','Stay in your terminal, with keyboard navigation and the same session history. Captured from the production terminal renderer.','slides':[
 ('conversation','Work from the terminal','Read the answer, check results, and track the completed goal.','Vis TUI showing the search task, example check results, and a completed goal.'),
 ('sessions','Switch with the keyboard','Use the session navigator to find work across your projects.','Vis TUI session navigator listing only the three fictional Fieldnotes sessions.'),
 ('project','Keep context in tabs','Open another session without losing your place.','Vis TUI with two session tabs and the fictional Fieldnotes project tour.')]}
]
gallery_markdown = ['## See Vis in action','', 'Explore each gallery with the arrow buttons, your keyboard, or a swipe. Select an', 'image to open it at full size. These screenshots use a fictional Fieldnotes project', 'in a fresh gateway and database, with new sessions and example tasks—not personal work.', '']
for spec in gallery_specs:
    key=spec['key']; label=spec['name']
    dimensions=(1206,2622) if key=='ios' else ((1280,800) if key=='desktop' else (1255,756))
    gallery_markdown += [f'<h3 id="{key}-gallery">{label}</h3>', '',spec['intro'],'',
        f'<section class="screenshot-gallery screenshot-gallery--{key}" data-screenshot-gallery role="region" aria-roledescription="carousel" aria-label="{label} screenshots">',
        f'  <div class="screenshot-gallery__track" id="{key}-slides" tabindex="0" aria-label="{label} screenshots; use Left and Right arrow keys to browse">']
    for number,(suffix,title,caption,alt) in enumerate(spec['slides'],1):
        image=f'assets/screenshots/{key}-{suffix}.png'
        gallery_markdown += [f'    <figure class="screenshot-gallery__slide" role="group" aria-roledescription="slide" aria-label="{number} of 3">',
            f'      <a class="screenshot-gallery__image" href="{image}" aria-label="Open full-size {label} screenshot: {title}">',
            f'        <img src="{image}" alt="{alt}" width="{dimensions[0]}" height="{dimensions[1]}" loading="lazy" decoding="async">',
            '      </a>',f'      <figcaption><strong>{title}</strong>{caption}</figcaption>','    </figure>']
    gallery_markdown += ['  </div>',f'  <div class="screenshot-gallery__controls" hidden>',
        f'    <button type="button" data-previous aria-controls="{key}-slides" aria-label="Previous {label} screenshot">← Previous</button>',
        '    <span role="status" aria-live="polite" aria-atomic="true">1 / 3</span>',
        f'    <button type="button" data-next aria-controls="{key}-slides" aria-label="Next {label} screenshot">Next →</button>','  </div>','</section>','']
print(patch(project_root_path/'resources/vis-docs/index.md',[{'from':'25:dbb','replace':'\n'.join(gallery_markdown)+'\n## Install'}]))
readme_gallery = ['## Screenshot galleries','','One fictional project, three ways to work. All captures use a fresh demo gateway,', 'database and sessions—no personal work. The linked galleries support buttons,', 'keyboard navigation and swiping; GitHub shows the previews below.', '', '### iOS', '', '<p>']
for suffix,title,caption,alt in gallery_specs[0]['slides']:
    readme_gallery += [f'  <a href="https://vis.blockether.com/#ios-gallery"><img src="resources/vis-docs/assets/screenshots/ios-{suffix}.png" width="220" alt="{alt}"></a>']
readme_gallery += ['</p>','','[Browse the iOS carousel →](https://vis.blockether.com/#ios-gallery)','','### Desktop','','[![Desktop Vis with the Fieldnotes project sidebar and a completed search task.](resources/vis-docs/assets/screenshots/desktop-conversation.png)](https://vis.blockether.com/#desktop-gallery)','','[Browse the desktop carousel →](https://vis.blockether.com/#desktop-gallery) ·', '[Project tour](resources/vis-docs/assets/screenshots/desktop-project.png) ·', '[Release checklist](resources/vis-docs/assets/screenshots/desktop-release.png)','','### TUI','','[![Vis TUI showing a search task, example check results, and a completed goal.](resources/vis-docs/assets/screenshots/tui-conversation.png)](https://vis.blockether.com/#tui-gallery)','','[Browse the TUI carousel →](https://vis.blockether.com/#tui-gallery) ·','[Session navigator](resources/vis-docs/assets/screenshots/tui-sessions.png) ·','[Project tour](resources/vis-docs/assets/screenshots/tui-project.png)','','## Install']
print(patch(project_root_path/'README.md',[{'from':'51:dbb','replace':'\n'.join(readme_gallery)}]))