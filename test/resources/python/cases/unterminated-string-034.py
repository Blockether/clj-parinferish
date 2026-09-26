inspection_prompt_candidate = inspection_prompt_candidate.replace('Arguments | `import inspect; print(inspect.signature(fn))`; never use `doc()` just for call shape.', 'Arguments | `import inspect; print(inspect.signature(fn))`; not `doc()`.')
inspection_candidate_literals = inspection_prompt_candidate.split('(def ^:private CORE_SYSTEM_PROMPT', 1)[1].split('(defn', 1)[0]
print('Candidate prompt length:', len(''.join(json.loads(s, strict=False) for s in re.findall(r'"(?:\\.|[^"\\])*"', inspection_candidate_literals)[1:])))
print(patch(project_root_path / 'test/com/blockether/vis/internal/context/prompt_test.clj', [
    {'from': '464:6d8', 'replace': '                               "Discover missing/changed facts only"))))'},
    {'from': '467:a53', 'replace': '        (expect (str/includes? text "operational failures use known recovery"))))'},
    {'from': '474:346', 'replace': '          "Semantics | Narrow `doc(name)` only for unknown preconditions, effects, units, retries and limits"))'},
    {'from': '494:8a1', 'replace': '                   "Arguments | `import inspect; print(inspect.signature(fn))`; not `doc()`"'},
    {'from': '522:39d', 'replace': '         ["Narrow `doc(name)` only for unknown preconditions, effects, units, retries and limits"'},
    {'from': '553:06b', 'replace': '          "Inspect shape before indexing or accessing attributes"
          "use keys/types or public `dir()` names, not assumed `__dict__`"
          "On error inspect, then adapt"'}
]))
print(await run_tests({'language': 'clojure', 'paths': ['test/com/blockether/vis/internal/context/prompt_test.clj']}))