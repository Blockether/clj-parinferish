package com.blockether.parinferish.python;

import java.util.Arrays;

/**
 * One pass over Python source that finds what the tokenizer rejects: strings
 * that never close, brackets that never close or close the wrong opener, stray
 * backslashes, typographic quotes and single braces in f-strings. It keeps
 * reading after each problem, so one pass reports all of them.
 *
 * <p>It follows the Python 3.12+ tokenizer (PEP 701): an f-string replacement
 * field is code, may nest any quotes and may span lines. It also notes, per
 * line, whether the line starts inside open brackets and whether it starts a
 * statement there, which is how the repair finds a bracket that should have
 * closed on an earlier line.
 *
 * <p>After a small edit it can rescan: it resumes where it last stood in code
 * before the edit and, at the first line start or string end after the edit
 * where it is back in step with the scan of the text before the edit, takes the
 * rest from that scan, so a candidate repair costs about the lines it changes,
 * not the whole text.
 */
final class Scanner {
    static final int UNTERMINATED_STRING = 0;
    static final int UNTERMINATED_TRIPLE = 1;
    static final int UNCLOSED = 2;
    static final int UNMATCHED = 3;
    static final int MISMATCHED = 4;
    static final int STRAY_BACKSLASH = 5;
    static final int TYPOGRAPHIC_QUOTE = 6;
    static final int FSTRING_BRACE = 7;
    static final int SEMICOLON = 8;
    static final int MARKER = 9;
    static final int COMPOUND_AFTER_SEMICOLON = 10;
    static final int LOST_NEWLINE = 11;
    static final int FSTRING_FIELD = 12;
    static final int INVALID_ESCAPE = 13;
    static final int TEXT_AFTER_STRING = 14;

    private static final String[] COMPOUND = {"def", "class", "with", "for", "while", "if", "try", "async"};

    /** How many of the innermost open brackets a problem records, and how far a closer looks down
     *  the stack for its opener. Real code nests far less; only degenerate input nests deeper, and
     *  copying or searching whole stacks for it would make the scan quadratic. */
    private static final int WINDOW = 32;

    /** How many open brackets a line may start under and still be a line a rescan resumes at or
     *  rejoins; lines deeper than that are scanned again. */
    private static final int LOGGED = 32;

    private static final int F_STRING = 0;
    private static final int F_FIELD = 1;
    private static final int F_SPEC = 2;

    /** What a string prefix makes of its string: an f- or t-string, raw, bytes. */
    private static final int FORMAT = 1;
    private static final int RAW = 2;
    private static final int BYTES = 4;

    final char[] s;
    final int n;

    /** Physical lines: start offset, bracket depth at the start (-1 when it starts inside a string),
     *  whether it continues a backslash-ended line, and where its comment starts (-1 for none). */
    final int lines;
    final int[] lineStart;
    final int[] lineDepth;
    final boolean[] lineCont;
    final int[] lineComment;

    /** Checkpoints, in text order and CP ints each: where the scan stood at the start of each line
     *  that starts in code and right after each string that ran over lines, places the scan so far
     *  never looked past. Each holds the position, the line, the kind, the depth, the statement
     *  indent, how many problems and suspects came before, and where {@code stackLog} keeps the open
     *  brackets (-1 when there were more than {@link #LOGGED}). A rescan resumes at one before the
     *  edit and rejoins at one after it. */
    private static final int CP = 8;
    private static final int AT = 0;
    private static final int LINE = 1;
    private static final int KIND = 2;
    private static final int DEPTH = 3;
    private static final int INDENT = 4;
    private static final int PROBLEMS = 5;
    private static final int SUSPECTS = 6;
    private static final int STACK = 7;
    private static final int LINE_START = 0;
    private static final int CONTINUATION = 1;
    private static final int STRING_END = 2;
    private int[] cp;
    private int cps;
    private int[] stackLog = new int[16];
    private int logged;

    /** The first character that is not whitespace, the only place a quote marker counts. */
    private int lead;

    /** Problems in the order found; the UNCLOSED ones come last, found at the end of the text.
     *  {@code at} is the newline that ended an unterminated string, or the opener a mismatched
     *  closer met; {@code open} holds the open brackets when a closer mismatched. */
    int count;
    int[] kind = new int[8];
    int[] pos = new int[8];
    int[] at = new int[8];
    int[][] open = new int[8][];

