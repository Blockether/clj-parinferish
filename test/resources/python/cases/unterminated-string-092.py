sub(P,1197,1207,[("""  "Tool-call arguments reach svar either already parsed (anthropic
   `tool_use.input`, gemini `functionCall.args` — carried through the envelope
   parse UNINTERNED by `keywordize-response`) or as a JSON string (OpenAI chat
   `function.arguments`, responses `function_call.arguments`). Both end up as
   the SAME string-keyed map, at every depth, so `:input` is uniform across
   every wire.

   There is no keyword→string repair pass here, deliberately: svar never
   interns tool arguments in the first place (see `RAW_TOOL_ARG_KEYS`), so a
   caller reads plain strings and nothing has to be un-done."''',
""""Tool-call arguments reach svar either already parsed (anthropic
   `tool_use.input`, gemini `functionCall.args` — a response body is parsed
   with `:key-fn identity`, so they arrive uninterned) or as a JSON string
   (OpenAI chat `function.arguments`, responses `function_call.arguments`).
   Both end up as the SAME string-keyed map, at every depth, so `:input` is
   uniform across every wire.

   There is no keyword→string repair pass here, deliberately: svar never
   interns a provider response at all, so a caller reads plain strings and
   nothing has to be un-done."'''.replace('""""','  "'))])
show2(P,1197,1210)
