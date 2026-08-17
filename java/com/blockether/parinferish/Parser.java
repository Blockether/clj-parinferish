package com.blockether.parinferish;

/**
 * The recursive-descent reader and the repair rules, translated one-to-one from
 * parinferish 0.8.0 — indent mode, paren mode, smart mode and the plain parse.
 *
 * <p>Upstream built a hiccup tree of tokens with metadata maps and then flattened
 * it back into a string. Here every collection appends <em>output ops</em>
 * (copy this source range / insert this character / insert these spaces) to one
 * growable int buffer, and a bailed-out branch simply truncates the buffer back
 * to the last committed op — which is exactly upstream rewinding its token index
 * and dropping the pending whitespace. One buffer, one pass, no tree.
 */
final class Parser {

    static final int MODE_NONE = 0;
    static final int MODE_INDENT = 1;
    static final int MODE_PAREN = 2;
    static final int MODE_SMART = 3;

    static final int ACT_NONE = 0;
    static final int ACT_INSERT = 1;
    static final int ACT_REMOVE = 2;

    private static final int OP_COPY = 0;
    private static final int OP_CHAR = 1;
    private static final int OP_SPACES = 2;

    /** Stands in for upstream's `nil` :min-indent — "this collection has no floor". */
    private static final int NO_INDENT = Integer.MIN_VALUE;
    /** Stands in for upstream's `nil` max-indent in paren mode. */
    private static final int NO_MAX = Integer.MAX_VALUE;

    private final Lexer lx;
    private final int mode;
    private final int cursorLine;
    private final int cursorColumn;

    private int index = -1;
    String error;

    private int opCount;
    private int[] opKind;
    private int[] opA;
    private int[] opB;
    private int[] opAct;
    private int[] opTok;

    /** Fields the last {@link #readStructured} filled in — upstream's returned node. */
    private byte rsKind;
    private boolean rsColl;
    private int rsIndent;
    private int rsTok;

    Parser(Lexer lx, int mode, int cursorLine, int cursorColumn) {
        this.lx = lx;
        this.mode = mode;
        this.cursorLine = cursorLine;
        this.cursorColumn = cursorColumn;
        int guess = Math.max(16, lx.count + 8);
        this.opKind = new int[guess];
        this.opA = new int[guess];
        this.opB = new int[guess];
        this.opAct = new int[guess];
        this.opTok = new int[guess];
    }

    // ── the op buffer ────────────────────────────────────────────────────────

    private void ensure(int extra) {
        if (opCount + extra <= opKind.length) {
            return;
        }
        int n = Math.max(opCount + extra, opKind.length * 2);
        opKind = java.util.Arrays.copyOf(opKind, n);
        opA = java.util.Arrays.copyOf(opA, n);
        opB = java.util.Arrays.copyOf(opB, n);
        opAct = java.util.Arrays.copyOf(opAct, n);
        opTok = java.util.Arrays.copyOf(opTok, n);
    }

    private int append(int kind, int a, int b, int act, int tok) {
        ensure(1);
        opKind[opCount] = kind;
        opA[opCount] = a;
        opB[opCount] = b;
        opAct[opCount] = act;
        opTok[opCount] = tok;
        return opCount++;
    }

    private void copyToken(int tok, int act) {
        append(OP_COPY, lx.start[tok], lx.end[tok], act, tok);
    }

    private void insertAt(int at, int kind, int a, int b, int act) {
        ensure(1);
        int tail = opCount - at;
        if (tail > 0) {
            System.arraycopy(opKind, at, opKind, at + 1, tail);
            System.arraycopy(opA, at, opA, at + 1, tail);
            System.arraycopy(opB, at, opB, at + 1, tail);
            System.arraycopy(opAct, at, opAct, at + 1, tail);
            System.arraycopy(opTok, at, opTok, at + 1, tail);
        }
        opKind[at] = kind;
        opA[at] = a;
        opB[at] = b;
        opAct[at] = act;
        opTok[at] = -1;
        opCount++;
    }

    /**
     * Upstream's `insert-delim`. It splits the trailing whitespace off the
     * collection and puts the closer in front of it — which never fires, because
     * a collection only ever commits on a non-whitespace child and the pending
     * whitespace behind that child is rewound, not kept. Reproducing the split
     * here would be WRONG: the ops of a nested collection are inline in this
     * buffer, so walking back over trailing whitespace would walk INTO the child
     * and close this collection inside it.
     */
    private void insertCloser(char closer, int fallbackTok) {
        int i = opCount - 1;
        while (i >= 0 && opTok[i] < 0) {
            i--;
        }
        int pos = i >= 0 ? lx.end[opTok[i]] : lx.end[fallbackTok];
        append(OP_CHAR, closer, pos, ACT_INSERT, -1);
    }

    // ── reading ──────────────────────────────────────────────────────────────

