package com.blockether.parinferish;

/**
 * The scanner: one left-to-right pass over the source, producing parallel
 * primitive arrays. No regular expressions and no {@code substring} — the
 * upstream Clojure implementation re-matched eleven anchored regexes against a
 * freshly copied remainder string for every token, which is what made whole-file
 * repair quadratic in the file size.
 *
 * <p>The token kinds, their order of precedence, and the line/column/indent
 * bookkeeping reproduce parinferish 0.8.0 exactly, because the repair rules that
 * consume them are indentation rules — an off-by-one column changes the answer.
 */
final class Lexer {

    static final byte NEWLINE_INDENT = 0;
    static final byte WHITESPACE = 1;
    static final byte SPECIAL_CHAR = 2;
    static final byte DELIMITER = 3;
    static final byte STRING = 4;
    static final byte CHARACTER = 5;
    static final byte BACKSLASH = 6;
    static final byte COMMENT = 7;
    static final byte NUMBER = 8;
    static final byte SYMBOL = 9;
    /**
     * A character no rule matches — a form feed or a vertical tab. Upstream
     * stopped tokenizing there and silently dropped the rest of the file; we pass
     * the character through untouched instead. See README, "Divergences".
     */
    static final byte RAW = 10;

    /**
     * A lone backslash is not whitespace, but parinferish treats it as such so a
     * closing delimiter can never be inserted right behind it (that would escape
     * the delimiter into a character literal).
     */
    static boolean isWhitespace(byte kind) {
        return kind == NEWLINE_INDENT || kind == WHITESPACE || kind == COMMENT || kind == BACKSLASH;
    }

    static boolean isOpenDelim(char c, boolean twoChars) {
        return twoChars || c == '(' || c == '[' || c == '{';
    }

    static boolean isCloseDelim(char c) {
        return c == ')' || c == ']' || c == '}';
    }

    static char closerFor(char opener) {
        switch (opener) {
            case '(': return ')';
            case '[': return ']';
            default: return '}';   // '{' and "#{"
        }
    }

    /** Java's {@code \s}: what the upstream symbol and character regexes excluded. */
    private static boolean isJavaSpace(char c) {
        return c == ' ' || c == '\t' || c == '\n' || c == '\u000B' || c == '\f' || c == '\r';
    }

    /** What Java's {@code .} refuses to match, i.e. where {@code ;.*} stops. */
    private static boolean isLineTerminator(char c) {
        return c == '\n' || c == '\r' || c == '\u0085' || c == '\u2028' || c == '\u2029';
    }

    private static boolean isDigit(char c) {
        return c >= '0' && c <= '9';
    }

    private static boolean isAsciiLetter(char c) {
        return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z');
    }

    /** The exclusion set of the upstream symbol regex. */
    private static boolean stopsSymbol(char c) {
        if (isJavaSpace(c)) {
            return true;
        }
        switch (c) {
            case '[': case ']': case '{': case '}': case '(': case ')':
            case '\'': case '"': case '`': case ',': case ';': case '\\':
                return true;
            default:
                return false;
        }
    }

    final char[] src;
    final int length;

    int count;
    byte[] kind;
    int[] start;
    int[] end;
    int[] line;
    int[] col;
    int[] indent;

    /** The last error the scan produced, or null. Any error disables every repair. */
    String error;

    Lexer(char[] src) {
        this.src = src;
        this.length = src.length;
        int guess = Math.max(16, src.length / 3 + 8);
        this.kind = new byte[guess];
        this.start = new int[guess];
        this.end = new int[guess];
        this.line = new int[guess];
        this.col = new int[guess];
        this.indent = new int[guess];
    }

    private void grow() {
        int n = kind.length * 2;
        byte[] k = new byte[n];
        System.arraycopy(kind, 0, k, 0, count);
        kind = k;
        start = java.util.Arrays.copyOf(start, n);
        end = java.util.Arrays.copyOf(end, n);
        line = java.util.Arrays.copyOf(line, n);
        col = java.util.Arrays.copyOf(col, n);
        indent = java.util.Arrays.copyOf(indent, n);
    }

