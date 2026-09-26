print(patch(project_root_path / 'apps/vis-companion/src/components/ChatContent.tsx',[
 {'from':'476:4d3','replace':'        role={frameless ? "group" : "region"}'},
 {'from':'539:ae0','replace':'  onOpenAttachment,\n  headingLevel,'},
 {'from':'546:435','replace':'  onOpenAttachment?: OpenAttachment;\n  /** Embedded result dividers share the level below their enclosing step. */\n  headingLevel?: 1 | 2 | 3 | 4 | 5 | 6;'},
 *[{'from':anchor,'replace':f'            <h{level}\n              aria-level={{headingLevel}}'} for level,anchor in [(1,'615:e05'),(2,'622:e06'),(3,'629:e07'),(4,'636:e08'),(5,'643:e09'),(6,'650:e0a')]]))
print(patch(project_root_path / 'apps/vis-companion/src/components/ActivityPanel.tsx',[
 {'from':'594:3a8','replace':'              <Markdown key={index} compact nested headingLevel={5}>'}]))
companion_format = await shell('npm exec --yes --package=prettier@3.6.2 -- prettier --write src/components/ActivityPanel.tsx src/components/ActivityPanel.test.tsx src/components/ActivityPanel.stories.tsx',{'cwd':str(project_root_path / 'apps/vis-companion'),'id':'activity-companion-format'})
print(companion_format.wait(30))
companion_checks = await shell('npm test -- src/components/ActivityPanel.test.tsx src/lib/activity.test.ts src/components/ui.test.tsx src/components/ChatContent.test.tsx && npm run lint && npm run build && npm run test:storybook',{'cwd':str(project_root_path / 'apps/vis-companion'),'id':'activity-companion-checks'})
print(companion_checks.logs(-5))
artifact_options={'root':str(review_dir),'configFile':str(project_root_path / 'apps/vis-companion/vite.config.ts'),'build':{'outDir':str(companion_build_dir),'emptyOutDir':True,'assetsInlineLimit':100000000,'rolldownOptions':{'input':str(review_dir / 'companion.html'),'output':{'codeSplitting':False}}}}
artifact_build_js='import { build } from "vite"; const options='+json.dumps(artifact_options)+'; options.plugins=[{name:"activity-review-source-scan",enforce:"pre",transform(source,id){if(id==='+json.dumps(str(project_root_path / 'apps/vis-companion/src/index.css'))+')return source+'+json.dumps('\n@source "'+str(project_root_path / 'apps/vis-companion/src')+'";\n@source "'+str(project_root_path / 'apps/vis-companion/.storybook')+'";')+';}}]; await build(options);'
companion_artifact_build=await shell('node --input-type=module -e '+shlex.quote(artifact_build_js),{'cwd':str(project_root_path / 'apps/vis-companion'),'id':'activity-artifact-build'})
print(companion_artifact_build.logs(-5))
tui_review = await shell('clojure -M:html-review ' + shlex.quote(str(review_dir / 'activity-tui.html')) + ' 40', {'cwd':str(project_root_path / 'apps/vis-tui'),'id':'activity-tui-review'})
print(tui_review.logs(-5))
print(lint_code({'language':'clojure','cwd':str(project_root_path / 'apps/vis-tui'),'paths':['src/com/blockether/vis/tui/render.clj','test/com/blockether/vis/tui/render_test.clj','test/com/blockether/vis/tui/html_backend_test.clj','build/vis_tui/review.clj']}))