    /**
     * Reads the next token, descending into a whole collection when it opens one.
     * Answers false for end of input and for a token that starts left of
     * {@code minIndent} — in both cases the caller rewinds.
     */
    private boolean readStructured(int minIndent, int indentChange) {
        int i = ++index;
        if (i >= lx.count) {
            return false;
        }
        byte k = lx.kind[i];
        if (minIndent != NO_INDENT && !Lexer.isWhitespace(k) && lx.col[i] < minIndent) {
            return false;
        }
        if (k == Lexer.DELIMITER) {
            char c = lx.src[lx.start[i]];
            if (Lexer.isOpenDelim(c, lx.end[i] - lx.start[i] == 2)) {
                int effective = mode;
                if (mode == MODE_SMART) {
                    boolean beforeCursor = lx.line[i] < cursorLine
                            || (lx.line[i] == cursorLine && lx.col[i] < cursorColumn);
                    effective = beforeCursor ? MODE_INDENT : MODE_PAREN;
                }
                switch (effective) {
                    case MODE_INDENT: readCollIndent(i); break;
                    case MODE_PAREN: readCollParen(i, indentChange); break;
                    default: readCollPlain(i); break;
                }
                rsKind = k;
                rsColl = true;
                rsIndent = lx.indent[i];
                rsTok = i;
                return true;
            }
        }
        rsKind = k;
        rsColl = false;
        rsIndent = lx.indent[i];
        rsTok = i;
        return true;
    }

    /**
     * Indent mode: indentation is the truth and delimiters bend. A line indented
     * left of the collection's own indent closes it (a closer is inserted at the
     * end of the last line that belonged to it); a closer that arrives while
     * deeper lines follow is moved down past them; a closer of the wrong kind is
     * dropped.
     */
    private void readCollIndent(int openerTok) {
        char endDelim = Lexer.closerFor(lx.src[lx.start[openerTok]]);
        int indent = lx.indent[openerTok];
        copyToken(openerTok, ACT_NONE);
        int lastIndex = index;
        int lastOps = opCount;
        while (true) {
            if (!readStructured(indent, 0)) {
                index = lastIndex;
                opCount = lastOps;
                insertCloser(endDelim, openerTok);
                return;
            }
            if (!rsColl && Lexer.isWhitespace(rsKind)) {
                copyToken(rsTok, ACT_NONE);          // pending: truncated away if we bail
                continue;
            }
            if (rsIndent < indent) {
                index = lastIndex;
                opCount = lastOps;
                insertCloser(endDelim, openerTok);
                return;
            }
            if (!rsColl && rsKind == Lexer.DELIMITER) {
                char c = lx.src[lx.start[rsTok]];
                if (c == endDelim) {
                    int slot = append(OP_COPY, lx.start[rsTok], lx.end[rsTok], ACT_NONE, rsTok);
                    int closerTok = rsTok;
                    if (readNextTokensWithIndent(indent)) {
                        opAct[slot] = ACT_REMOVE;
                        int pos = opTok[opCount - 1] >= 0 ? lx.end[opTok[opCount - 1]] : lx.end[closerTok];
                        append(OP_CHAR, endDelim, pos, ACT_INSERT, -1);
                    }
                    return;
                }
                copyToken(rsTok, ACT_REMOVE);
                lastIndex = index;
                lastOps = opCount;
                continue;
            }
            if (!rsColl) {
                copyToken(rsTok, ACT_NONE);
            }
            lastIndex = index;
            lastOps = opCount;
        }
    }

    /**
     * The lookahead behind a closing delimiter: every line that follows and is
     * indented deeper than this collection belongs INSIDE it, so the closer is
     * moved past them. Nothing is committed until a token appears after a
     * newline; whatever is left uncommitted is rewound for the caller to re-read.
     */
    private boolean readNextTokensWithIndent(int indent) {
        int lastIndex = index;
        int lastOps = opCount;
        boolean newLine = false;
        boolean any = false;
        while (readStructured(indent, 0)) {
            if (!rsColl && rsKind == Lexer.DELIMITER) {
                copyToken(rsTok, ACT_REMOVE);
                continue;
            }
            if (!rsColl && Lexer.isWhitespace(rsKind)) {
                copyToken(rsTok, ACT_NONE);
                newLine = newLine || rsKind == Lexer.NEWLINE_INDENT;
                continue;
            }
            if (!rsColl) {
                copyToken(rsTok, ACT_NONE);
            }
            if (newLine) {
                lastIndex = index;
                lastOps = opCount;
                any = true;
            }
        }
        index = lastIndex;
        opCount = lastOps;
        return any;
    }

