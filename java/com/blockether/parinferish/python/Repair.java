package com.blockether.parinferish.python;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.BitSet;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/**
 * Delimiter repair for Python source: strings that never close, brackets that
 * never close or close the wrong opener, a ';' inside brackets, statements
 * glued together by ';' or by a line break that lost its backslash, stray
 * backslashes, typographic quotes, quote markers around the code, single
 * braces and fields that hold only text in f-strings, invalid escapes and
 * quotes inside a string's text that end it early.
 *
 * <p>Each round takes the first problem, tries the few edits that could fix
 * it, rescans the text after each one and keeps the edit that leaves the
 * fewest problems. It stops when nothing is left, when no edit helps, or when
 * its work budget (a small multiple of the text size) runs out, so the time
 * spent is bounded by the size of the input. The result lists every change
 * with its position in the original source; the problems of the original
 * source serve as a diagnosis when the repair cannot finish.
 *
 * <p>The repair only answers "what would make the delimiters consistent". It
 * cannot tell whether the result is valid Python: compile it before running it.
 */
public final class Repair {
    private Repair() {
    }

    /** One change the repair made, at a 1-based line and column of the original source. */
    public static final class Fix {
        public final String kind;
        public final int line;
        public final int column;
        public final String message;

        Fix(String kind, int line, int column, String message) {
            this.kind = kind;
            this.line = line;
            this.column = column;
            this.message = message;
        }

        @Override
        public String toString() {
            return message;
        }
    }

    /** One delimiter problem, at a 1-based line and column of the original source. */
    public static final class Problem {
        public final String kind;
        public final int line;
        public final int column;
        public final String message;

        Problem(String kind, int line, int column, String message) {
            this.kind = kind;
            this.line = line;
            this.column = column;
            this.message = message;
        }

        @Override
        public String toString() {
            return message;
        }
    }

    /** What a repair produced. {@code clean} means no delimiter problem is left in {@code text}. */
    public static final class Result {
        public final String text;
        public final boolean changed;
        public final boolean clean;
        public final List<Fix> fixes;
        public final List<Problem> problems;

        Result(String text, boolean changed, boolean clean, List<Fix> fixes, List<Problem> problems) {
            this.text = text;
            this.changed = changed;
            this.clean = clean;
            this.fixes = Collections.unmodifiableList(fixes);
            this.problems = Collections.unmodifiableList(problems);
        }
    }

    /** Repairs {@code source} using only its own text. */
    public static Result repair(String source) {
        return repair(source, 0);
    }

    /**
     * Repairs {@code source}. {@code errorLine} is the 1-based line where the Python compiler
     * reported a syntax error, or 0 when unknown; when the scanner finds no delimiter problem of
     * its own, it lets the repair close a bracket that a statement near that line left open.
     */
    public static Result repair(String source, int errorLine) {
        Scanner first = new Scanner(source).scan();
        List<Problem> problems = problems(first, errorLine);
        if (problems.isEmpty()) return new Result(source, false, true, new ArrayList<>(), problems);
        Work w = new Work(source, first, errorLine);
        w.run();
        String text = w.sc == first ? source : new String(w.s);
        return new Result(text, !text.equals(source), w.sc.count == 0, w.fixes, problems);
    }

    /** The delimiter problems of {@code source}, without repairing anything. */
    public static List<Problem> diagnose(String source, int errorLine) {
        return Collections.unmodifiableList(problems(new Scanner(source).scan(), errorLine));
    }

    private static final int SUSPECT = 100;
    private static final int MAX_FIXES = 32;
    private static final int MAX_PROBLEMS = 8;

    private static final int TRIPLE_QUOTE = 0;
    private static final int CLOSE_QUOTE = 1;
    private static final int ESCAPE_QUOTE = 2;
    private static final int EXTEND_TRIPLE = 3;
    private static final int SWAP_TRIPLE = 4;
    private static final int CLOSE_TRIPLE = 5;
    private static final int CLOSE_BRACKETS = 6;
    private static final int REPLACE_CLOSER = 7;
    private static final int REMOVE_CLOSER = 8;
    private static final int REMOVE_BACKSLASH = 9;
    private static final int TRIM_CONTINUATION = 10;
    private static final int NEWLINE_ESCAPES = 11;
    private static final int UNESCAPE_QUOTES = 12;
    private static final int STRAIGHT_QUOTES = 13;
    private static final int DOUBLE_BRACE = 14;
    private static final int REMOVE_BRACE = 15;
    private static final int REMOVE_MARKER = 16;
    private static final int SPLIT_STATEMENT = 17;
    private static final int RESTORE_NEWLINE = 18;
    private static final int LITERAL_BRACES = 19;
    private static final int DOUBLE_BACKSLASH = 20;
    private static final int ESCAPE_QUOTES = 21;

    private static final String[] FIX_KINDS = {
        "triple-quote", "close-quote", "escape-quote", "extend-triple-quote", "swap-triple-quote",
        "close-triple-quote", "close-brackets", "replace-closer", "remove-closer", "remove-backslash",
        "trim-continuation", "newline-escapes", "unescape-quotes", "straight-quotes", "double-brace",
        "remove-brace", "remove-marker", "split-statement", "restore-newline", "literal-braces", "double-backslash",
        "escape-quotes"};

    private static final String[] PROBLEM_KINDS = {
        "unterminated-string", "unterminated-triple-string", "unclosed-bracket", "unmatched-closer",
        "mismatched-closer", "stray-backslash", "typographic-quote", "single-brace", "semicolon-in-brackets",
        "quote-marker", "compound-after-semicolon", "lost-newline", "literal-brace", "invalid-escape",
        "text-after-string"};

    /** A candidate: a few non-overlapping edits against the current text. */
    private static final class Cand {
        final int kind;
        final int ref;
        final int ref2;
        int edits;
        int[] at = new int[2];
        int[] del = new int[2];
        String[] ins = new String[2];
        Cand then;
        long own;
        Scanner scanner;

        Cand(int kind, int ref, int ref2) {
            this.kind = kind;
            this.ref = ref;
            this.ref2 = ref2;
        }

        Cand edit(int a, int d, String i) {
            if (edits == at.length) {
                at = Arrays.copyOf(at, edits * 2);
                del = Arrays.copyOf(del, edits * 2);
                ins = Arrays.copyOf(ins, edits * 2);
            }
            at[edits] = a;
            del[edits] = d;
            ins[edits] = i;
            edits++;
            return this;
        }

        /** Edit indices by position; an insertion sorts before a deletion at the same place. */
        int[] order() {
            int[] o = new int[edits];
            for (int k = 0; k < edits; k++) o[k] = k;
            for (int k = 1; k < edits; k++) {
                int x = o[k];
                int j = k - 1;
                while (j >= 0 && (at[o[j]] > at[x] || (at[o[j]] == at[x] && del[o[j]] > del[x]))) {
                    o[j + 1] = o[j];
                    j--;
                }
                o[j + 1] = x;
            }
            return o;
        }