    /** Lines that start a statement while brackets opened on earlier lines are still open. */
    int suspects;
    int[] suspectLine = new int[4];
    int[][] suspectOpen = new int[4][];

    /** False when the text ends inside a string. */
    boolean endsInCode = true;

    private int depth;
    private int[] stPos = new int[16];
    private char[] stCh = new char[16];

    private int frames;
    private int[] fType = new int[8];
    private int[] fStart = new int[8];
    private int[] fQuote = new int[8];
    private int[] fBase = new int[8];
    private boolean[] fTriple = new boolean[8];
    private boolean[] fRaw = new boolean[8];
    private boolean[] fBad = new boolean[8];

    private int cursor;
    private int stmtIndent;

    /** While rescanning: the scan of the text before the edit, the edit as {@code [from, to)} of that
     *  text, how far it moved what follows, how many lines it added, and the next checkpoint of
     *  {@code base} to rejoin at. {@code done} once the rest came from {@code base}. */
    private Scanner base;
    private int from;
    private int to;
    private int shift;
    private int lineShift;
    private int next;
    private boolean done;

    /** Set by a triple-quoted string that closed on a later line than it opened. */
    private boolean crossed;

    Scanner(String text) {
        this(text.toCharArray());
    }

    Scanner(char[] s) {
        this(s, starts(s));
    }

    private Scanner(char[] s, int[] lineStart) {
        this.s = s;
        this.n = s.length;
        this.lines = lineStart.length;
        this.lineStart = lineStart;
        lineDepth = new int[lines];
        Arrays.fill(lineDepth, -1);
        lineCont = new boolean[lines];
        lineComment = new int[lines];
        Arrays.fill(lineComment, -1);
    }

    private static int[] starts(char[] s) {
        int c = 1;
        for (char ch : s) {
            if (ch == '\n') c++;
        }
        int[] starts = new int[c];
        for (int i = 0, l = 1; l < c; i++) {
            if (s[i] == '\n') starts[l++] = i + 1;
        }
        return starts;
    }

    Scanner scan() {
        cp = new int[CP * (lines + 8)];
        line(0, false);
        int i = 0;
        while (i < n && Character.isWhitespace(s[i])) i++;
        lead = i;
        if (i < n && s[i] == '>') add(MARKER, i, -1, null);
        return run(0);
    }

    /**
     * Scans {@code t}: the text of {@code base} with its {@code [from, to)} replaced by
     * {@code t[from, to + t.length - base.n)}. Answers exactly what {@code new Scanner(t).scan()}
     * answers, but resumes at the last checkpoint of {@code base} before the edit and, at the first
     * checkpoint after it where the scan stands where the scan of {@code base} stood, takes the rest
     * from {@code base}.
     */
    static Scanner rescan(Scanner base, char[] t, int from, int to) {
        int shift = t.length - base.n;
        int end = to + shift;
        int keep = base.lineOf(from) + 1;
        int tail = base.lineOf(to) + 1;
        int added = 0;
        for (int i = from; i < end; i++) {
            if (t[i] == '\n') added++;
        }
        int[] starts = new int[keep + added + base.lines - tail];
        System.arraycopy(base.lineStart, 0, starts, 0, keep);
        int l = keep;
        for (int i = from; i < end; i++) {
            if (t[i] == '\n') starts[l++] = i + 1;
        }
        for (int k = tail; k < base.lines; k++) starts[l++] = base.lineStart[k] + shift;
        Scanner x = new Scanner(t, starts);
        x.base = base;
        x.from = from;
        x.to = to;
        x.shift = shift;
        x.lineShift = keep + added - tail;
        x.next = base.checkpointAfter(to);
        int c = base.checkpointAfter(from) - 1;
        while (c > 0 && (base.cp[c * CP + STACK] < 0 || base.readTo(c) >= from)) c--;
        return c > 0 && from > base.lead ? x.resume(c) : x.scan();
    }

    /** The first checkpoint after position {@code p}. */
    private int checkpointAfter(int p) {
        int lo = 0;
        int hi = cps;
        while (lo < hi) {
            int mid = (lo + hi) >>> 1;
            if (cp[mid * CP + AT] <= p) lo = mid + 1;
            else hi = mid;
        }
        return lo;
    }

