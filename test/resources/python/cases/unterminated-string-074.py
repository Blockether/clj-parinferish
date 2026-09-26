root=Path(session['workspace']['root'])
p=root/'extensions/channels/vis-channel-tui/test/com/blockether/vis/ext/channel_tui/chat_test.clj'
print(await patch(p,[{'from':'541:59a','to':'541:59a','replace':'                                       "text" "ponder"\n                                       "cumulative" "pondering"})]));