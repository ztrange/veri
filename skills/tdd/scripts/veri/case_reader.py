"""Which paths are test files."""
import fnmatch
import re

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
