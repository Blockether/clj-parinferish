(ns build
  "Build/deploy for clj-parinferish. One small jar: three compiled Java classes
   and one Clojure namespace."
  (:require [clojure.string :as str]
            [clojure.tools.build.api :as b]
            [deps-deploy.deps-deploy :as dd]))

(def lib 'com.blockether/parinferish)

(def declared-version
  "This library's own release number. The repo-root `PARINFERISH_VERSION` file is
   its single source of truth; the release tag mirrors it."
  (str/trim (slurp "PARINFERISH_VERSION")))

(def version
  "What an artifact is stamped with. CI exports PARINFERISH_VERSION from the
   release tag and publishes that exact number; every other build is a
   `-SNAPSHOT`, so a local install cannot shadow a release in ~/.m2."
  (if-let [tag (System/getenv "PARINFERISH_VERSION")]
    (str/replace tag #"^v" "")
    (str declared-version "-SNAPSHOT")))

(defn- check-version!
  "Refuse to build artifacts whose version sources disagree: the tag names the
   Clojars coordinate and `PARINFERISH_VERSION` is what the pom declares, so drift
   between them publishes a version nobody asked for."
  []
  (let [release (str/replace version #"-SNAPSHOT$" "")]
    (when-not (= release declared-version)
      (throw (ex-info (format "version mismatch: tag %s, PARINFERISH_VERSION %s"
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
  ;; MIT asks that the notice travel with every copy, so the jar carries the
  ;; license text itself — an audit of the artifact alone still sees the terms.
  (b/copy-file {:src "LICENSE" :target (str class-dir "/META-INF/LICENSE")})
  (b/copy-file {:src "NOTICE" :target (str class-dir "/META-INF/NOTICE")})
  (b/jar {:class-dir class-dir :jar-file jar-file})
  (println "Built:" jar-file "version:" version))

(defn deploy [_]
  (jar nil)
  (dd/deploy {:installer :remote :artifact jar-file :pom-file (b/pom-path {:lib lib :class-dir class-dir})}))

(defn install [_]
  (jar nil)
  (dd/deploy {:installer :local :artifact jar-file :pom-file (b/pom-path {:lib lib :class-dir class-dir})}))