        char[] apply(char[] cur) {
            int len = cur.length;
            for (int k = 0; k < edits; k++) len += ins[k].length() - del[k];
            char[] t = new char[len];
            int prev = 0;
            int w = 0;
            for (int k : order()) {
                System.arraycopy(cur, prev, t, w, at[k] - prev);
                w += at[k] - prev;
                ins[k].getChars(0, ins[k].length(), t, w);
                w += ins[k].length();
                prev = at[k] + del[k];
            }
            System.arraycopy(cur, prev, t, w, cur.length - prev);
            return t;
        }

        /** Maps a position in the applied text back to the text before the edits. */
        int back(int p) {
            int shift = 0;
            for (int k : order()) {
                int a = at[k] + shift;
                if (p < a) break;
                int li = ins[k].length();
                if (p < a + li) return at[k];
                shift += li - del[k];
            }
            return p - shift;
        }
    }

    /**
     * Which quote can triple-quote the text from {@code from} to an end that only moves on: not the
     * quote the text ends with, nor one it holds three times in a row outside an escape. However
     * often the end moves, it reads each character once.
     */
    private static final class Triple {
        private final char[] s;
        private final int from;
        private final char[] quotes;
        private final int[] next = new int[2];
        private final int[] run = new int[2];
        private final boolean[] tripled = new boolean[2];

        Triple(char[] s, int from, char q) {
            this.s = s;
            this.from = from;
            this.quotes = new char[] {q, q == '\'' ? '"' : '\''};
            next[0] = from;
            next[1] = from;
        }

        /** The quote character that can triple-quote {@code [from, to)}, or 0. */
        char quote(int to) {
            for (int i = 0; i < 2; i++) {
                char t = quotes[i];
                if (to > from && s[to - 1] == t) continue;
                if (!tripled(i, to)) return t;
            }
            return 0;
        }

        /** Whether quote {@code i} appears three times in a row in {@code [from, to)}. */
        private boolean tripled(int i, int to) {
            char t = quotes[i];
            int k = next[i];
            int r = run[i];
            while (!tripled[i] && k < to) {
                char c = s[k];
                if (c == '\\') {
                    k += 2;
                    r = 0;
                } else {
                    r = c == t ? r + 1 : 0;
                    tripled[i] = r >= 3;
                    k++;
                }
            }
            next[i] = k;
            run[i] = r;
            return tripled[i];
        }
    }

    private static final class Work {
        final String original;
        final Scanner first;
        final int errorLine;
        Scanner sc;
        char[] s;
        int n;
        final List<Fix> fixes = new ArrayList<>();
        long budget;
        int logSize;
        int[] logAt = new int[8];
        int[] logDel = new int[8];
        int[] logIns = new int[8];

        int pKind;
        int pPos;
        int pAt;
        int[] pOpen;
        int pLine;

        Work(String original, Scanner first, int errorLine) {
            this.original = original;
            this.first = first;
            this.errorLine = errorLine;
            this.budget = 64L * Math.max(original.length(), 4096);
            use(first);
        }

        void use(Scanner scanner) {
            sc = scanner;
            s = scanner.s;
            n = scanner.n;
        }

        /** Applies {@code c} to the text {@code x} scanned, charges the budget for the result and
         *  scans it, reusing the scan of {@code x} away from the edits. */
        Scanner scan(Cand c, Scanner x) {
            char[] t = c.apply(x.s);
            budget -= t.length;
            int from = x.n;
            int to = 0;
            for (int k = 0; k < c.edits; k++) {
                from = Math.min(from, c.at[k]);
                to = Math.max(to, c.at[k] + c.del[k]);
            }
            return Scanner.rescan(x, t, from, Math.max(from, to));
        }

        void run() {
            long[] score = score(sc);
            Set<Long> skipped = new HashSet<>();
            int fixed = 0;
            while (fixed < MAX_FIXES && budget > 0 && pick(skipped)) {
                budget -= sc.count;
                Cand best = null;
                long[] bestScore = {score[0], score[1], -1};
                for (Cand c : candidates()) {
                    if (budget <= 0) break;
                    Scanner next = scan(c, sc);
                    long[] sc2 = c.kind == TRIPLE_QUOTE ? chained(c, next, 0)
                        : c.kind == EXTEND_TRIPLE ? extended(c, next, 0) : score(next);
                    if (less(sc2, bestScore)) {
                        best = c;
                        bestScore = sc2;
                        c.scanner = next;
                    }
                }
                if (best == null) {
                    skipped.add(key(pKind, pPos));
                    continue;
                }
                for (Cand c = best; c != null; c = c.then) accept(c);
                score = bestScore;
                skipped.clear();
                fixed++;
            }
        }

        /**
         * Scores triple-quote candidate {@code c}, applied and scanned as {@code x}, together with
         * the best conversions of the unterminated strings that open right after its closing quote on the same
         * line: consecutive multi-line values such as {@code [{'a':'...'},{'b':'...'}]}. Links the chosen
         * follow-up through {@code c.then}; the third score element counts the characters the strings take in.
         */
        long[] chained(Cand c, Scanner x, int depth) {
            long[] best = score(x);
            best[2] = c.own;
            int end = c.at[1] + 5;
            int k = firstReported(x);
            if (depth >= 4 || budget <= 0 || k < 0 || x.kind[k] != Scanner.UNTERMINATED_STRING || x.pos[k] < end
                || x.lineOf(x.pos[k]) != x.lineOf(end - 1)) {
                return best;
            }
            int tried = 0;
            for (Cand f : follow(x, k)) {
                if (f.kind != TRIPLE_QUOTE) continue;
                if (tried++ == 3 || budget <= 0) break;
                Scanner x2 = scan(f, x);
                long[] s2 = chained(f, x2, depth + 1);
                s2[2] += c.own;
                if (less(s2, best)) {
                    best = s2;
                    c.then = f;
                    f.scanner = x2;
                }
            }
            return best;
        }

        /**
         * Scores the completed closer {@code c}, applied and scanned as {@code x}, together with the best
         * completion of the triple-quoted string it leaves open: consecutive values whose closers all lost a
         * quote, as in {@code [{'a':'''...''},{'b':'''...''}]}. Links the chosen follow-up through {@code c.then}.
         */
        long[] extended(Cand c, Scanner x, int depth) {
            long[] best = score(x);
            int k = firstReported(x);
            if (depth >= 4 || budget <= 0 || k < 0 || x.kind[k] != Scanner.UNTERMINATED_TRIPLE) return best;
            int tried = 0;
            for (Cand f : follow(x, k)) {
                if (f.kind != EXTEND_TRIPLE) continue;
                if (tried++ == 4 || budget <= 0) break;
                Scanner x2 = scan(f, x);
                long[] s2 = extended(f, x2, depth + 1);
                if (less(s2, best)) {
                    best = s2;
                    c.then = f;
                    f.scanner = x2;
                }
            }
            return best;
        }

        /** The candidates for problem {@code k} of {@code x}, the text a candidate made, as if it were current. */
        List<Cand> follow(Scanner x, int k) {
            Scanner saveSc = sc;
            int saveKind = pKind;
            int savePos = pPos;
            int saveAt = pAt;
            List<Cand> out = new ArrayList<>();
            use(x);
            pKind = x.kind[k];
            pPos = x.pos[k];
            pAt = x.at[k];
            if (pKind == Scanner.UNTERMINATED_TRIPLE) unterminatedTriple(out);
            else unterminated(out);
            use(saveSc);
            pKind = saveKind;
            pPos = savePos;
            pAt = saveAt;
            return out;
        }

