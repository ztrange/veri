"""Which paths are test files, and how a test source is cut into its cases."""
import ast
import fnmatch
import os
import re

from js_tests import CALL

JS_EXT = r"\.(?:jsx?|tsx?|mjs|cjs)$"

_TEST_PATTERN = r"(^|/)tests/|\.test\.|\.spec\.(?:jsx?|tsx?|mjs|cjs)$|_test\.go$|(^|/)test_[^/]*\.py$|_test\.py$"
_TEST_FILE = re.compile(_TEST_PATTERN)
_TEST_FILE_BYTES = re.compile(_TEST_PATTERN.encode())
# In veri's own tree the pytest leg is the code `make test` runs to decide a suite passed, not a test (#4262).
_PYTEST_LEG_DIR = "skills/tdd/scripts/tests/leg/"
_VERI_PY_TESTS = "skills/tdd/scripts/tests/py"


def is_test_path(path):
    leg = _PYTEST_LEG_DIR.encode() if isinstance(path, bytes) else _PYTEST_LEG_DIR
    if path.startswith(leg) and os.path.isdir(_VERI_PY_TESTS):
        return False
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


CASE_HEAD = _CASE = re.compile(
    r"^\s*(?:(?:async\s+)?def\s+(?=test)|func\s+(?=Test))(\w+)|^\s*" + CALL + r"([\"'`])((?:\\.|.)+?)\2", re.M)


_DECORATORS = re.compile(r"(?:\n[ \t]*(?:@[^\n]*)?)+\Z")


def _def_ends(text):
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        return {}
    return {node.lineno: (min([d.lineno for d in node.decorator_list] + [node.lineno]), node.end_lineno)
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}


def _unescaped(title):
    return re.sub(r"\\(.)", r"\1", title)


def _spans(text):
    found = list(_CASE.finditer(text))
    trailer = re.search(r"^finish\b.*\s*\Z", text, re.M)
    starts = [m.end() - len(m.group().lstrip()) for m in found]
    ends = starts[1:] + [trailer.start() if trailer and found and trailer.start() > found[-1].start() else len(text)]
    return found, starts, ends


def old_cut_cases_all(text, call_form_only=False):
    found, starts, ends = _spans(text)
    return [(m.group(1) or m.group(3), text[start:end].rstrip())
            for m, start, end in zip(found, starts, ends, strict=False)
            if m.group(3) or not call_form_only or text.startswith("func", start)]


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
    # literal it reads as a division can hold a quote), fall back to the plain paren count. A scan that reaches the
    # enclosing block's "}" first (False) found a call that never closes: no fallback may cut it at a later ")".
    closed = _literal_call_end(text, opening)
    return None if closed is False else closed or _plain_call_end(text, opening)


def _divides(text, opening, slash):
    # A "/" right after an operand (a name, a number, a closing paren or bracket) is a division; else, or right
    # after the keyword return, a regex opens.
    before = text[opening:slash].rstrip()
    return (before[-1:].isalnum() or before[-1:] in "_$)]") and not re.search(r"\breturn\Z", before)


def _regex_end(text, slash):
    i, in_class = slash + 1, False
    while i < len(text) and text[i] != "\n" and (in_class or text[i] != "/"):
        if text[i] in "[]":
            in_class = text[i] == "["
        i += 2 if text[i] == "\\" else 1
    return i if text[i:i + 1] == "/" else None


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
        elif text[i] == "/" and not _divides(text, opening, i) and (end := _regex_end(text, i)) is not None:
            i = end
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


def cut_cases(text):
    found, starts, ends = _spans(text)
    lines, def_ends = text.splitlines(keepends=True), _def_ends(text)
    cases = []
    for m, start, end in zip(found, starts, ends, strict=False):
        body = text[start:end]
        span = def_ends.get(text.count("\n", 0, start) + 1)
        closed = _call_end(text, text.rfind("(", start, m.start(3))) if m.group(3) else None
        if m.group(1) and span:
            body = "".join(lines[span[0] - 1:span[1]]).rstrip()
        elif closed:
            body = text[start:closed]
        elif m.group(3):
            raise UnclosedCase("the call of case %s never closes" % _unescaped(m.group(3)))
        else:
            body = "".join(body.partition("\n}")[:2])
            body = _DECORATORS.sub("", body.rstrip()).rstrip()
        cases.append((m.group(1) or _unescaped(m.group(3)), body))
    return cases


def strip_param_suffix(name):
    return re.sub(r"\[.*\]$", "", name)


def cut_prefix(case):
    return case[:-1] if case.endswith("…") else case[:-3] if case.endswith("...") else None


def js_title_pattern(case):
    prefix = cut_prefix(case)
    gap = "(?:(?!\\1).)*"
    if prefix is not None:
        title = "(%s%s)" % (re.escape(prefix), gap)
    else:
        title = "(%s)" % gap.join(re.escape(part) for part in re.split(r"…|\.\.\.", case))
    return re.compile(CALL + r"(['\"])" + title + r"\1")


# wrong_test_route.py (owned by an open PR) still imports the old spelling; drop this once it takes the public one.
_js_title_pattern = js_title_pattern


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
    return [m.group(2) for m in js_title_pattern(case).finditer(text)
            if "//" not in code(text[text.rfind("\n", 0, m.start()) + 1:m.start()])]


def defines_helper(name, text, py_file, go_file):
    escaped = re.escape(name)
    if py_file:
        pattern = r"^def %s\(" % escaped
    elif go_file:
        pattern = r"^func %s\(" % escaped
    else:
        pattern = (r"^\s*(?:export\s+)?(?:(?:async\s+)?function\s+{0}\("
                   r"|const\s+{0}\s*=\s*(?:async\s+)?(?:function\b|\([^)]*\)\s*=>))").format(escaped)
    return re.search(pattern, text, re.M) is not None


def _class_defines(text, classes, case):
    """True when the Python source text holds the class chain `classes` (outermost first, nested by
    definition) and its innermost class defines a method named case; False on a source that does not parse."""
    try:
        body = ast.parse(text).body
    except (SyntaxError, ValueError):
        return False
    for name in classes:
        found = [node for node in body if isinstance(node, ast.ClassDef) and node.name == name]
        if not found:
            return False
        body = found[0].body
    return any(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == case for node in body)


def file_defines(path, case, classes=(), any_title=False):
    """True when the test file at path defines case, by the rules wrong-test-route.sh searches with; with
    classes, only a Python test file whose class chain defines case does (class_defines). A JS title must be
    case itself, unless any_title, where any live title case's pattern matches counts: a name cut at … or ...
    then resolves to the longer title it is a prefix of."""
    root, name = os.path.split(path)
    py_file, go_file, js_file = is_test_file(name), is_go_test_file(name), is_js_test_file(name, root)
    if not (py_file or go_file or js_file):
        return False
    with open(path, encoding="utf-8", errors="replace") as handle:
        text = handle.read()
    if classes:
        return py_file and _class_defines(text, classes, case)
    titles = live_titles(case, text) if js_file else []
    return bool(defined_name(case, text, py_file, go_file) or (titles if any_title else case in titles))
