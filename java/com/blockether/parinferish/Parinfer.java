package com.blockether.parinferish;

import java.util.List;
import java.util.Objects;

/**
 * Parinfer for Clojure source: reads the delimiters and the indentation of a
 * file and returns the file with the delimiters (or the indentation) repaired.
 *
 * <p>This is a from-scratch Java rewrite of
 * <a href="https://github.com/oakes/parinferish">parinferish</a> 0.8.0, whose
 * behaviour it reproduces token for token. The rewrite exists for one reason:
 * upstream re-matched eleven anchored regexes against a freshly copied remainder
 * string for every token, so repairing a whole file cost time quadratic in its
 * size — seconds for a ten-thousand-line namespace. Here a single scan fills
 * primitive arrays and the repair appends copy/insert ops to one int buffer, so
 * cost is linear in the source.
 *
 * <p>Every entry point is a pure function of its arguments: no shared state, no
 * caches, safe to call from any number of threads.
 *
 * <h2>Modes</h2>
 * <ul>
 *   <li>{@link #indentMode(String)} — indentation is the truth: closing
 *       delimiters are inserted, moved down or dropped so the structure matches
 *       how the code is indented.</li>
 *   <li>{@link #parenMode(String)} — the delimiters are the truth: lines are
 *       re-indented to match the structure they are actually inside.</li>
 *   <li>{@link #smartMode(String, int, int)} — indent mode for the collections
 *       that start before the cursor, paren mode for the rest.</li>
 *   <li>{@link Mode#NONE} — no repair; read the source and report what does not
 *       balance ({@link Result#errorMessage()}).</li>
 * </ul>
 *
 * <p>A source whose <em>strings</em> do not terminate, or that ends a line on a
 * backslash, is returned verbatim in every mode: an unreadable file is one this
 * library must not rewrite.
 */
public final class Parinfer {

    /** Which truth the repair keeps: the indentation, the delimiters, or neither. */
    public enum Mode { NONE, INDENT, PAREN, SMART }

    private Parinfer() {
    }

    /** Repairs {@code source} with indent mode and returns the repaired text. */
    public static String indentMode(String source) {
        return parse(source, Mode.INDENT).text();
    }

    /** Repairs {@code source} with paren mode and returns the repaired text. */
    public static String parenMode(String source) {
        return parse(source, Mode.PAREN).text();
    }

    /**
     * Repairs {@code source} with smart mode: collections that start before the
     * cursor are read in indent mode, the rest in paren mode. Both coordinates are
     * zero-based.
     */
    public static String smartMode(String source, int cursorLine, int cursorColumn) {
        return parse(source, Mode.SMART, cursorLine, cursorColumn).text();
    }

    /** Parses (and, unless {@link Mode#NONE}, repairs) {@code source}. */
    public static Result parse(String source, Mode mode) {
        if (mode == Mode.SMART) {
            throw new IllegalArgumentException("Smart mode requires a cursor line and column");
        }
        return parse(source, mode, -1, -1);
    }

    /** Parses (and, unless {@link Mode#NONE}, repairs) {@code source}. */
    public static Result parse(String source, Mode mode, int cursorLine, int cursorColumn) {
        Objects.requireNonNull(source, "source");
        Objects.requireNonNull(mode, "mode");
        Lexer lx = new Lexer(source.toCharArray());
        lx.scan();
        // A source the scanner could not read has no repair: upstream drops the
        // mode outright, and every mode then renders the input verbatim.
        int m = lx.error != null ? Parser.MODE_NONE : modeCode(mode);
        Parser parser = new Parser(lx, m, cursorLine, cursorColumn);
        parser.parse();
        // The scanner's error wins over the parser's: an unterminated string is
        // WHY the reader then ran out of input, and the root cause is the useful
        // one to report.
        String error = lx.error != null ? lx.error : parser.error;
        boolean disabled = m == Parser.MODE_PAREN && error != null;
        return new Result(parser, source, parser.render(disabled), error, disabled);
    }

    private static int modeCode(Mode mode) {
        switch (mode) {
            case INDENT: return Parser.MODE_INDENT;
            case PAREN: return Parser.MODE_PAREN;
            case SMART: return Parser.MODE_SMART;
            default: return Parser.MODE_NONE;
        }
    }

    /** What one parse produced. */
    public static final class Result {

        private final Parser parser;
        private final String source;
        private final String text;
        private final String error;
        private final boolean disabled;
        private List<Edit> edits;

        Result(Parser parser, String source, String text, String error, boolean disabled) {
            this.parser = parser;
            this.source = source;
            this.text = text;
            this.error = error;
            this.disabled = disabled;
        }

        /** The repaired source — equal to {@link #source()} when nothing changed. */
        public String text() {
            return text;
        }

        /** The source as given. */
        public String source() {
            return source;
        }

        /** True when the repair changed anything. */
        public boolean isChanged() {
            return !text.equals(source);
        }

        /**
         * The last problem the read found: {@code "Unbalanced quote"},
         * {@code "Backslash at end of line"}, {@code "Unmatched delimiter"},
         * {@code "EOF while reading"}, or null.
         */
        public String errorMessage() {
            return error;
        }

        public boolean hasError() {
            return error != null;
        }

        /**
         * The insertions and removals {@link #text()} applied, in output order —
         * computed on demand, so a caller that only wants the text pays nothing.
         */
        public List<Edit> edits() {
            List<Edit> e = edits;
            if (e == null) {
                e = parser.collectEdits(disabled);
                edits = e;
            }
            return e;
        }
    }

    /** One insertion or removal, positioned in the ORIGINAL source. */
    public static final class Edit {

        public enum Action { INSERT, REMOVE }

        private final Action action;
        private final int offset;
        private final int line;
        private final int column;
        private final String text;

        Edit(Action action, int offset, int line, int column, String text) {
            this.action = action;
            this.offset = offset;
            this.line = line;
            this.column = column;
            this.text = text;
        }

        static Edit of(Lexer lx, Action action, int offset, String text) {
            int line = 0;
            int lineStart = 0;
            for (int i = 0; i < offset && i < lx.length; i++) {
                if (lx.src[i] == '\n') {
                    line++;
                    lineStart = i + 1;
                }
            }
            return new Edit(action, offset, line, offset - lineStart, text);
        }

        public Action action() {
            return action;
        }

        /** Character offset into the original source. */
        public int offset() {
            return offset;
        }

        /** Zero-based line of {@link #offset()} in the original source. */
        public int line() {
            return line;
        }

        /** Zero-based column of {@link #offset()} in the original source. */
        public int column() {
            return column;
        }

        /** The text inserted, or the text removed. */
        public String text() {
            return text;
        }

        @Override
        public String toString() {
            return action + " " + line + ":" + column + " " + text;
        }
    }
}