        /** The problem the tokenizer would report first: an unclosed opener only at the end of the text. */
        static int firstReported(Scanner x) {
            int best = -1;
            for (int k = 0; k < x.count; k++) {
                if (best < 0 || reported(x, k) < reported(x, best)) best = k;
            }
            return best;
        }

        static long reported(Scanner x, int k) {
            return x.kind[k] == Scanner.UNCLOSED ? (long) x.n + x.pos[k] : x.pos[k];
        }

        static long[] score(Scanner x) {
            long hard = 0;
            for (int k = 0; k < x.count; k++) {
                hard += x.kind[k] == Scanner.UNTERMINATED_TRIPLE ? 1 + (x.lines - x.lineOf(x.pos[k])) : 1;
            }
            return new long[] {hard, x.suspects, 0};
        }

        static boolean less(long[] a, long[] b) {
            for (int i = 0; i < a.length; i++) {
                if (a[i] != b[i]) return a[i] < b[i];
            }
            return false;
        }

        long key(int kind, int p) {
            return ((long) toOriginal(p) << 8) | kind;
        }

        long reported(int k) {
            return reported(sc, k);
        }

        boolean pick(Set<Long> skipped) {
            int best = -1;
            for (int k = 0; k < sc.count; k++) {
                if (skipped.contains(key(sc.kind[k], sc.pos[k]))) continue;
                if (best < 0 || reported(k) < reported(best)) best = k;
            }
            if (best >= 0) {
                pKind = sc.kind[best];
                pPos = sc.pos[best];
                pAt = sc.at[best];
                pOpen = sc.open[best];
                pLine = -1;
                return true;
            }
            if (first.count > 0) return false;
            for (int k = 0; k < sc.suspects; k++) {
                int l = sc.suspectLine[k];
                int[] o = sc.suspectOpen[k];
                if (skipped.contains(key(SUSPECT, sc.lineStart[l]))) continue;
                if (!near(sc, l, o, errorLine)) continue;
                pKind = SUSPECT;
                pPos = sc.lineStart[l];
                pAt = -1;
                pOpen = o;
                pLine = l;
                return true;
            }
            return false;
        }

        List<Cand> candidates() {
            List<Cand> out = new ArrayList<>();
            // First: a clean scan it ties with, such as an empty ''' ''' at the end, is the weaker repair.
            if (pKind != SUSPECT) shortTriple(out);
            switch (pKind) {
                case Scanner.UNTERMINATED_STRING -> unterminated(out);
                case Scanner.UNTERMINATED_TRIPLE -> unterminatedTriple(out);
                case Scanner.UNCLOSED -> unclosed(out);
                case Scanner.UNMATCHED -> out.add(new Cand(REMOVE_CLOSER, pPos, -1).edit(pPos, 1, ""));
                case Scanner.MISMATCHED -> mismatched(out);
                case Scanner.STRAY_BACKSLASH -> backslash(out);
                case Scanner.TYPOGRAPHIC_QUOTE -> typographic(out);
                case Scanner.SEMICOLON -> semicolon(out);
                case Scanner.MARKER -> {
                    int b = pPos;
                    int e = pPos;
                    while (e < n && (s[e] == '>' || s[e] == '\u00AB' || s[e] == '\u00BB')) e++;
                    if (e < n && s[e] == ' ') e++;
                    else if (b > 0 && s[b - 1] == ' ') b--;
                    out.add(new Cand(REMOVE_MARKER, pPos, -1).edit(b, e - b, ""));
                }
                case Scanner.COMPOUND_AFTER_SEMICOLON -> {
                    int e = pPos + 1;
                    while (e < n && (s[e] == ' ' || s[e] == '\t')) e++;
                    out.add(new Cand(SPLIT_STATEMENT, pPos, -1).edit(pPos, e - pPos, "\n" + indentOf(pPos)));
                }
                case Scanner.LOST_NEWLINE -> out.add(new Cand(RESTORE_NEWLINE, pPos, -1)
                    .edit(pPos, 1, "\n" + indentOf(pPos)));
                case Scanner.FSTRING_BRACE -> {
                    out.add(new Cand(DOUBLE_BRACE, pPos, -1).edit(pPos, 0, "}"));
                    out.add(new Cand(REMOVE_BRACE, pPos, -1).edit(pPos, 1, ""));
                }
                case Scanner.FSTRING_FIELD -> literalBraces(out);
                case Scanner.INVALID_ESCAPE -> out.add(new Cand(DOUBLE_BACKSLASH, pPos, -1).edit(pPos, 0, "\\"));
                case Scanner.TEXT_AFTER_STRING -> quotedText(out);
                default -> {
                    Cand c = moveClose(pLine, pOpen);
                    if (c != null) out.add(c);
                }
            }
            return out;
        }

        /** Escapes the quote that ended a string right before the text touching it and the quote that closes
         *  that quoted text, for every quoted word up to the real end of the string; then that first quote
         *  alone when letters surround it, as in a contraction. When the text is an 'n' that stood for a line
         *  break, restoring the break competes too. On a line whose source left a string of the same quotes
         *  open, a quote is missing rather than doubled, so the quoted words are left to the repair of that string. */
        void quotedText(List<Cand> out) {
            if (s[pPos] == 'n') {
                for (int k = 0; k < sc.count; k++) {
                    if (sc.kind[k] == Scanner.LOST_NEWLINE && sc.pos[k] == pPos) {
                        out.add(new Cand(RESTORE_NEWLINE, pPos, -1).edit(pPos, 1, "\n" + indentOf(pPos)));
                        break;
                    }
                }
            }
            char q = s[pAt];
            boolean triple = pPos - pAt >= 6 && s[pAt + 1] == q && s[pAt + 2] == q
                && s[pPos - 2] == q && s[pPos - 3] == q;
            int w = triple ? 3 : 1;
            int limit = pPos;
            if (triple) limit = n;
            else while (limit < n && s[limit] != '\n') limit++;
            int a = pPos - w;
            boolean pairs = !openOnLine(pPos, q);
            Cand c = new Cand(ESCAPE_QUOTES, pPos, a);
            while (pairs && c.edits < 32) {
                int b = delimiter(a + w, limit, q, w);
                int e = b < 0 ? -1 : delimiter(b + w, limit, q, w);
                budget -= (e >= 0 ? e : limit) - a;
                if (e < 0) break;
                c.edit(a, 0, "\\").edit(b, 0, "\\");
                if (!sc.touches(e + w)) {
                    out.add(c);
                    break;
                }
                a = e;
            }
            if (w == 1 && pPos > 1 && Character.isLetter(s[pPos - 2]) && Character.isLetter(s[pPos])) {
                out.add(new Cand(ESCAPE_QUOTE, pPos, pPos - 1).edit(pPos - 1, 0, "\\"));
            }
        }

        /** Lines of the source that leave a string open, for strings opened with ' and with ". */
        BitSet[] openLines;