    void scan() {
        int p = 0;
        int curLine = 0;
        int curCol = 0;
        int curIndent = 0;
        byte lastKind = -1;
        while (p < length) {
            final char c = src[p];
            byte k;
            int e;
            if (c == '\n') {                                   // ^\n[ ]*
                k = NEWLINE_INDENT;
                e = p + 1;
                while (e < length && src[e] == ' ') {
                    e++;
                }
            } else if (c == ' ' || c == '\t' || c == '\r' || c == ',') {   // ^[ \t\r,]+
                k = WHITESPACE;
                e = p + 1;
                while (e < length) {
                    char d = src[e];
                    if (d == ' ' || d == '\t' || d == '\r' || d == ',') {
                        e++;
                    } else {
                        break;
                    }
                }
            } else if (c == '\'' || c == '`' || c == '~' || c == '^' || c == '@') {   // ^['`~^@]
                k = SPECIAL_CHAR;
                e = p + 1;
            } else if (c == '[' || c == ']' || c == '{' || c == '}' || c == '(' || c == ')') {
                k = DELIMITER;
                e = p + 1;
            } else if (c == '#' && p + 1 < length && src[p + 1] == '{') {   // ^#\{
                k = DELIMITER;
                e = p + 2;
            } else if (c == '"') {
                k = STRING;
                e = scanString(p);
            } else if (c == '\\' && p + 1 < length && !isJavaSpace(src[p + 1])) {   // ^\\\S
                k = CHARACTER;
                e = p + 2;
            } else if (c == '\\') {
                k = BACKSLASH;
                e = p + 1;
            } else if (c == ';') {                             // ^;.*
                k = COMMENT;
                e = p + 1;
                while (e < length && !isLineTerminator(src[e])) {
                    e++;
                }
            } else {
                e = scanNumber(p);
                if (e > p) {
                    k = NUMBER;
                } else {
                    e = p;
                    while (e < length && !stopsSymbol(src[e])) {
                        e++;
                    }
                    if (e > p) {
                        k = SYMBOL;
                    } else {
                        k = RAW;                               // upstream truncated the file here
                        e = p + 1;
                    }
                }
            }

            if (count == kind.length) {
                grow();
            }
            final int tokLine;
            final int startCol;
            if (k == NEWLINE_INDENT) {
                curLine++;
                tokLine = curLine;
                startCol = -1;
                curCol = (e - p) - 1;
                curIndent = curCol;
                if (lastKind == BACKSLASH) {
                    error = "Backslash at end of line";
                }
            } else if (k == STRING) {
                int lastNewline = -1;
                for (int i = p; i < e; i++) {
                    if (src[i] == '\n') {
                        curLine++;
                        lastNewline = i;
                    }
                }
                tokLine = curLine;
                startCol = curCol;
                curCol = lastNewline >= 0 ? e - lastNewline - 1 : curCol + (e - p);
                if (src[e - 1] != '"') {
                    error = "Unbalanced quote";
                }
            } else {
                tokLine = curLine;
                startCol = curCol;
                curCol += e - p;
                if (k == DELIMITER && isOpenDelim(c, e - p == 2)) {
                    curIndent = curCol;
                }
            }

            kind[count] = k;
            start[count] = p;
            end[count] = e;
            line[count] = tokLine;
            col[count] = startCol;
            indent[count] = curIndent;
            count++;
            lastKind = k;
            p = e;
        }
    }

    /**
     * A string token runs to the closing quote inclusive; a backslash swallows the
     * next character. An unterminated string ends at EOF and is reported by the
     * caller — which, upstream and here, is decided by the LAST character being a
     * quote, so the one-character source {@code "} is not an error.
     */
    private int scanString(int p) {
        int i = p + 1;
        while (i < length) {
            char c = src[i];
            if (c == '\\') {
                i += (i + 1 < length) ? 2 : 1;
            } else if (c == '"') {
                return i + 1;
            } else {
                i++;
            }
        }
        return length;
    }

    /** {@code ^[+-]?\d+[/\.]?[a-zA-Z\d]*}, or {@code p} when it does not match. */
    private int scanNumber(int p) {
        int i = p;
        char c = src[i];
        if (c == '+' || c == '-') {
            i++;
        }
        if (i >= length || !isDigit(src[i])) {
            return p;
        }
        while (i < length && isDigit(src[i])) {
            i++;
        }
        if (i < length && (src[i] == '/' || src[i] == '.')) {
            i++;
        }
        while (i < length && (isAsciiLetter(src[i]) || isDigit(src[i]))) {
            i++;
        }
        return i;
    }
}
