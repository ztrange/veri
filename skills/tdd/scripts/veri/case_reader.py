"""Which paths are test files."""
import re

_TEST_FILE = re.compile(r"(^|/)tests/|\.test\.")
_TEST_FILE_BYTES = re.compile(rb"(^|/)tests/|\.test\.")


def is_test_path(path):
    pattern = _TEST_FILE_BYTES if isinstance(path, bytes) else _TEST_FILE
    return bool(pattern.search(path))
