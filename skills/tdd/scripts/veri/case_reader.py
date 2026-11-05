"""Which paths are test files, and how a test source is cut into its cases."""
import ast
import fnmatch
import re

from js_tests import CALL

JS_EXT = r"\.(?:jsx?|tsx?|mjs|cjs)$"

_TEST_PATTERN = r"(^|/)tests/|\.test\.|\.spec\.(?:jsx?|tsx?|mjs|cjs)$|_test\.go$|(^|/)test_[^/]*\.py$|_test\.py$"
_TEST_FILE = re.compile(_TEST_PATTERN)
_TEST_FILE_BYTES = re.compile(_TEST_PATTERN.encode())


def is_test_path(path):
    pattern = _TEST_FILE_BYTES if isinstance(path, bytes) else _TEST_FILE
    return bool(pattern.search(path))


def is_go_test_file(name):
    return name.endswith("_test.go")


def is_test_file(name):
    return fnmatch.fnmatch(name, "test_*.py") or name.endswith("_test.py")


def is_js_test_file(name, root=""):
    if name.endswith(".d.ts"):
        return False
    if re.search(r"\.(?:test|spec)" + JS_EXT, name):
        return True
    in_tests = "__tests__" in root.replace("\\", "/").split("/")
    return in_tests and re.search(JS_EXT, name) is not None


_CASE = re.compile(r"^\s*(?:(?:async\s+)?def\s+(?=test)|func\s+(?=Test))(\w+)|^\s*name=\"([^\"]+)\"|^\s*" + CALL + r"([\"'`])((?:\\.|.)+?)\3", re.M)


_MODULE_LEVEL = re.compile(r"\n[ \t]*\n(?:[ \t]*\n)*(?:#|\w+[ \t]*\(\))")


_DECORATORS = re.compile(r"(?:\n[ \t]*(?:@[^\n]*)?)+\Z")


def _def_ends(text):
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        return {}
    return {node.lineno: (min([d.lineno for d in node.decorator_list] + [node.lineno]), node.end_lineno)
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}


def _helpers_only(tail):
    in_function = False
    for line in tail.splitlines():
        if in_function:
            in_function = line.rstrip() != "}"
        elif not line.strip() or line.lstrip().startswith("#"):
            continue
        elif re.match(r"\w+[ \t]*\(\)", line):
            in_function = not line.rstrip().endswith("}")
        else:
            return False
    return True


def _module_level_cut(body):
    for cut in _MODULE_LEVEL.finditer(body):
        if _helpers_only(body[cut.start():]):
            return cut
    return None


def _unescaped(title):
    return re.sub(r"\\(.)", r"\1", title)


def _spans(text):
    found = list(_CASE.finditer(text))
    trailer = re.search(r"^finish\b.*\s*\Z", text, re.M)
    starts = [m.end() - len(m.group().lstrip()) for m in found]
    ends = starts[1:] + [trailer.start() if trailer and found and trailer.start() > found[-1].start() else len(text)]
    return found, starts, ends


def _old_cut_cases_all(text, call_form_only=False):
    found, starts, ends = _spans(text)
    return [(m.group(1) or m.group(2) or m.group(4), text[start:end].rstrip()) for m, start, end in zip(found, starts, ends)
            if m.group(4) or not call_form_only or text.startswith("func", start)]


class UnclosedCase(LookupError):
    pass


def _plain_call_end(text, opening):
    depth = 0
    for i in range(opening, len(text)):
        if text[i] == "(":
            depth += 1
        elif text[i] == ")":
            depth -= 1
            if depth == 0:
                return i + 1
    return None


def _call_end(text, opening):
    # Literal-aware scan first; when it runs off the end of the text inside a string or comment (a regex
    # literal can hold a quote it cannot read), fall back to the plain paren count. A scan that reaches the
    # enclosing block's "}" first (False) found a call that never closes: no fallback may cut it at a later ")".
    closed = _literal_call_end(text, opening)
    return None if closed is False else closed or _plain_call_end(text, opening)


def _literal_call_end(text, opening):
    depth, braces, quote, escaped, i = 0, 0, None, False, opening
    while i < len(text):
        if quote:
            if escaped:
                escaped = False
            elif text[i] == "\\":
                escaped = True
            elif text[i] == quote:
                quote = None
        elif text.startswith("//", i):
            i += len(text[i:].partition("\n")[0])
        elif text.startswith("/*", i):
            i = text.find("*/", i + 2)
            if i < 0:
                return None
            i += 1
        elif text[i] in "'\"`":
            quote = text[i]
        elif text[i] == "(":
            depth += 1
        elif text[i] == ")":
            depth -= 1
            if depth == 0:
                return i + 1
        elif text[i] == "{":
            braces += 1
        elif text[i] == "}":
            braces -= 1
            if braces < 0:
                return False
        i += 1
    return None


def _cases(text):
    found, starts, ends = _spans(text)
    lines, def_ends = text.splitlines(keepends=True), _def_ends(text)
    cases = []
    for m, start, end in zip(found, starts, ends):
        body = text[start:end]
        span = def_ends.get(text.count("\n", 0, start) + 1)
        closed = _call_end(text, text.rfind("(", start, m.start(4))) if m.group(4) else None
        if m.group(1) and span:
            body = "".join(lines[span[0] - 1:span[1]]).rstrip()
        elif closed:
            body = text[start:closed]
        elif m.group(4):
            raise UnclosedCase("the call of case %s never closes" % _unescaped(m.group(4)))
        else:
            if m.group(1):
                body = "".join(body.partition("\n}")[:2])
            else:
                cut = _module_level_cut(body)
                body = body[:cut.start()] if cut else body
            body = _DECORATORS.sub("", body.rstrip()).rstrip()
        cases.append((m.group(1) or m.group(2) or _unescaped(m.group(4)), body))
    return cases


def cut_prefix(case):
    return case[:-1] if case.endswith("…") else case[:-3] if case.endswith("...") else None


def _js_title_pattern(case):
    prefix = cut_prefix(case)
    gap = "(?:(?!\\1).)*"
    if prefix is not None:
        title = "(%s%s)" % (re.escape(prefix), gap)
    else:
        title = "(%s)" % gap.join(re.escape(part) for part in re.split(r"…|\.\.\.", case))
    return re.compile(CALL + r"(['\"])" + title + r"\1")


def defined_name(case, text, py_file, go_file):
    cut = cut_prefix(case)
    if go_file and case.startswith("Test"):
        match = re.search(r"func (%s)\(" % re.escape(case), text)
    elif py_file and case.startswith("test_"):
        pattern = r"def (%s\w*)\(" % re.escape(cut) if cut else r"def (%s)\(" % re.escape(case)
        match = re.search(pattern, text)
    else:
        return None
    return match.group(1) if match else None


def live_titles(case, text):
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)

    def code(prefix):
        return re.sub(r"\"[^\"]*\"|'[^']*'|`[^`]*`", "", prefix)
    return [m.group(2) for m in _js_title_pattern(case).finditer(text)
            if "//" not in code(text[text.rfind("\n", 0, m.start()) + 1:m.start()])]