        /** Whether the source left a string that opens with {@code q} open on the line holding {@code p}. */
        boolean openOnLine(int p, char q) {
            if (openLines == null) {
                openLines = new BitSet[] {new BitSet(), new BitSet()};
                for (int k = 0; k < first.count; k++) {
                    if (first.kind[k] != Scanner.UNTERMINATED_STRING) continue;
                    int o = first.pos[k];
                    while (first.s[o] != '\'' && first.s[o] != '"') o++;
                    openLines[first.s[o] == '\'' ? 0 : 1].set(first.lineOf(first.pos[k]));
                }
            }
            return openLines[q == '\'' ? 0 : 1].get(first.lineOf(toOriginal(p)));
        }

        /** The first unescaped run of {@code w} quotes {@code q} in {@code [from, limit)}, or -1. */
        int delimiter(int from, int limit, char q, int w) {
            for (int i = from; i < limit; i++) {
                if (s[i] == '\\') i++;
                else if (s[i] == q && (w == 1 || (i + 2 < limit && s[i + 1] == q && s[i + 2] == q))) return i;
            }
            return -1;
        }

        /** Doubles the '{' of an f-string field that holds no expression and the '}' that closes it, so
         *  the f-string keeps them as text; then, for fields that nest braces, every brace between them too. */
        void literalBraces(List<Cand> out) {
            char q = s[pAt];
            boolean triple = pAt + 2 < n && s[pAt + 1] == q && s[pAt + 2] == q;
            int end = -1;
            for (int p = pPos + 1, d = 0; p < n && end < 0; p++) {
                char x = s[p];
                if (x == '\\') {
                    if (p + 1 < n && s[p + 1] != '{' && s[p + 1] != '}') p++;
                } else if ((x == q && (!triple || (p + 2 < n && s[p + 1] == q && s[p + 2] == q)))
                    || (x == '\n' && !triple)) {
                    break;
                } else if (x == '{') {
                    d++;
                } else if (x == '}' && d-- == 0) {
                    end = p;
                }
            }
            Cand c = new Cand(LITERAL_BRACES, pPos, -1).edit(pPos, 0, "{");
            out.add(end < 0 ? c : c.edit(end, 0, "}"));
            if (end < 0) return;
            Cand all = new Cand(LITERAL_BRACES, pPos, -1);
            for (int p = pPos; p <= end; p++) {
                if (s[p] == '{' || s[p] == '}') all.edit(p, 0, String.valueOf(s[p]));
                else if (s[p] == '\\' && s[p + 1] != '{' && s[p + 1] != '}') p++;
            }
            if (all.edits > 2) out.add(all);
        }

        /**
         * A string earlier on the line that lost its closing quote swallows the code up to the next quote,
         * as in {@code ['a/b.clj], 'k':1}}; closes it before a bracket inside its text. When the code it
         * swallowed opens the next string, as in {@code ['a/b.tsx,[{'k':1}]}, its text ends in that code:
         * the first two such strings on the line are closed before it too.
         */
        void earlierQuote(List<Cand> out, int qp) {
            int l = sc.lineOf(qp);
            if (sc.lineDepth[l] < 0) return;
            int a1 = -1;
            int e1 = -1;
            int a2 = -1;
            int e2 = -1;
            List<Cand> ends = new ArrayList<>();
            for (int p = sc.lineStart[l]; p < qp; p++) {
                char d = s[p];
                if (d == '#') return;
                if (d == '"' || d == '\'') {
                    int e = skipString(p);
                    if (e > qp || e - p < 2 || s[e - 1] != d) return;
                    if (ends.size() < 2) endsInCode(ends, p, e);
                    a2 = a1;
                    e2 = e1;
                    a1 = p;
                    e1 = e;
                    p = e - 1;
                }
            }
            int made = swallowed(out, a1, e1, 0);
            swallowed(out, a2, e2, made);
            out.addAll(ends);
        }

        int swallowed(List<Cand> out, int a, int e, int made) {
            if (a < 0 || (a + 2 < n && s[a + 1] == s[a] && s[a + 2] == s[a])) return made;
            String qs = String.valueOf(s[a]);
            for (int x = a + 2; x < e - 1 && made < 4; x++) {
                if (")]}".indexOf(s[x]) >= 0 && s[x - 1] != ' ' && s[x - 1] != '\t') {
                    out.add(new Cand(CLOSE_QUOTE, a, -1).edit(x, 0, qs));
                    made++;
                }
            }
            return made;
        }

        /** Closes the string from {@code a} to {@code e} before the code its text ends with: a comma or an
         *  opening bracket among brackets, colons and blanks, as the {@code ,[{} of {@code 'a.tsx,[{'} or the
         *  {@code ], } of {@code 'a/b], '}. */
        void endsInCode(List<Cand> out, int a, int e) {
            if (a + 2 < n && s[a + 1] == s[a] && s[a + 2] == s[a]) return;
            int k = e - 1;
            boolean code = false;
            while (k > a + 1 && ",([{)]}: \t".indexOf(s[k - 1]) >= 0) {
                code |= ",([{".indexOf(s[k - 1]) >= 0;
                k--;
            }
            if (code && k > a + 1 && s[k - 1] != '\\') {
                out.add(new Cand(CLOSE_QUOTE, a, -1).edit(k, 0, String.valueOf(s[a])));
            }
        }

        /**
         * A triple-quoted value closed with one or two quotes, as in {@code 'replace':'''...)''},}, runs on to
         * the quotes that open the next value, so its text ends in code such as {@code 'replace':}. For each
         * such string before the problem, completes the runs of one or two of its quotes that a closing
         * bracket follows: at most eight, in the order of the text.
         */
        void shortTriple(List<Cand> out) {
            budget -= pPos;
            int made = 0;
            for (int p = 0; p < pPos && made < 8; p++) {
                char c = s[p];
                if (c == '\\') {
                    p++;
                } else if (c == '#') {
                    while (p + 1 < n && s[p + 1] != '\n') p++;
                } else if (c == '\'' || c == '"') {
                    int e = skipString(p);
                    if (e - p >= 6 && e <= pPos && s[p + 1] == c && s[p + 2] == c && s[e - 1] == c && s[e - 2] == c
                        && s[e - 3] == c && opensValue(p + 3, e - 3)) {
                        for (int k = p + 3; k < e - 3 && made < 8; k++) {
                            if (s[k] == '\\') {
                                k++;
                            } else if (s[k] == c) {
                                int r = 1;
                                while (k + r < e - 3 && s[k + r] == c) r++;
                                if (r < 3 && ")]}".indexOf(s[k + r]) >= 0) {
                                    out.add(new Cand(EXTEND_TRIPLE, p, k).edit(k + r, 0, repeat(c, 3 - r)));
                                    made++;
                                }
                                k += r - 1;
                            }
                        }
                    }
                    p = e - 1;
                }
            }
        }

