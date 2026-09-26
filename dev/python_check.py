"""Parse Python sources with CPython and report whether each one is valid.

Usage: python3 dev/python_check.py FILE...

Prints one tab-separated line per file, in argument order:

    FILE<TAB>ok
    FILE<TAB>error<TAB>LINE<TAB>COLUMN<TAB>MESSAGE

The corpus in test/resources/python/ uses this to record what CPython says about
each case and to check that a repaired case parses. It parses the way a Vis
sandbox block is parsed: top-level `await` is allowed.
"""

import ast
import sys
import warnings


def check(path):
    with open(path, encoding="utf-8", newline="") as f:
        source = f.read()
    try:
        compile(source, path, "exec", flags=ast.PyCF_ONLY_AST, dont_inherit=True)
        return "ok"
    except SyntaxError as e:
        message = " ".join(str(e.msg).split())
        return f"error\t{e.lineno or 0}\t{e.offset or 0}\t{message}"
    except ValueError as e:
        return f"error\t0\t0\t{' '.join(str(e).split())}"


def main(paths):
    # A SyntaxWarning (an invalid escape sequence) is not a parse failure.
    warnings.simplefilter("ignore")
    for path in paths:
        print(f"{path}\t{check(path)}")


if __name__ == "__main__":
    main(sys.argv[1:])
