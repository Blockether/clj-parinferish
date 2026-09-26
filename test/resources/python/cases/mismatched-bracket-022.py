jpol=str(rt/"src/java/com/blockether/vispython/JailPolicy.java")
seat=str(rt/"src/java/com/blockether/vispython/Seatbelt.java")
skin=str(rt/"src/clj/com/blockether/vis_python_runtime.clj")
print(patch(jpol,[
 {"from":"19:125","to":"22:442","replace":" * caller names only the session's directories. {@code unixConnect} contains exact\n * local control sockets a child may dial. {@code inbound} ports are additionally\n * reachable on every interface; loopback listeners are always allowed.\n * {@code keychain} opens the OS credential store: the Security services and\n * keychain databases on macOS, the D-Bus session bus on Linux."},
 {"from":"24:410","to":"26:f4a","replace":"public record JailPolicy(List<String> readWrite, List<String> readOnly, List<String> denyRead,\n    List<String> denyWrite, List<String> denyExec, List<String> unixConnect, Egress egress,\n    List<Integer> inbound, boolean keychain) {"},
 {"from":"48:55b","replace":"    denyExec = strings(denyExec);\n    unixConnect = strings(unixConnect);"}
]))
print(patch(seat,[
 {"from":"113:641","to":"114:bde","replace":"    out.append(network(policy));\n    List<String> sockets = JailPolicy.realPaths(policy.unixConnect());\n    if (!sockets.isEmpty()) {\n      out.append(\"(allow network-outbound (remote unix-socket\");\n      for (String socket : sockets) {\n        out.append(\"(path \ ".trim()).append(quote(socket)).append(")");\n      }\n      out.append(\"))\");\n    }\n    return out.toString();"}
]))
print(patch(skin,[
 {"from":"96:334","to":"98:3c7","replace":"   `{:proxy <port>}` — the one loopback port sockets may reach — `:unix-connect`\n   lists exact local control sockets, `:inbound` lists ports additionally exposed\n   on every interface (loopback listeners are always allowed), and `:keychain?`\n   opens the OS credential store."},
 {"from":"99:4d4","to":"101:96d","replace":"  [{:keys [read-write read-only deny-read deny-write deny-exec unix-connect network inbound keychain?]}]\n  (JailPolicy. (vec read-write) (vec read-only) (vec deny-read) (vec deny-write) (vec deny-exec)\n               (vec unix-connect) (egress network) (mapv int inbound) (boolean keychain?)))"}
]))
print(patch(rjt,[
 {"from":"43:f3f","to":"48:d07","replace":"    (let [p (runtime/jail-policy {:read-write [\"/a\" \"\" \"/a\" nil]\n                                  :unix-connect [\"/tmp/control.sock\" \"\" \"/tmp/control.sock\"]\n                                  :inbound [80 80 443]})]\n      (is (= [\"/a\"] (.readWrite p)))\n      (is (= [] (.readOnly p)))\n      (is (= [\"/tmp/control.sock\"] (.unixConnect p)))\n      (is (= [80 443] (.inbound p)))\n      (is (= JailPolicy$Egress/OFF (.egress p)))\n      (is (false? (.keychain p))))"},
 {"from":"90:924","replace":"          (is (str/includes? (compile {:network :open}) \"(allow network*)\"))))\n      (testing \"one exact Unix control socket is reachable after the network deny\"\n        (let [socket (str root \"/control.sock\")\n              _ (spit socket \"\")\n              p (compile {:unix-connect [socket]})]\n          (is (str/includes? p (str \"(remote unix-socket(path \\\"\" socket \"\\\"))\")))\n          (is (< (str/index-of p \"(deny network*)\")\n                 (str/index-of p \"(remote unix-socket\")))))"}
]))