        /** Whether the text in {@code [from, to)} ends, blanks aside, in code that a value follows: {@code :},
         *  {@code =}, a comma or an opening bracket. */
        boolean opensValue(int from, int to) {
            while (to > from && (s[to - 1] == ' ' || s[to - 1] == '\t')) to--;
            return to > from && ":=,([{".indexOf(s[to - 1]) >= 0;
        }
        void unterminated(List<Cand> out) {
            int qp = quoteAt(pPos);
            char q = s[qp];
            String qs = String.valueOf(q);
            int ls = sc.lineStart[sc.lineOf(qp)];
            // A triple-quoted string whose text ends with the quote: the first of four quotes ended it. Tried
            // first, since closing the string the fourth quote opened scans as clean too.
            for (int e = qp, made = 0; e >= ls && made < 2; e--) {
                if (s[e] != q) continue;
                int b = e;
                while (b > ls && s[b - 1] == q) b--;
                if (e - b == 3 && (b == 0 || s[b - 1] != '\\')) {
                    out.add(new Cand(ESCAPE_QUOTE, pPos, b).edit(b, 0, "\\"));
                    made++;
                }
                e = b;
            }
            int end = trimEnd(qp + 1, pAt);
            out.add(new Cand(CLOSE_QUOTE, pPos, -1).edit(end, 0, qs));
            int k = end;
            for (int made = 0; made < 4 && k > qp + 1 && ")]},;:".indexOf(s[k - 1]) >= 0; made++) {
                k--;
                while (k > qp + 1 && (s[k - 1] == ' ' || s[k - 1] == '\t')) k--;
                out.add(new Cand(CLOSE_QUOTE, pPos, -1).edit(k, 0, qs));
            }
            earlierQuote(out, qp);
            for (int e = qp - 1, made = 0; e > ls && made < 3; e--) {
                if (s[e] == q && Character.isLetter(s[e + 1]) && Character.isLetter(s[e - 1])) {
                    out.add(new Cand(ESCAPE_QUOTE, pPos, e).edit(e, 0, "\\"));
                    made++;
                }
            }
            Triple triple = null;
            for (int e = pAt, found = 0; e < n && found < 8; e++) {
                char c = s[e];
                if (c == '\\') {
                    e++;
                    continue;
                }
                if (c != q) continue;
                int r = 1;
                while (e + r < n && s[e + r] == q) r++;
                if (r == 1 && plausibleEnd(e + 1)) {
                    if (triple == null) triple = new Triple(s, qp + 1, q);
                    char t = triple.quote(e);
                    if (t != 0) {
                        String ttt = repeat(t, 3);
                        Cand c3 = new Cand(TRIPLE_QUOTE, pPos, e).edit(qp, 1, ttt).edit(e, 1, ttt);
                        c3.own = e - qp - 1;
                        out.add(c3);
                        found++;
                    }
                }
                e += r - 1;
            }
        }

        void unterminatedTriple(List<Cand> out) {
            int qp = quoteAt(pPos);
            char q = s[qp];
            char o = q == '\'' ? '"' : '\'';
            String qqq = repeat(q, 3);
            // A partial closer is as likely the last quote run as the first: keep the first and the last four.
            List<Cand> ends = new ArrayList<>();
            for (int e = qp + 3; e < n; e++) {
                char c = s[e];
                if (c == '\\') {
                    e++;
                } else if (c == q) {
                    int r = 1;
                    while (e + r < n && s[e + r] == q) r++;
                    if (r < 3 && plausibleEnd(e + r)) {
                        ends.add(new Cand(EXTEND_TRIPLE, pPos, e).edit(e + r, 0, repeat(q, 3 - r)));
                    }
                    e += r - 1;
                } else if (c == o && e + 2 < n && s[e + 1] == o && s[e + 2] == o) {
                    if (plausibleEnd(e + 3)) {
                        ends.add(new Cand(SWAP_TRIPLE, pPos, e).edit(e, 3, qqq));
                    }
                    e += 2;
                }
            }
            int m = ends.size();
            for (int i = 0; i < m; i++) {
                if (i < 4 || i >= m - 4) out.add(ends.get(i));
            }
            int end = trimEnd(qp + 3, n);
            out.add(new Cand(CLOSE_TRIPLE, pPos, -1).edit(end, 0, qqq));
            int k = end;
            for (int made = 0; made < 4 && k > qp + 3 && ")]},;:".indexOf(s[k - 1]) >= 0; made++) {
                k--;
                while (k > qp + 3 && (s[k - 1] == ' ' || s[k - 1] == '\t')) k--;
                out.add(new Cand(CLOSE_TRIPLE, pPos, -1).edit(k, 0, qqq));
            }
        }

        void unclosed(List<Cand> out) {
            int m = 0;
            int[] open = new int[sc.count];
            for (int k = 0; k < sc.count; k++) {
                if (sc.kind[k] == Scanner.UNCLOSED) open[m++] = sc.pos[k];
            }
            open = Arrays.copyOf(open, m);
            for (int k = 0, made = 0; k < sc.suspects && made < 3; k++) {
                if (contains(sc.suspectOpen[k], pPos)) {
                    Cand c = moveClose(sc.suspectLine[k], sc.suspectOpen[k]);
                    if (c != null) {
                        out.add(c);
                        made++;
                    }
                }
            }
            sibling(out, open[m - 1], n);
            int ip = insertionBefore(sc.lines);
            if (ip > open[m - 1]) out.add(new Cand(CLOSE_BRACKETS, open[0], -1).edit(ip, 0, closers(open, 0)));
            int l = sc.lineOf(open[m - 1]);
            int from = m - 1;
            while (from > 0 && sc.lineOf(open[from - 1]) == l) from--;
            int ip2 = insertionBefore(l + 1);
            if (ip2 > open[m - 1] && ip2 != ip) {
                out.add(new Cand(CLOSE_BRACKETS, open[from], -1).edit(ip2, 0, closers(open, from)));
            }
        }

        /** A ';' inside brackets: close them before it, or where a later line starts a statement. */
        void semicolon(List<Cand> out) {
            int[] open = pOpen;
            int m = open.length;
            for (int k = 0, made = 0; k < sc.suspects && made < 2; k++) {
                int l = sc.suspectLine[k];
                if (sc.lineStart[l] < pPos && contains(sc.suspectOpen[k], open[m - 1])) {
                    Cand c = moveClose(l, sc.suspectOpen[k]);
                    if (c != null) {
                        out.add(c);
                        made++;
                    }
                }
            }
            sibling(out, open[m - 1], pPos);
            int ip = trimEnd(open[m - 1] + 1, pPos);
            out.add(new Cand(CLOSE_BRACKETS, open[0], -1).edit(ip, 0, closers(open, 0)));
        }
        void mismatched(List<Cand> out) {
            char c = s[pPos];
            int[] open = pOpen;
            int j = open.length - 2;
            while (j >= 0 && !Scanner.matches(s[open[j]], c)) j--;
            stringCloser(out, c);
            if (j >= 0 && c == '}') keyAfterComma(out, open, j + 1);
            sibling(out, pAt, pPos);
            if (j >= 0) out.add(new Cand(CLOSE_BRACKETS, open[j + 1], -1).edit(pPos, 0, closers(open, j + 1)));
            out.add(new Cand(REPLACE_CLOSER, pPos, pAt).edit(pPos, 1, String.valueOf(Scanner.closerOf(s[pAt]))));
            out.add(new Cand(REMOVE_CLOSER, pPos, -1).edit(pPos, 1, ""));
            int la = sc.lineOf(pAt);
            int lp = sc.lineOf(pPos);
            for (int k = 0, made = 0; k < sc.suspects && made < 2; k++) {
                int l = sc.suspectLine[k];
                if (l > la && l <= lp && contains(sc.suspectOpen[k], pAt)) {
                    Cand m = moveClose(l, sc.suspectOpen[k]);
                    if (m != null) {
                        out.add(m);
                        made++;
                    }
                }
            }
        }