    /** The last position the scan read before it took checkpoint {@code c}: the one before a line
     *  start, and after a string whatever {@link #touches} read past its closing quote. */
    private int readTo(int c) {
        int p = cp[c * CP + AT];
        if (cp[c * CP + KIND] != STRING_END) return p - 1;
        if (p >= n || !identStart(s[p])) return p;
        int k = p + 1;
        while (k < n && identPart(s[k])) k++;
        return k;
    }

    /** Continues from checkpoint {@code c} of {@code base}, which lies before the edit. */
    private Scanner resume(int c) {
        Scanner b = base;
        int[] q = b.cp;
        int o = c * CP;
        int p = q[o + AT];
        int l = q[o + LINE];
        int k = q[o + KIND];
        lead = b.lead;
        System.arraycopy(b.lineDepth, 0, lineDepth, 0, l);
        System.arraycopy(b.lineCont, 0, lineCont, 0, l);
        System.arraycopy(b.lineComment, 0, lineComment, 0, l);
        cps = k == STRING_END ? c + 1 : c;
        cp = new int[Math.max(q.length, CP * (cps + 16))];
        System.arraycopy(q, 0, cp, 0, cps * CP);
        depth = q[o + DEPTH];
        int so = q[o + STACK];
        logged = k == STRING_END ? so + depth : so;
        stackLog = new int[logged + depth + 16];
        System.arraycopy(b.stackLog, 0, stackLog, 0, logged);
        count = q[o + PROBLEMS];
        int m = Math.max(8, count * 2);
        kind = Arrays.copyOf(b.kind, m);
        pos = Arrays.copyOf(b.pos, m);
        at = Arrays.copyOf(b.at, m);
        open = Arrays.copyOf(b.open, m);
        suspects = q[o + SUSPECTS];
        suspectLine = Arrays.copyOf(b.suspectLine, Math.max(4, suspects * 2));
        suspectOpen = Arrays.copyOf(b.suspectOpen, Math.max(4, suspects * 2));
        if (depth > stPos.length) {
            stPos = new int[depth * 2];
            stCh = new char[depth * 2];
        }
        for (int d = 0; d < depth; d++) {
            stPos[d] = b.stackLog[so + d];
            stCh[d] = s[stPos[d]];
        }
        stmtIndent = q[o + INDENT];
        cursor = l;
        if (k != STRING_END) line(p, k == CONTINUATION);
        return run(p);
    }

    private Scanner run(int i) {
        while (i < n) {
            if (frames == 0) {
                i = code(i, 0);
            } else {
                int t = fType[frames - 1];
                i = t == F_STRING ? literal(i) : t == F_FIELD ? code(i, fBase[frames - 1]) : spec(i);
            }
        }
        base = null;
        if (done) return this;
        if (frames > 0) {
            add(fTriple[0] ? UNTERMINATED_TRIPLE : UNTERMINATED_STRING, fStart[0], n, null);
            depth = fBase[0];
            frames = 0;
            endsInCode = false;
        }
        for (int d = 0; d < depth; d++) add(UNCLOSED, stPos[d], -1, null);
        return this;
    }

    /** The zero-based line holding {@code p}. */
    int lineOf(int p) {
        int lo = 0;
        int hi = lines - 1;
        while (lo < hi) {
            int mid = (lo + hi + 1) >>> 1;
            if (lineStart[mid] <= p) lo = mid;
            else hi = mid - 1;
        }
        return lo;
    }

    /** Where line {@code l} ends: its newline, or the end of the text. */
    int lineEnd(int l) {
        return l + 1 < lines ? lineStart[l + 1] - 1 : n;
    }

    int hardCount() {
        return count;
    }

