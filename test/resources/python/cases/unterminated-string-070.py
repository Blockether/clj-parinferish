screen_edits=[
 {'from':'5003:418','to':'5013:ba8','replace':'''(defn- create-terminal!
  [opts]
  (cond (:html-terminal opts) (:html-terminal opts)
        (:html? opts)
        (let [terminal (-> (HtmlTerminal/builder)
                           (.title "Vis terminal")
                           (.defaultForeground t/text-fg)
                           (.defaultBackground t/terminal-bg)
                           (.build))]
          (announce-html-terminal! terminal)
          terminal)
        :else
        (UnixTerminal. @vis/tty-in @vis/tty-out (Charset/defaultCharset) (terminal-ctrl-c-behaviour))))},
 {'from':'5163:00b','to':'5166:a1f','replace':'''  "Start the fullscreen chat TUI. Blocks until user quits.
   Optional `opts` map:
     :session-id     uuid-string  - resume a specific session
     :resume         true         - resume the latest :tui session
     :html-terminal  HtmlTerminal - use a transport owned by the gateway"'''}]
print(patch(screen,screen_edits))
html_repl=r'''(deftest html-terminal-construction-and-arguments-test
  (testing "the complete Vis screen can swap only its Terminal backend"
    (let [announced
          (atom nil)

          terminal
          (with-redefs-fn {#'screen/announce-html-terminal!
                           (fn [value]
                             (reset! announced (.getUrl ^HtmlTerminal value)))}
            #(#'screen/create-terminal! {:html? true}))]

      (try (is (instance? HtmlTerminal terminal))
           (is (= (.getUrl ^HtmlTerminal terminal) @announced))
           (is (.startsWith ^String @announced "http://127.0.0.1:"))
           (finally (.close ^HtmlTerminal terminal)))))
  (testing "a gateway can inject the same terminal without a second HTTP server"
    (with-open [terminal (-> (HtmlTerminal/builder) (.embeddedServer false) (.build))]
      (is (identical? terminal (#'screen/create-terminal! {:html? true :html-terminal terminal})))
      (is (false? (.hasEmbeddedServer terminal)))))
  (is (= {:resume true :html-out "view.html"}
         (#'screen/parse-args ["--resume" "--html-out" "view.html"] core/tui-html-usage))))'''
print(patch(html_test,[{'from':'47:afb','to':'63:3a9','replace':html_repl}]))
core=tui/'src/com/blockether/vis/ext/channel_tui/core.clj'
core_edits=[
 {'from':'83:1f6','to':'86:d86','replace':'''(defn html-channel-main
  "Lazy browser-terminal entry point over the same Lanterna application."
  [args]
  ((require-screen-channel-main 'com.blockether.vis.ext.channel-tui.screen/html-channel-main) args))

(defn tui-routes-contribution
  "Resolve the gateway browser transport only when the gateway asks for routes."
  []
  ((or (requiring-resolve 'com.blockether.vis.ext.channel-tui.gateway/routes-contribution)
       (throw (ex-info "TUI gateway route contribution did not resolve" {})))))

(def channel-contributions
  (update builtin-hooks/channel-contributions
          :gateway.slot/http-routes
          (fnil conj [])
          {:id :tui/http :fn tui-routes-contribution}))'''},
 {'from':'110:d5c','to':'110:d5c','replace':'     :ext/channel-contributions channel-contributions}))'}]
print(patch(core,core_edits))
server_file=wt/'src/com/blockether/vis/internal/gateway/server.clj'
server_edits=[
 {'from':'3937:0ac','to':'3942:64f','replace':'''  ;;    :routes            (fn [token] reitit-route-data)
  ;;    :open-uris         #{"/ui" ...} ; reachable without auth
  ;;    :protocol-open-uris #{"/ui" ...} ; browser routes with no API header
  ;;    :request-authed-fn (fn [request token] bool)   ; extra auth carrier
  ;;    :on-unauthorized   (fn [request] ring-response) ; custom 401 for :prefix
  ;;    :on-not-found      (fn [request] ring-response) ; custom 404 for :prefix
  ;;    :form-params?      true}        ; urlencoded form parsing under :prefix'''},
 {'from':'4060:4b7','to':'4080:b31','replace':'''(defn- wrap-protocol
  "Wire-protocol gate (§3). API clients must advertise a compatible version.
   A contributed browser route may name exact `:protocol-open-uris` because native
   navigation, EventSource and media requests cannot attach API protocol headers."
  [handler contribs]
  (fn [request]
    (let [uri (str (:uri request))
          browser-uri? (some #(contains? (or (:protocol-open-uris %) #{}) uri) contribs)]
      (if (or (contains? protocol-open-uris uri)
              (str/starts-with? uri "/docs")
              browser-uri?)
        (handler request)
        (let [v (protocol/gateway-verdict request)]
          (if (:is-compatible v)
            (handler request)
            (let [{:keys [title summary remedy]} (protocol/explain v)]
              (json-response 426
                             {:error {:type "incompatible_protocol"
                                      :message (str title " — " summary)
                                      :title title
                                      :remedy remedy}
                              :protocol (protocol/handshake)
                              :compatibility v}))))))))'''} ,
 {'from':'4358:cf6','to':'4358:cf6','replace':'    (wrap-protocol contribs)'}]
print(patch(server_file,server_edits))