        /**
         * Drops a closer written right after a string whose own text leaves that bracket open, as in
         * {@code ["tui ["], "x"]}: the closer balanced the string's content and ended the list early.
         */
        void stringCloser(List<Cand> out, char c) {
            char o = c == ')' ? '(' : c == ']' ? '[' : '{';
            int depth = 0;
            for (int p = pAt + 1; p < pPos; p++) {
                char d = s[p];
                if (d == '"' || d == '\'') {
                    int e = skipString(p);
                    int q = e;
                    while (q < pPos && (s[q] == ' ' || s[q] == '\t')) q++;
                    if (depth == 1 && q < pPos && s[q] == c && e - 1 > p && s[e - 1] == d) {
                        int balance = 0;
                        for (int k = p + 1; k < e - 1; k++) {
                            if (s[k] == o) balance++;
                            else if (s[k] == c) balance--;
                        }
                        if (balance > 0) {
                            out.add(new Cand(REMOVE_CLOSER, q, -1).edit(q, 1, ""));
                            return;
                        }
                    }
                    p = e - 1;
                } else if (d == '#') {
                    while (p + 1 < pPos && s[p + 1] != '\n') p++;
                } else if (d == '(' || d == '[' || d == '{') {
                    depth++;
                } else if (d == ')' || d == ']' || d == '}') {
                    if (--depth < 0) return;
                }
            }
        }

        /**
         * Closes the brackets opened from {@code open[from]} before a {@code , 'key':} that belongs to the
         * enclosing dict, as in {@code {'q': ['a', 'k': 1}}.
         */
        void keyAfterComma(List<Cand> out, int[] open, int from) {
            int m = open.length;
            int level = 0;
            int nest = 0;
            int comma = -1;
            for (int p = open[from] + 1; p < pPos; p++) {
                char d = s[p];
                if (d == '"' || d == '\'') {
                    int e = skipString(p);
                    if (comma >= 0) {
                        int q = e;
                        while (q < pPos && (s[q] == ' ' || s[q] == '\t')) q++;
                        if (q + 1 < pPos && s[q] == ':' && s[q + 1] != '=' && s[open[from + level]] != '{') {
                            int ip = trimEnd(open[from] + 1, comma);
                            StringBuilder b = new StringBuilder();
                            for (int k = from + level; k >= from; k--) b.append(Scanner.closerOf(s[open[k]]));
                            out.add(new Cand(CLOSE_BRACKETS, open[from], -1).edit(ip, 0, b.toString()));
                            return;
                        }
                    }
                    comma = -1;
                    p = e - 1;
                } else if (d == '#') {
                    while (p + 1 < pPos && s[p + 1] != '\n') p++;
                } else if (d == '(' || d == '[' || d == '{') {
                    comma = -1;
                    if (nest == 0 && from + level + 1 < m && open[from + level + 1] == p) level++;
                    else nest++;
                } else if (d == ')' || d == ']' || d == '}') {
                    comma = -1;
                    if (--nest < 0) return;
                } else if (d == ',') {
                    comma = nest == 0 ? p : -1;
                } else if (d != ' ' && d != '\t' && d != '\n' && d != '\r') {
                    comma = -1;
                }
            }
        }
        /**
         * Closes the call opened at {@code o} before a later {@code , name(} that repeats its callee directly
         * inside it: {@code [str(a, str(b)]} was meant as {@code [str(a), str(b)]}.
         */
        void sibling(List<Cand> out, int o, int limit) {
            if (s[o] != '(') return;
            int b = o;
            while (b > 0 && (Scanner.identPart(s[b - 1]) || s[b - 1] == '.')) b--;
            if (b == o || !Scanner.identStart(s[b])) return;
            int depth = 0;
            for (int p = o + 1; p < limit; p++) {
                char c = s[p];
                if (c == '"' || c == '\'') {
                    p = skipString(p) - 1;
                } else if (c == '#') {
                    while (p + 1 < limit && s[p + 1] != '\n') p++;
                } else if (c == '(' || c == '[' || c == '{') {
                    depth++;
                } else if (c == ')' || c == ']' || c == '}') {
                    if (--depth < 0) return;
                } else if (c == ',' && depth == 0) {
                    int q = p + 1;
                    while (q < limit && (s[q] == ' ' || s[q] == '\t' || s[q] == '\n')) q++;
                    int k = 0;
                    while (b + k < o && q + k < limit && s[q + k] == s[b + k]) k++;
                    if (b + k == o && q + k < limit && s[q + k] == '(') {
                        out.add(new Cand(CLOSE_BRACKETS, o, -1).edit(p, 0, ")"));
                        return;
                    }
                }
            }
        }

        /** End of the string literal whose quote is at {@code p}, or the end of its line when it is not closed. */
        int skipString(int p) {
            char q = s[p];
            boolean triple = p + 2 < n && s[p + 1] == q && s[p + 2] == q;
            for (int e = p + (triple ? 3 : 1); e < n; e++) {
                char c = s[e];
                if (c == '\\') {
                    e++;
                } else if (c == '\n' && !triple) {
                    return e;
                } else if (c == q && (!triple || (e + 2 < n && s[e + 1] == q && s[e + 2] == q))) {
                    return e + (triple ? 3 : 1);
                }
            }
            return n;
        }

        void backslash(List<Cand> out) {
            int l = sc.lineOf(pPos);
            int le = sc.lineEnd(l);
            char x = pPos + 1 < n ? s[pPos + 1] : '\n';
            if (x == '"' || x == '\'') {
                Cand c = new Cand(UNESCAPE_QUOTES, pPos, -1);
                for (int k = pPos; k + 1 < le; k++) {
                    if (s[k] != '\\') continue;
                    if (s[k + 1] == '"' || s[k + 1] == '\'') c.edit(k, 1, "");
                    k++;
                }
                out.add(c);
            }
            if (x == 'n') {
                Cand c = new Cand(NEWLINE_ESCAPES, pPos, -1);
                for (int k = 0; k < sc.count; k++) {
                    int p = sc.pos[k];
                    if (sc.kind[k] == Scanner.STRAY_BACKSLASH && p + 1 < n && s[p + 1] == 'n' && sc.lineOf(p) == l) {
                        c.edit(p, 2, "\n");
                    }
                }
                out.add(c);
            }
            int k = pPos + 1;
            while (k < n && (s[k] == ' ' || s[k] == '\t')) k++;
            if (k > pPos + 1 && (k >= n || s[k] == '\n' || s[k] == '\r')) {
                out.add(new Cand(TRIM_CONTINUATION, pPos, -1).edit(pPos + 1, k - pPos - 1, ""));
            }
            out.add(new Cand(REMOVE_BACKSLASH, pPos, -1).edit(pPos, 1, ""));
        }