    private int code(int i, int base) {
        char c = s[i];
        return switch (c) {
            case ' ', '\t', '\f', '\r' -> i + 1;
            case '\n' -> {
                if (frames == 0) {
                    line(i + 1, false);
                    if (done) yield n;
                }
                yield i + 1;
            }
            case '#' -> {
                if (frames == 0) lineComment[lineAt(i)] = i;
                int j = i;
                while (j < n && s[j] != '\n') j++;
                yield j;
            }
            case '\\' -> {
                int j = i + 1;
                if (j < n && s[j] == '\r') j++;
                if (j < n && s[j] == '\n') {
                    if (frames == 0) {
                        line(j + 1, true);
                        if (done) yield n;
                    }
                    yield j + 1;
                }
                add(STRAY_BACKSLASH, i, -1, null);
                yield i + 1;
            }
            case '\'', '"' -> ended(touching(i, string(i, i, 0)));
            case '(', '[', '{' -> {
                push(i, c);
                yield i + 1;
            }
            case ')', ']', '}' -> close(i, c, base);
            case ':' -> {
                if (frames > 0 && depth == base) frame(F_SPEC, i, depth);
                yield i + 1;
            }
            case ';' -> {
                if (frames > 0) {
                    badField();
                } else if (depth > 0) {
                    add(SEMICOLON, i, stPos[depth - 1], openWindow());
                    depth = 0;
                } else if (compound(i + 1)) {
                    add(COMPOUND_AFTER_SEMICOLON, i, -1, null);
                }
                yield i + 1;
            }
            case '$', '?', '`' -> {
                if (frames > 0 && (c != '$' || !identPart(s[i - 1]))) badField();
                yield i + 1;
            }
            case '\u2018', '\u2019', '\u201C', '\u201D' -> {
                add(TYPOGRAPHIC_QUOTE, i, -1, null);
                yield i + 1;
            }
            case '\u00AB', '\u00BB' -> {
                add(MARKER, i, -1, null);
                yield i + 1;
            }
            default -> {
                if (identStart(c)) {
                    int j = i + 1;
                    while (j < n && identPart(s[j])) j++;
                    if (c == 'n' && frames == 0 && depth == 0 && i > 0 && ")]}'\"".indexOf(s[i - 1]) >= 0
                        && !(j - i == 3 && s[i + 1] == 'o' && s[i + 2] == 't')) {
                        add(LOST_NEWLINE, i, -1, null);
                    }
                    if (j < n && j - i <= 2 && (s[j] == '\'' || s[j] == '"')) {
                        int p = prefix(i, j);
                        if (p >= 0) yield ended((p & FORMAT) != 0 ? string(i, j, p) : touching(j, string(i, j, p)));
                    }
                    yield j;
                }
                if (c >= '0' && c <= '9') {
                    int j = i + 1;
                    while (j < n && (identPart(s[j]) || s[j] == '.')) j++;
                    yield j;
                }
                yield i + 1;
            }
        };
    }

    /** Whether a compound statement keyword follows {@code p} on its line, after spaces. */
    private boolean compound(int p) {
        while (p < n && (s[p] == ' ' || s[p] == '\t')) p++;
        for (String k : COMPOUND) {
            int e = p + k.length();
            if (e < n && startsWith(k, p) && !identPart(s[e])) return true;
        }
        return false;
    }

    private boolean startsWith(String k, int p) {
        for (int j = 0; j < k.length(); j++) {
            if (s[p + j] != k.charAt(j)) return false;
        }
        return true;
    }

    /** -1 when {@code [i, j)} is no string prefix, else its {@link #FORMAT}, {@link #RAW} and {@link #BYTES} flags. */
    private int prefix(int i, int j) {
        boolean r = false;
        boolean f = false;
        boolean b = false;
        boolean u = false;
        for (int k = i; k < j; k++) {
            switch (Character.toLowerCase(s[k])) {
                case 'r' -> {
                    if (r || u) return -1;
                    r = true;
                }
                case 'f', 't' -> {
                    if (f || b || u) return -1;
                    f = true;
                }
                case 'b' -> {
                    if (b || f || u) return -1;
                    b = true;
                }
                case 'u' -> {
                    if (j - i != 1) return -1;
                    u = true;
                }
                default -> {
                    return -1;
                }
            }
        }
        return (f ? FORMAT : 0) | (r ? RAW : 0) | (b ? BYTES : 0);
    }

    private int string(int start, int qp, int flags) {
        char q = s[qp];
        boolean triple = qp + 2 < n && s[qp + 1] == q && s[qp + 2] == q;
        int j = qp + (triple ? 3 : 1);
        if ((flags & FORMAT) != 0) {
            frame(F_STRING, start, depth);
            fQuote[frames - 1] = qp;
            fTriple[frames - 1] = triple;
            fRaw[frames - 1] = (flags & RAW) != 0;
            return j;
        }
        boolean check = (flags & RAW) == 0;
        boolean bytes = (flags & BYTES) != 0;
        boolean spans = false;
        while (j < n) {
            char c = s[j];
            if (c == '\\') {
                if (check && j + 1 < n && escapeEnd(j, bytes) < 0) add(INVALID_ESCAPE, j, -1, null);
                j += j + 2 < n && s[j + 1] == '\r' && s[j + 2] == '\n' ? 3 : 2;
                continue;
            }
            if (c == q) {
                if (!triple) return j + 1;
                if (j + 2 < n && s[j + 1] == q && s[j + 2] == q) {
                    crossed = spans;
                    return j + 3;
                }
            } else if (c == '\n') {
                if (!triple) {
                    add(UNTERMINATED_STRING, start, j, null);
                    return j;
                }
                spans = true;
            }
            j++;
        }
        add(triple ? UNTERMINATED_TRIPLE : UNTERMINATED_STRING, start, n, null);
        endsInCode = false;
        return n;
    }

