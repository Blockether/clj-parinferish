(ns build
  "Build/deploy for clj-parinferish. One small jar: three compiled Java classes,
   one Clojure namespace, and a namespaced VERSION resource."
  (:require [clojure.java.io :as io]
            [clojure.string :as str]
            [clojure.tools.build.api :as b]
            [deps-deploy.deps-deploy :as dd]))

(def lib 'com.blockether/parinferish)

(def declared-version
  "This library's own release number. `resources/VERSION` is the single source of
   truth; the release tag mirrors it."
  (str/trim (slurp "resources/VERSION")))

(def version
  "VERSION env (set by CI from the release tag) wins; otherwise
   `declared-version` tagged `-SNAPSHOT` for local builds."
  (let [v (System/getenv "VERSION")]
    (cond
      (and v (str/starts-with? v "v")) (subs v 1)
      v v
      :else (str declared-version "-SNAPSHOT"))))

(defn- check-version!
  "Refuse to build artifacts whose version sources disagree: the tag names the
   Clojars coordinate, `resources/VERSION` is stamped into the namespaced
   `com/blockether/parinferish/VERSION` resource, and drift there ships a lying
   version string."
  []
  (let [release (str/replace version #"-SNAPSHOT$" "")]
    (when-not (= release declared-version)
      (throw (ex-info (format "version mismatch: release %s, resources/VERSION %s"
                              release declared-version)
                      {:release release :declared declared-version})))))

(def class-dir "target/classes")
(def jar-file (format "target/%s.jar" (name lib)))
(def basis (delay (b/create-basis {:project "deps.edn"})))

(defn clean [_] (b/delete {:path "target"}))

(defn compile-java
  "Compiles java/ into target/classes. `--release 21` is the floor consumers can
   count on; the classes carry no reflection and no resources, so native-image
   needs no configuration for them."
  [_]
  (b/javac {:src-dirs ["java"]
            :class-dir class-dir
            :basis @basis
            :javac-opts ["--release" "21" "-Xlint:all"]}))

(defn- pom-data []
  [[:description "Parinfer for Clojure source, in pure Java — a linear-time rewrite of parinferish."]
   [:url "https://github.com/Blockether/clj-parinferish"]
   [:licenses [:license [:name "MIT License"] [:url "https://opensource.org/licenses/MIT"]]]
   [:scm [:url "https://github.com/Blockether/clj-parinferish"]
    [:connection "scm:git:https://github.com/Blockether/clj-parinferish.git"]
    [:developerConnection "scm:git:ssh://git@github.com/Blockether/clj-parinferish.git"]]])

(defn jar [_]
  (check-version!)
  (clean nil)
  (compile-java nil)
  (b/write-pom {:class-dir class-dir
                :lib lib
                :version version
                :basis @basis
                :src-dirs ["src" "java"]
                :pom-data (pom-data)})
  (b/copy-dir {:src-dirs ["src"] :target-dir class-dir})
  ;; NAMESPACED version resource so it can never collide with another library's
  ;; root VERSION on a shared classpath.
  (let [vfile (io/file class-dir "com" "blockether" "parinferish" "VERSION")]
    (io/make-parents vfile)
    (spit vfile version))
  (b/jar {:class-dir class-dir :jar-file jar-file})
  (println "Built:" jar-file "version:" version))

(defn deploy [_]
  (jar nil)
  (dd/deploy {:installer :remote :artifact jar-file :pom-file (b/pom-path {:lib lib :class-dir class-dir})}))

(defn install [_]
  (jar nil)
  (dd/deploy {:installer :local :artifact jar-file :pom-file (b/pom-path {:lib lib :class-dir class-dir})}))