        void typographic(List<Cand> out) {
            char c = s[pPos];
            boolean single = c == '\u2018' || c == '\u2019';
            String a = single ? "'" : "\"";
            int le = sc.lineEnd(sc.lineOf(pPos));
            for (int k = pPos + 1; k < le; k++) {
                char d = s[k];
                if (single ? d == '\u2018' || d == '\u2019' : d == '\u201C' || d == '\u201D') {
                    out.add(new Cand(STRAIGHT_QUOTES, pPos, -1).edit(pPos, 1, a).edit(k, 1, a));
                    break;
                }
            }
            out.add(new Cand(STRAIGHT_QUOTES, pPos, -1).edit(pPos, 1, a));
        }

        /** Closes every bracket open at the start of line {@code line} at the end of the code line
         *  before it, then drops the closers further on that no longer have an opener. */
        Cand moveClose(int line, int[] open) {
            int ip = insertionBefore(line);
            if (ip < 0 || ip <= open[open.length - 1]) return null;
            String cl = closers(open, 0);
            Cand c = new Cand(CLOSE_BRACKETS, open[0], -1).edit(ip, 0, cl);
            for (int k = 0; k < open.length && budget > 0; k++) {
                Scanner x = scan(c, sc);
                int u = -1;
                int from = ip + cl.length();
                for (int j = 0; j < x.count; j++) {
                    if (x.pos[j] >= from && (u < 0 || x.pos[j] < x.pos[u])) u = j;
                }
                if (u < 0 || x.kind[u] != Scanner.UNMATCHED) break;
                c.edit(c.back(x.pos[u]), 1, "");
            }
            return c;
        }

        /** Where to put closers for code that should end before line {@code line}: the end of the
         *  last line before it that has code, ahead of any comment; -1 when there is none. */
        int insertionBefore(int line) {
            for (int l = line - 1; l >= 0; l--) {
                boolean endInCode = l + 1 < sc.lines ? sc.lineDepth[l + 1] >= 0 : sc.endsInCode;
                if (!endInCode) return -1;
                int start = sc.lineStart[l];
                int end = sc.lineComment[l] >= 0 ? sc.lineComment[l] : sc.lineEnd(l);
                end = trimEnd(start, end);
                if (l + 1 < sc.lines && sc.lineCont[l + 1] && end > start && s[end - 1] == '\\') {
                    end = trimEnd(start, end - 1);
                }
                if (end > start) return end;
            }
            return -1;
        }

        boolean plausibleEnd(int k) {
            while (k < n && (s[k] == ' ' || s[k] == '\t')) k++;
            if (k >= n) return true;
            char c = s[k];
            if (",)]}:;.+%*=#\n\r<>!".indexOf(c) >= 0) return true;
            if (!Scanner.identStart(c)) return false;
            int j = k + 1;
            while (j < n && Scanner.identPart(s[j])) j++;
            return switch (new String(s, k, j - k)) {
                case "if", "else", "for", "in", "is", "and", "or", "not" -> true;
                default -> false;
            };
        }

        int quoteAt(int p) {
            while (s[p] != '\'' && s[p] != '"') p++;
            return p;
        }

        /** The indentation of the line holding {@code p}. */
        String indentOf(int p) {
            int ls = sc.lineStart[sc.lineOf(p)];
            int e = ls;
            while (e < p && (s[e] == ' ' || s[e] == '\t')) e++;
            return new String(s, ls, e - ls);
        }

        int trimEnd(int from, int to) {
            while (to > from) {
                char c = s[to - 1];
                if (c != ' ' && c != '\t' && c != '\r' && c != '\f' && c != '\n') break;
                to--;
            }
            return to;
        }

        String closers(int[] open, int from) {
            StringBuilder b = new StringBuilder();
            for (int k = open.length - 1; k >= from; k--) b.append(Scanner.closerOf(s[open[k]]));
            return b.toString();
        }

        void accept(Cand c) {
            fixes.add(describe(c));
            int[] o = c.order();
            for (int k = o.length - 1; k >= 0; k--) {
                int e = o[k];
                if (logSize == logAt.length) {
                    logAt = Arrays.copyOf(logAt, logSize * 2);
                    logDel = Arrays.copyOf(logDel, logSize * 2);
                    logIns = Arrays.copyOf(logIns, logSize * 2);
                }
                logAt[logSize] = c.at[e];
                logDel[logSize] = c.del[e];
                logIns[logSize] = c.ins[e].length();
                logSize++;
            }
            use(c.scanner);
        }

        int toOriginal(int p) {
            for (int k = logSize - 1; k >= 0; k--) {
                int a = logAt[k];
                int m = logIns[k];
                if (p >= a + m) p += logDel[k] - m;
                else if (p > a) p = a;
            }
            return p;
        }

        int line(int p) {
            return first.lineOf(toOriginal(p)) + 1;
        }

        int column(int p) {
            int o = toOriginal(p);
            return o - first.lineStart[first.lineOf(o)] + 1;
        }

        /** Where the edits of {@code c} are: their columns when they share a line, else lines and columns; the
         *  first and the last when there are more than four. */
        String places(Cand c) {
            int[] o = c.order();
            int first = c.at[o[0]];
            int last = c.at[o[o.length - 1]];
            boolean one = line(first) == line(last);
            if (o.length > 4) {
                return one ? "from column " + column(first) + " to column " + column(last)
                    : "from line " + line(first) + ", column " + column(first) + " to line " + line(last) + ", column "
                        + column(last);
            }
            StringBuilder b = new StringBuilder(one ? "at columns " : "at ");
            for (int k = 0; k < o.length; k++) {
                int p = c.at[o[k]];
                if (k > 0) b.append(k == o.length - 1 ? " and " : ", ");
                b.append(one ? "" : "line " + line(p) + ", column ").append(column(p));
            }
            return b.toString();
        }