    private int literal(int i) {
        int f = frames - 1;
        char c = s[i];
        char q = s[fQuote[f]];
        if (c == '\\') return escape(i, fRaw[f]);
        if (c == q) {
            if (!fTriple[f]) return end(f, i + 1);
            if (i + 2 < n && s[i + 1] == q && s[i + 2] == q) return end(f, i + 3);
            return i + 1;
        }
        if (c == '\n' && !fTriple[f]) {
            abandon(f, i);
            return i;
        }
        if (c == '{') {
            if (i + 1 < n && s[i + 1] == '{') return i + 2;
            frame(F_FIELD, i, depth);
            if (!expressionStart(i + 1)) badField();
            return i + 1;
        }
        if (c == '}') {
            if (i + 1 < n && s[i + 1] == '}') return i + 2;
            add(FSTRING_BRACE, i, -1, null);
        }
        return i + 1;
    }

    private int spec(int i) {
        int g = frames - 1;
        while (fType[g] != F_STRING) g--;
        char c = s[i];
        char q = s[fQuote[g]];
        if (c == '{') {
            frame(F_FIELD, i, depth);
            return i + 1;
        }
        if (c == '}') {
            frames -= 2;
            return i + 1;
        }
        if (c == '\\') return escape(i, fRaw[g]);
        if (c == q) {
            if (!fTriple[g]) return end(g, i + 1);
            if (i + 2 < n && s[i + 1] == q && s[i + 2] == q) return end(g, i + 3);
            return i + 1;
        }
        if (c == '\n' && !fTriple[g]) {
            abandon(g, i);
            return i;
        }
        return i + 1;
    }

    /** A backslash in an f-string's text escapes the next character, but never a brace; a valid
     *  {@code \N{name}} takes its braces along. */
    private int escape(int i, boolean raw) {
        int j = i + 1;
        if (j < n && (s[j] == '{' || s[j] == '}')) return j;
        if (j + 1 < n && s[j] == '\r' && s[j + 1] == '\n') return j + 2;
        if (!raw && j < n) {
            int e = escapeEnd(i, false);
            if (e < 0) add(INVALID_ESCAPE, i, -1, null);
            else if (s[j] == 'N') return e;
        }
        return Math.min(n, j + 1);
    }

    /** Where the escape at backslash {@code i} of a string that is not raw ends, or -1 when Python
     *  rejects it: an x, u or U escape with too few hex digits, a code point past U+10FFFF, or an N
     *  escape without a name in braces. Bytes know only the x escape. */
    private int escapeEnd(int i, boolean bytes) {
        char c = s[i + 1];
        int digits = c == 'x' ? 2 : bytes ? 0 : c == 'u' ? 4 : c == 'U' ? 8 : 0;
        if (digits > 0) {
            int k = i + 2;
            long v = 0;
            while (k < n && k < i + 2 + digits && hex(s[k]) >= 0) v = v * 16 + hex(s[k++]);
            return k == i + 2 + digits && v <= 0x10FFFF ? k : -1;
        }
        if (c != 'N' || bytes) return i + 2;
        int k = i + 3;
        if (k > n || s[i + 2] != '{') return -1;
        while (k < n && k < i + 131 && nameChar(s[k])) k++;
        return k < n && s[k] == '}' && k > i + 3 ? k + 1 : -1;
    }

    private static int hex(char c) {
        if (c >= '0' && c <= '9') return c - '0';
        if (c >= 'a' && c <= 'f') return c - 'a' + 10;
        return c >= 'A' && c <= 'F' ? c - 'A' + 10 : -1;
    }

