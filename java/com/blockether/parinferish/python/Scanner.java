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

    private static final String[] COMPOUND = {"def", "class", "with", "for", "while", "if", "try", "async"};

    /** How many of the innermost open brackets a problem records, and how far a closer looks down
     *  the stack for its opener. Real code nests far less; only degenerate input nests deeper, and
     *  copying or searching whole stacks for it would make the scan quadratic. */
    private static final int WINDOW = 32;

    private static final int F_STRING = 0;
    private static final int F_FIELD = 1;
    private static final int F_SPEC = 2;

    final String text;
    final char[] s;
    final int n;

    /** Physical lines: start offset, bracket depth at the start (-1 when it starts inside a string),
     *  whether it continues a backslash-ended line, and where its comment starts (-1 for none). */
    final int lines;
    final int[] lineStart;
    final int[] lineDepth;
    final boolean[] lineCont;
    final int[] lineComment;

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

    private int cursor;
    private int stmtIndent;

    Scanner(String text) {
        this.text = text;
        this.s = text.toCharArray();
        this.n = s.length;
        int c = 1;
        for (int i = 0; i < n; i++) {
            if (s[i] == '\n') c++;
        }
        lines = c;
        lineStart = new int[c];
        for (int i = 0, l = 1; i < n; i++) {
            if (s[i] == '\n') lineStart[l++] = i + 1;
        }
        lineDepth = new int[c];
        Arrays.fill(lineDepth, -1);
        lineCont = new boolean[c];
        lineComment = new int[c];
        Arrays.fill(lineComment, -1);
    }

    Scanner scan() {
        line(0, false);
        int i = 0;
        while (i < n && Character.isWhitespace(s[i])) i++;
        if (i < n && s[i] == '>') add(MARKER, i, -1, null);
        i = 0;
        while (i < n) {
            if (frames == 0) {
                i = code(i, 0);
            } else {
                int t = fType[frames - 1];
                i = t == F_STRING ? literal(i) : t == F_FIELD ? code(i, fBase[frames - 1]) : spec(i);
            }
        }
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
                if (frames == 0) line(i + 1, false);
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
                    if (frames == 0) line(j + 1, true);
                    yield j + 1;
                }
                add(STRAY_BACKSLASH, i, -1, null);
                yield i + 1;
            }
            case '\'', '"' -> string(i, i, false);
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
                if (frames == 0 && depth > 0) {
                    add(SEMICOLON, i, stPos[depth - 1], openWindow());
                    depth = 0;
                } else if (frames == 0 && compound(i + 1)) {
                    add(COMPOUND_AFTER_SEMICOLON, i, -1, null);
                }
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
                        if (p >= 0) yield string(i, j, p == 1);
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
            if (e < n && text.startsWith(k, p) && !identPart(s[e])) return true;
        }
        return false;
    }

    /** -1 when {@code [i, j)} is no string prefix, 1 for an f- or t-string, 0 otherwise. */
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
        return f ? 1 : 0;
    }

    private int string(int start, int qp, boolean fmt) {
        char q = s[qp];
        boolean triple = qp + 2 < n && s[qp + 1] == q && s[qp + 2] == q;
        int j = qp + (triple ? 3 : 1);
        if (fmt) {
            frame(F_STRING, start, depth);
            fQuote[frames - 1] = qp;
            fTriple[frames - 1] = triple;
            return j;
        }
        while (j < n) {
            char c = s[j];
            if (c == '\\') {
                j += j + 2 < n && s[j + 1] == '\r' && s[j + 2] == '\n' ? 3 : 2;
                continue;
            }
            if (c == q) {
                if (!triple) return j + 1;
                if (j + 2 < n && s[j + 1] == q && s[j + 2] == q) return j + 3;
            } else if (c == '\n' && !triple) {
                add(UNTERMINATED_STRING, start, j, null);
                return j;
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
        if (c == '\\') return escape(i);
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
        if (c == '\\') return escape(i);
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

    /** A backslash in an f-string's text escapes the next character, but never a brace. */
    private int escape(int i) {
        int j = i + 1;
        if (j < n && (s[j] == '{' || s[j] == '}')) return j;
        if (j + 1 < n && s[j] == '\r' && s[j + 1] == '\n') return j + 2;
        return Math.min(n, j + 1);
    }

    private int end(int f, int next) {
        depth = fBase[f];
        frames = f;
        return next;
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
        }
        fType[frames] = type;
        fStart[frames] = start;
        fBase[frames] = base;
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
        lineDepth[l] = depth;
        lineCont[l] = cont;
        if (cont) return;
        int f = p;
        while (f < n && (s[f] == ' ' || s[f] == '\t' || s[f] == '\f')) f++;
        if (f >= n || s[f] == '\n' || s[f] == '\r' || s[f] == '#') return;
        int col = width(p, f);
        if (depth == 0) {
            stmtIndent = col;
        } else if (col <= stmtIndent && startsStatement(f)) {
            if (suspects == suspectLine.length) {
                suspectLine = Arrays.copyOf(suspectLine, suspects * 2);
                suspectOpen = Arrays.copyOf(suspectOpen, suspects * 2);
            }
            suspectLine[suspects] = l;
            suspectOpen[suspects] = openWindow();
            suspects++;
        }
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
        switch (text.substring(f, j)) {
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

    static boolean identStart(char c) {
        return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || c == '_' || (c >= 0x80 && Character.isLetter(c));
    }

    static boolean identPart(char c) {
        return identStart(c) || (c >= '0' && c <= '9') || (c >= 0x80 && Character.isLetterOrDigit(c));
    }
}