    /**
     * Paren mode: the delimiters are the truth and indentation bends. Lines are
     * pushed right to clear the enclosing collection's indent, or pulled left when
     * they run past the last child collection.
     */
    private void readCollParen(int openerTok, int indentChange) {
        char endDelim = Lexer.closerFor(lx.src[lx.start[openerTok]]);
        int minIndent = lx.indent[openerTok] + indentChange;
        copyToken(openerTok, ACT_NONE);
        int maxIndent = NO_MAX;
        int ic = indentChange;
        while (true) {
            if (!readStructured(NO_INDENT, ic)) {
                error = "EOF while reading";
                return;
            }
            if (!rsColl && rsKind == Lexer.NEWLINE_INDENT) {
                int current = lx.indent[rsTok];
                int next;
                if (current < minIndent) {
                    next = minIndent - current;
                } else if (maxIndent != NO_MAX && current > maxIndent) {
                    next = maxIndent - current;
                } else {
                    next = 0;
                }
                if (next > 0) {
                    copyToken(rsTok, ACT_NONE);
                    append(OP_SPACES, next, lx.end[rsTok], ACT_INSERT, -1);
                } else if (next < 0) {
                    append(OP_COPY, lx.start[rsTok], lx.end[rsTok] + next, ACT_NONE, rsTok);
                    append(OP_COPY, lx.end[rsTok] + next, lx.end[rsTok], ACT_REMOVE, rsTok);
                } else {
                    copyToken(rsTok, ACT_NONE);
                }
                ic = next;
                continue;
            }
            if (rsColl) {
                int m = rsIndent - 1;
                maxIndent = Math.min(m, maxIndent);
                continue;
            }
            if (rsKind == Lexer.DELIMITER) {
                copyToken(rsTok, ACT_NONE);
                if (lx.src[lx.start[rsTok]] != endDelim) {
                    error = "Unmatched delimiter";
                }
                return;
            }
            copyToken(rsTok, ACT_NONE);
        }
    }

    /** No repair at all: read the structure, report what does not balance. */
    private void readCollPlain(int openerTok) {
        char endDelim = Lexer.closerFor(lx.src[lx.start[openerTok]]);
        copyToken(openerTok, ACT_NONE);
        while (true) {
            if (!readStructured(NO_INDENT, 0)) {
                error = "EOF while reading";
                return;
            }
            if (rsColl) {
                continue;
            }
            if (rsKind == Lexer.DELIMITER) {
                copyToken(rsTok, ACT_NONE);
                if (lx.src[lx.start[rsTok]] != endDelim) {
                    error = "Unmatched delimiter";
                }
                return;
            }
            copyToken(rsTok, ACT_NONE);
        }
    }

    void parse() {
        while (readStructured(NO_INDENT, 0)) {
            if (rsColl) {
                continue;
            }
            boolean stray = rsKind == Lexer.DELIMITER && Lexer.isCloseDelim(lx.src[lx.start[rsTok]]);
            if (stray && (mode == MODE_INDENT || mode == MODE_SMART)) {
                copyToken(rsTok, ACT_REMOVE);
            } else {
                copyToken(rsTok, ACT_NONE);
                if (stray) {
                    error = "Unmatched delimiter";
                }
            }
        }
    }

    /**
     * Renders the ops. `disabled` drops every insertion and keeps the text of
     * every removal, which is the source verbatim: a file paren mode could not
     * read is a file it must not rewrite.
     */
    String render(boolean disabled) {
        StringBuilder sb = new StringBuilder(lx.length + 16);
        for (int i = 0; i < opCount; i++) {
            int act = opAct[i];
            if (disabled ? act == ACT_INSERT : act == ACT_REMOVE) {
                continue;
            }
            switch (opKind[i]) {
                case OP_COPY:
                    sb.append(lx.src, opA[i], opB[i] - opA[i]);
                    break;
                case OP_CHAR:
                    sb.append((char) opA[i]);
                    break;
                default:
                    for (int s = 0; s < opA[i]; s++) {
                        sb.append(' ');
                    }
                    break;
            }
        }
        return sb.toString();
    }

    /**
     * The insertions and removals the render applied, in output order. A disabled
     * render applied none, by definition.
     */
    java.util.List<Parinfer.Edit> collectEdits(boolean disabled) {
        java.util.List<Parinfer.Edit> edits = new java.util.ArrayList<>();
        if (disabled) {
            return edits;
        }
        for (int i = 0; i < opCount; i++) {
            switch (opAct[i]) {
                case ACT_REMOVE:
                    edits.add(Parinfer.Edit.of(lx, Parinfer.Edit.Action.REMOVE, opA[i],
                            new String(lx.src, opA[i], opB[i] - opA[i])));
                    break;
                case ACT_INSERT:
                    edits.add(Parinfer.Edit.of(lx, Parinfer.Edit.Action.INSERT, opB[i],
                            opKind[i] == OP_CHAR ? String.valueOf((char) opA[i]) : " ".repeat(opA[i])));
                    break;
                default:
                    break;
            }
        }
        return edits;
    }
}