    private static boolean nameChar(char c) {
        return (c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z') || (c >= '0' && c <= '9') || c == ' ' || c == '-';
    }

    /** Whether the text at {@code p}, after spaces, can start the expression of a replacement field. */
    private boolean expressionStart(int p) {
        while (p < n && (s[p] == ' ' || s[p] == '\t')) p++;
        if (p >= n) return true;
        if (s[p] == '.') {
            return p + 1 < n && ((s[p + 1] >= '0' && s[p + 1] <= '9')
                || (s[p + 1] == '.' && p + 2 < n && s[p + 2] == '.'));
        }
        return "}:!=)],;$?`/%&|^><@".indexOf(s[p]) < 0;
    }

    /** Reports the innermost replacement field, once, as text no expression can be: literal braces
     *  that lost their doubling. Fields inside a format spec stay as they are. */
    private void badField() {
        int f = frames - 1;
        if (f < 1 || fType[f] != F_FIELD || fType[f - 1] != F_STRING || fBad[f]) return;
        fBad[f] = true;
        add(FSTRING_FIELD, fStart[f], fQuote[f - 1], null);
    }

    private int end(int f, int next) {
        depth = fBase[f];
        frames = f;
        return touching(fQuote[f], next);
    }

    private void abandon(int f, int newline) {
        add(UNTERMINATED_STRING, fStart[f], newline, null);
        depth = fBase[f];
        frames = f;
    }

    private int close(int i, char c, int base) {
        if (depth == base) {
            if (frames > 0 && c == '}') {
                frames--;
                return i + 1;
            }
            add(UNMATCHED, i, -1, null);
            return i + 1;
        }
        if (matches(stCh[depth - 1], c)) {
            depth--;
            return i + 1;
        }
        add(MISMATCHED, i, stPos[depth - 1], openWindow());
        int floor = Math.max(base, depth - 1 - WINDOW);
        int j = depth - 2;
        while (j >= floor && !matches(stCh[j], c)) j--;
        if (j >= floor) {
            depth = j;
        } else if (frames > 0 && c == '}') {
            depth = base;
            frames--;
        }
        return i + 1;
    }

    static boolean matches(char open, char close) {
        return open == '(' ? close == ')' : open == '[' ? close == ']' : open == '{' && close == '}';
    }

    static char closerOf(char open) {
        return open == '(' ? ')' : open == '[' ? ']' : '}';
    }

    /** The positions of the innermost {@link #WINDOW} open brackets, outermost first. */
    private int[] openWindow() {
        return Arrays.copyOfRange(stPos, Math.max(0, depth - WINDOW), depth);
    }
    private void push(int i, char c) {
        if (depth == stPos.length) {
            stPos = Arrays.copyOf(stPos, depth * 2);
            stCh = Arrays.copyOf(stCh, depth * 2);
        }
        stPos[depth] = i;
        stCh[depth] = c;
        depth++;
    }

    private void frame(int type, int start, int base) {
        if (frames == fType.length) {
            int m = frames * 2;
            fType = Arrays.copyOf(fType, m);
            fStart = Arrays.copyOf(fStart, m);
            fQuote = Arrays.copyOf(fQuote, m);
            fBase = Arrays.copyOf(fBase, m);
            fTriple = Arrays.copyOf(fTriple, m);
            fRaw = Arrays.copyOf(fRaw, m);
            fBad = Arrays.copyOf(fBad, m);
        }
        fType[frames] = type;
        fStart[frames] = start;
        fBase[frames] = base;
        fBad[frames] = false;
        frames++;
    }

    private void add(int k, int p, int a, int[] o) {
        if (count == kind.length) {
            int m = count * 2;
            kind = Arrays.copyOf(kind, m);
            pos = Arrays.copyOf(pos, m);
            at = Arrays.copyOf(at, m);
            open = Arrays.copyOf(open, m);
        }
        kind[count] = k;
        pos[count] = p;
        at[count] = a;
        open[count] = o;
        count++;
    }

    private int lineAt(int p) {
        while (cursor + 1 < lines && lineStart[cursor + 1] <= p) cursor++;
        return cursor;
    }

    /** Called at every line start that is code: records the line and checks whether it starts a
     *  statement while brackets are open. */
    private void line(int p, boolean cont) {
        int l = lineAt(p);
        int k = cont ? CONTINUATION : LINE_START;
        if (rejoined(p, k)) return;
        lineDepth[l] = depth;
        lineCont[l] = cont;
        checkpoint(p, l, k);
        if (cont) return;
        int f = p;
        while (f < n && (s[f] == ' ' || s[f] == '\t' || s[f] == '\f')) f++;
        if (f >= n || s[f] == '\n' || s[f] == '\r' || s[f] == '#') return;
        int col = width(p, f);
        if (depth == 0) {
            stmtIndent = col;
        } else if (col <= stmtIndent && startsStatement(f)) {
            suspect(l, openWindow());
        }
    }

    /** A string's closing quote followed right away by a name or a number: most likely a quote inside the
     *  text ended the string early. */
    private int touching(int qp, int j) {
        if (touches(j)) add(TEXT_AFTER_STRING, j, qp, null);
        return j;
    }

    /** Right after a string that ran over lines, in code: a checkpoint, since its line started inside
     *  the string and nothing before it looked further. */
    private int ended(int j) {
        if (!crossed) return j;
        crossed = false;
        if (frames > 0) return j;
        int l = lineAt(j);
        if (rejoined(j, STRING_END)) return n;
        checkpoint(j, l, STRING_END);
        return j;
    }

    private void suspect(int l, int[] o) {
        if (suspects == suspectLine.length) {
            suspectLine = Arrays.copyOf(suspectLine, suspects * 2);
            suspectOpen = Arrays.copyOf(suspectOpen, suspects * 2);
        }
        suspectLine[suspects] = l;
        suspectOpen[suspects] = o;
        suspects++;
    }

    private void checkpoint(int p, int l, int k) {
        int o = cps * CP;
        if (o == cp.length) cp = Arrays.copyOf(cp, o * 2);
        cp[o + AT] = p;
        cp[o + LINE] = l;
        cp[o + KIND] = k;
        cp[o + DEPTH] = depth;
        cp[o + INDENT] = stmtIndent;
        cp[o + PROBLEMS] = count;
        cp[o + SUSPECTS] = suspects;
        cp[o + STACK] = log();
        cps++;
    }

    /** Records the open brackets; where they went, or -1 when there are too many. */
    private int log() {
        if (depth > LOGGED) return -1;
        int o = logged;
        if (depth > 0) {
            if (o + depth > stackLog.length) stackLog = Arrays.copyOf(stackLog, Math.max(o + depth, o * 2));
            System.arraycopy(stPos, 0, stackLog, o, depth);
            logged = o + depth;
        }
        return o;
    }

    /** Whether the scan, at a checkpoint after the edit, stands where the scan of {@code base} stood
     *  at the same place; if so, it ends with what that scan found from there on. */
    private boolean rejoined(int p, int k) {
        if (base == null || p <= to + shift) return false;
        Scanner b = base;
        int[] q = b.cp;
        int want = p - shift;
        int j = next;
        while (j < b.cps && q[j * CP + AT] < want) j++;
        next = j;
        if (j == b.cps) return false;
        int o = j * CP;
        if (q[o + AT] != want || q[o + KIND] != k || q[o + DEPTH] != depth || q[o + INDENT] != stmtIndent) {
            return false;
        }
        int so = q[o + STACK];
        if (so < 0) return false;
        for (int d = 0; d < depth; d++) {
            if (moved(b.stackLog[so + d]) != stPos[d]) return false;
        }
        stitch(j);
        return true;
    }

    /** Ends the scan with what {@code base} found from its checkpoint {@code j} on. */
    private void stitch(int j) {
        Scanner b = base;
        int[] q = b.cp;
        int o = j * CP;
        int kb = q[o + LINE];
        int l = kb + lineShift;
        int m = b.lines - kb;
        System.arraycopy(b.lineDepth, kb, lineDepth, l, m);
        System.arraycopy(b.lineCont, kb, lineCont, l, m);
        for (int i = 0; i < m; i++) {
            int c = b.lineComment[kb + i];
            lineComment[l + i] = c < 0 ? c : c + shift;
        }
        int dp = count - q[o + PROBLEMS];
        int ds = suspects - q[o + SUSPECTS];
        int so = q[o + STACK];
        int dl = logged - so;
        int size = (cps + b.cps - j) * CP;
        if (size > cp.length) cp = Arrays.copyOf(cp, size);
        for (int i = j; i < b.cps; i++) {
            int f = i * CP;
            int g = cps++ * CP;
            cp[g + AT] = q[f + AT] + shift;
            cp[g + LINE] = q[f + LINE] + lineShift;
            cp[g + KIND] = q[f + KIND];
            cp[g + DEPTH] = q[f + DEPTH];
            cp[g + INDENT] = q[f + INDENT];
            cp[g + PROBLEMS] = q[f + PROBLEMS] + dp;
            cp[g + SUSPECTS] = q[f + SUSPECTS] + ds;
            int st = q[f + STACK];
            cp[g + STACK] = st < 0 ? st : st + dl;
        }
        int len = b.logged - so;
        if (logged + len > stackLog.length) stackLog = Arrays.copyOf(stackLog, logged + len);
        for (int i = 0; i < len; i++) stackLog[logged + i] = moved(b.stackLog[so + i]);
        logged += len;
        for (int i = q[o + PROBLEMS]; i < b.count; i++) {
            add(b.kind[i], moved(b.pos[i]), moved(b.at[i]), moved(b.open[i]));
        }
        for (int i = q[o + SUSPECTS]; i < b.suspects; i++) {
            suspect(b.suspectLine[i] + lineShift, moved(b.suspectOpen[i]));
        }
        endsInCode = b.endsInCode;
        done = true;
    }

    /** Where position {@code p} of the text of {@code base} is now: -1 when the edit replaced it;
     *  negative values mean no position and stay. */
    private int moved(int p) {
        return p < from ? p : p >= to ? p + shift : -1;
    }

    private int[] moved(int[] o) {
        if (o == null || shift == 0) return o;
        int[] r = new int[o.length];
        for (int j = 0; j < o.length; j++) r[j] = moved(o[j]);
        return r;
    }

    private int width(int from, int to) {
        int w = 0;
        for (int k = from; k < to; k++) w = s[k] == '\t' ? (w / 8 + 1) * 8 : w + 1;
        return w;
    }

    /** Whether the code at {@code f} reads as the start of a statement rather than as an argument
     *  or element: a statement keyword, a decorator, an assignment, or a call or attribute access. */
    private boolean startsStatement(int f) {
        char c = s[f];
        if (c == '@') return true;
        if (!identStart(c)) return false;
        int j = f + 1;
        while (j < n && identPart(s[j])) j++;
        if (j < n && (s[j] == '\'' || s[j] == '"')) return false;
        switch (new String(s, f, j - f)) {
            case "def", "class", "return", "import", "from", "with", "try", "except", "finally", "elif",
                 "while", "raise", "pass", "break", "continue", "del", "global", "nonlocal", "assert",
                 "async", "await" -> {
                return true;
            }
            case "if", "for", "else" -> {
                return endsWithColon(j);
            }
            case "not", "and", "or", "in", "is", "lambda", "yield", "None", "True", "False" -> {
                return false;
            }
            default -> {
            }
        }
        int k = j;
        while (k < n && (s[k] == ' ' || s[k] == '\t')) k++;
        if (k >= n) return false;
        char d = s[k];
        if (d == '(' || d == '.' || d == '[') return true;
        if (d == '=') return k + 1 >= n || s[k + 1] != '=';
        return k + 1 < n && s[k + 1] == '=' && "+-*/%&|^@".indexOf(d) >= 0;
    }

    private boolean endsWithColon(int from) {
        int e = from;
        while (e < n && s[e] != '\n' && s[e] != '#') e++;
        while (e > from && (s[e - 1] == ' ' || s[e - 1] == '\t' || s[e - 1] == '\r')) e--;
        return e > from && s[e - 1] == ':';
    }

    /** Whether a name or a number starts at {@code j}, which Python lets touch the closing quote of a string
     *  only as a keyword or as the prefix of the next string. */
    boolean touches(int j) {
        if (j >= n) return false;
        char c = s[j];
        if (c >= '0' && c <= '9') return true;
        if (!identStart(c)) return false;
        int k = j + 1;
        while (k < n && identPart(s[k])) k++;
        if (k < n && k - j <= 2 && (s[k] == '\'' || s[k] == '"') && prefix(j, k) >= 0) return false;
        return switch (new String(s, j, k - j)) {
            case "False", "None", "True", "and", "as", "assert", "async", "await", "break", "class", "continue",
                 "def", "del", "elif", "else", "except", "finally", "for", "from", "global", "if", "import", "in",
                 "is", "lambda", "nonlocal", "not", "or", "pass", "raise", "return", "try", "while", "with",
                 "yield" -> false;
            default -> true;
        };
    }

    static boolean identStart(char c) {
        return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || c == '_' || (c >= 0x80 && Character.isLetter(c));
    }

    static boolean identPart(char c) {
        return identStart(c) || (c >= '0' && c <= '9') || (c >= 0x80 && Character.isLetterOrDigit(c));
    }
}
