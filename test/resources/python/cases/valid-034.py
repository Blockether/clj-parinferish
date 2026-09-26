pseudo_ok_names = ['active','any-link','checked','current','default','defined','dir','disabled','empty','enabled','first-child','first-of-type','focus','focus-visible','focus-within','future','has','host','host-context','hover','in-range','indeterminate','is','lang','last-child','last-of-type','link','local-link','matches','not','nth-child','nth-last-child','nth-last-of-type','nth-of-type','only-child','only-of-type','optional','out-of-range','past','paused','placeholder-shown','playing','read-only','read-write','required','root','scope','target','target-within','user-invalid','visited','where','contains','-soup-contains','-soup-contains-own']
lines_ps = ",\n".join('            "%s"' % n for n in pseudo_ok_names)
partA = '''    class SelectorSyntaxError(Exception):
        """What soupsieve raises for a malformed selector; bs4 lets it through."""

    # Every pseudo-class soupsieve accepts. Anything outside this set -- and
    # every pseudo-element -- makes soupsieve raise NotImplementedError, so
    # this engine raises it too instead of quietly matching nothing.
    _CSS_PSEUDO_CLASSES = frozenset(
        [
%s,
        ]
    )

    # A tag name no markup can produce: how an unresolvable namespace prefix
    # ("ns|p" with no namespace map) is spelled so it matches nothing.
    _CSS_NEVER = chr(0) + "never"

    def _css_ident_ok(name):
        if not name:
            return False
        if name[0].isdigit():
            return False
        for ch in name:
            if ch.isalnum() or ch in ("-", "_", chr(92)) or ord(ch) > 127:
                continue
            return False
        return True

    def _css_bad(selector):
        raise SelectorSyntaxError("Invalid CSS selector: %r" % (selector,))

    def _split_commas(text):
        # Comma-splits a selector without cutting inside [attr], :not(...) or a
        # quoted value.
        parts = []
        buf = []
        square = 0
        paren = 0
        quote = None
        for ch in text:
            if quote is not None:
                buf.append(ch)
                if ch == quote:
                    quote = None
                continue
            if ch == _Q or ch == chr(39):
                quote = ch
                buf.append(ch)
            elif ch == "[":
                square = square + 1
                buf.append(ch)
            elif ch == "]":
                square = square - 1
                buf.append(ch)
            elif ch == "(":
                paren = paren + 1
                buf.append(ch)
            elif ch == ")":
                paren = paren - 1
                buf.append(ch)
            elif ch == "," and square == 0 and paren == 0:
                parts.append("".join(buf))
                buf = []
            else:
                buf.append(ch)
        parts.append("".join(buf))
        return parts

    def _parse_simple(tok):
        tag = None
        idv = None
        classes = []
        attrs = []
        pseudos = []
        i = 0
        n = len(tok)
        stop = (".", "#", "[", ":")
        # leading type selector
        j = i
        while j < n and tok[j] not in stop:
            j = j + 1
        t = tok[i:j]
        if t:
            local = t
            prefix = None
            if "|" in t:
                prefix, _sep, local = t.rpartition("|")
            if local != "*" and not _css_ident_ok(local):
                _css_bad(tok)
            if prefix is not None and prefix not in ("", "*"):
                if not _css_ident_ok(prefix):
                    _css_bad(tok)
                # No namespace map is ever passed here, so a real prefix can
                # never resolve -- soupsieve matches nothing in that case.
                tag = _CSS_NEVER
            elif local != "*":
                tag = local
        i = j
        while i < n:
            c = tok[i]
            if c == "." or c == "#":
                i = i + 1
                s = i
                while i < n and tok[i] not in stop:
                    i = i + 1
                name = tok[s:i]
                if not _css_ident_ok(name):
                    _css_bad(tok)
                if c == ".":
                    classes.append(name)
                else:
                    idv = name
            elif c == "[":
                i = i + 1
                s = i
                while i < n and tok[i] != "]":
                    i = i + 1
                if i >= n:
                    _css_bad(tok)
                body = tok[s:i]
                i = i + 1
                op = None
                for cand in ("~=", "|=", "^=", "$=", "*=", "="):
                    if cand in body:
                        an, av = body.split(cand, 1)
                        op = cand
                        av = av.strip()
                        quoted = len(av) >= 2 and av[0] == av[-1] and av[0] in (_Q, chr(39))
                        if quoted:
                            av = av[1:-1]
                        elif not av:
                            _css_bad(tok)
                        an = an.strip()
                        if not an:
                            _css_bad(tok)
                        attrs.append((an, op, av))
                        break
                if op is None:
                    an = body.strip()
                    if not an:
                        _css_bad(tok)
                    attrs.append((an, None, None))
            elif c == ":":
                i = i + 1
                element = False
                if i < n and tok[i] == ":":
                    element = True
                    i = i + 1
                s = i
                while i < n and tok[i] not in stop and tok[i] != "(":
                    i = i + 1
                pname = tok[s:i].lower()
                parg = None
                if i < n and tok[i] == "(":
                    depth = 0
                    s = i + 1
                    closed = False
                    while i < n:
                        if tok[i] == "(":
                            depth = depth + 1
                        elif tok[i] == ")":
                            depth = depth - 1
                            if depth == 0:
                                closed = True
                                break
                        i = i + 1
                    if not closed:
                        _css_bad(tok)
                    parg = tok[s:i]
                    i = i + 1
                if not pname:
                    _css_bad(tok)
                if element:
                    raise NotImplementedError(
                        "'::%s' pseudo-element is not implemented at this time."
                        % (pname,)
                    )
                if pname not in _CSS_PSEUDO_CLASSES:
                    raise NotImplementedError(
                        "':%s' pseudo-class is not implemented at this time."
                        % (pname,)
                    )
                pseudos.append((pname, parg))
            else:
                i = i + 1
        return (tag, idv, classes, attrs, pseudos)''' % (lines_ps,)
print(partA.count('\n'))