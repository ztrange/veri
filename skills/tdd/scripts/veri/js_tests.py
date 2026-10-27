import re

JS_EXT = r"\.(?:jsx?|tsx?|mjs|cjs)$"

CALL = r"\b(?:it|test)(?:\.(?:only|skip))?(?:\.each(?:\([^)]*\)|`[^`]*`))?\(\s*"


def is_js_test_file(name, root=""):
    if name.endswith(".d.ts"):
        return False
    if re.search(r"\.(?:test|spec)" + JS_EXT, name):
        return True
    in_tests = "__tests__" in root.replace("\\", "/").split("/")
    return in_tests and re.search(JS_EXT, name) is not None