        Fix describe(Cand c) {
            int p = c.kind == ESCAPE_QUOTE || c.kind == ESCAPE_QUOTES
                || c.kind == EXTEND_TRIPLE || c.kind == SWAP_TRIPLE ? c.ref2 : c.at[0];
            int line = line(p);
            int col = column(p);
            String where = "line " + line + ": ";
            String msg = switch (c.kind) {
                case TRIPLE_QUOTE -> where + "made the string at column " + col + " triple-quoted ("
                    + c.ins[0] + ") because its text continues onto the next lines; it now ends on line "
                    + line(c.ref2);
                case CLOSE_QUOTE -> where + "added the missing closing " + c.ins[0] + " at column " + col;
                case ESCAPE_QUOTE -> where + "escaped the " + s[c.ref2] + " at column " + col
                    + " that ended the string early";
                case EXTEND_TRIPLE -> where + "completed the closing " + repeat(s[c.ref2], 3) + " at column "
                    + col + " of the triple-quoted string from line " + line(c.ref);
                case SWAP_TRIPLE -> where + "changed the closing " + new String(s, c.ref2, 3)
                    + " at column " + col + " to " + c.ins[0] + " to match the string from line " + line(c.ref);
                case CLOSE_TRIPLE -> where + "added the missing closing " + c.ins[0] + " at column " + col
                    + " for the triple-quoted string from line " + line(c.ref);
                case CLOSE_BRACKETS -> closeMessage(c, where, col);
                case REPLACE_CLOSER -> where + "replaced '" + s[p] + "' at column " + col + " with '" + c.ins[0]
                    + "' to match '" + s[c.ref2] + "' from line " + line(c.ref2);
                case REMOVE_CLOSER -> where + "removed the unmatched '" + s[p] + "' at column " + col;
                case REMOVE_BACKSLASH -> where + "removed the stray backslash at column " + col;
                case TRIM_CONTINUATION -> where + "removed the spaces after the line-continuation backslash at column "
                    + (col - 1);
                case NEWLINE_ESCAPES -> where + "turned the literal \\n outside strings into line breaks";
                case UNESCAPE_QUOTES -> where + "removed the backslashes before quotes outside strings, from column "
                    + col;
                case STRAIGHT_QUOTES -> where + "replaced the typographic quotes at column " + col
                    + " with straight quotes";
                case DOUBLE_BRACE -> where + "doubled the single '}' at column " + col + " in the f-string";
                case REMOVE_BRACE -> where + "removed the single '}' at column " + col + " in the f-string";
                case LITERAL_BRACES -> where + "doubled the '{' at column " + col
                    + (c.edits == 1 ? "" : c.edits == 2 ? " and its closing '}'"
                        : ", its closing '}' and the braces between them")
                    + " in the f-string, which held text rather than an expression";
                case DOUBLE_BACKSLASH -> where + "doubled the backslash at column " + col
                    + " so the string keeps it as text instead of an invalid escape";
                case ESCAPE_QUOTES -> where + "escaped the " + (c.edits > 4 ? c.edits + " " : "") + s[c.ref2] + " "
                    + places(c) + " so the string keeps them as text";
                case REMOVE_MARKER -> where + "removed the quote marker " + s[c.ref] + " at column " + column(c.ref);
                case SPLIT_STATEMENT -> where + "moved the statement after ';' at column " + col + " onto its own line";
                default -> where + "turned the 'n' at column " + col + " back into the line break it stood for";
            };
            return new Fix(FIX_KINDS[c.kind], line, col, msg);
        }

        String closeMessage(Cand c, String where, int col) {
            String cl = c.ins[0];
            StringBuilder b = new StringBuilder(where).append("added '").append(cl).append("' at column ").append(col)
                .append(" to close ").append(cl.length() == 1 ? "'" + s[c.ref] + "'" : "the brackets")
                .append(" from line ").append(line(c.ref));
            for (int k = 1; k < c.edits; k++) {
                b.append(k == 1 ? ", and removed the extra '" : ", '").append(s[c.at[k]]).append("' on line ")
                    .append(line(c.at[k]));
            }
            return b.toString();
        }
    }

    static boolean near(Scanner sc, int line, int[] open, int errorLine) {
        return errorLine <= 0 || (errorLine >= sc.lineOf(open[0]) + 1 && errorLine <= line + 1);
    }

    static boolean contains(int[] xs, int x) {
        for (int v : xs) {
            if (v == x) return true;
        }
        return false;
    }

    static String repeat(char c, int k) {
        return String.valueOf(c).repeat(k);
    }

    static List<Problem> problems(Scanner sc, int errorLine) {
        List<Problem> out = new ArrayList<>();
        Integer[] order = new Integer[sc.count];
        for (int k = 0; k < sc.count; k++) order[k] = k;
        Arrays.sort(order, (a, b) -> Integer.compare(sc.pos[a], sc.pos[b]));
        for (int k = 0; k < sc.count && out.size() < MAX_PROBLEMS; k++) out.add(problem(sc, order[k]));
        if (sc.count > 0) return out;
        for (int k = 0; k < sc.suspects && out.size() < 3; k++) {
            int l = sc.suspectLine[k];
            int[] o = sc.suspectOpen[k];
            if (!near(sc, l, o, errorLine)) continue;
            int ol = sc.lineOf(o[0]);
            out.add(new Problem("open-bracket-at-statement", l + 1, 1, "line " + (l + 1)
                + " starts a new statement while '" + sc.s[o[0]] + "' from line " + (ol + 1) + ", column "
                + (o[0] - sc.lineStart[ol] + 1) + " is still open"));
        }
        return out;
    }

    static Problem problem(Scanner sc, int k) {
        int p = sc.pos[k];
        int l = sc.lineOf(p);
        int col = p - sc.lineStart[l] + 1;
        char[] s = sc.s;
        String where = "line " + (l + 1) + ", column " + col + ": ";
        String msg = switch (sc.kind[k]) {
            case Scanner.UNTERMINATED_STRING -> {
                int q = p;
                boolean f = false;
                while (s[q] != '\'' && s[q] != '"') {
                    char c = Character.toLowerCase(s[q]);
                    f |= c == 'f' || c == 't';
                    q++;
                }
                yield where + "the " + (f ? "f-string" : "string") + " is not closed on its line";
            }
            case Scanner.UNTERMINATED_TRIPLE -> where + "the triple-quoted string is never closed";
            case Scanner.UNCLOSED -> where + "'" + s[p] + "' is never closed";
            case Scanner.UNMATCHED -> where + "'" + s[p] + "' has no opening bracket";
            case Scanner.MISMATCHED -> {
                int o = sc.at[k];
                int ol = sc.lineOf(o);
                yield where + "'" + s[p] + "' does not match '" + s[o] + "' from line " + (ol + 1) + ", column "
                    + (o - sc.lineStart[ol] + 1);
            }
            case Scanner.STRAY_BACKSLASH -> where + "backslash outside a string; there it may only end a line";
            case Scanner.TYPOGRAPHIC_QUOTE -> where + "typographic quote " + s[p]
                + "; Python needs straight quotes (' or \")";
            case Scanner.SEMICOLON -> {
                int o = sc.at[k];
                int ol = sc.lineOf(o);
                yield where + "';' ends the statement while '" + s[o] + "' from line " + (ol + 1) + ", column "
                    + (o - sc.lineStart[ol] + 1) + " is still open";
            }
            case Scanner.FSTRING_BRACE -> where + "single '}' in an f-string; write '}}' for a literal brace";
            case Scanner.FSTRING_FIELD -> where + "'{' opens an f-string field that holds no Python expression;"
                + " write '{{' and '}}' for literal braces";
            case Scanner.INVALID_ESCAPE -> where + "'\\" + s[p + 1] + "' is not a valid escape; write '\\\\" + s[p + 1]
                + "' to keep the backslash, or use a raw string";
            case Scanner.TEXT_AFTER_STRING -> {
                int o = sc.at[k];
                int ol = sc.lineOf(o);
                yield where + "the string from " + (ol == l ? "" : "line " + (ol + 1) + ", ") + "column "
                    + (o - sc.lineStart[ol] + 1) + " ends right before this text";
            }
            case Scanner.MARKER -> where + "'" + s[p] + "' is a quote marker, not Python; remove it";
            case Scanner.COMPOUND_AFTER_SEMICOLON -> where
                + "a compound statement cannot follow ';'; start it on its own line";
            default -> where + "'n' right after '" + s[p - 1] + "' looks like a \\n that lost its backslash";
        };
        return new Problem(PROBLEM_KINDS[sc.kind[k]], l + 1, col, msg);
    }
}
