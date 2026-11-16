"""Cases for stub_script.py, the one writer of a `#!/bin/sh` stub script."""
import stat

from stub_script import write_stub


def test_4052_write_stub_writes_the_header_then_the_body_sets_mode_0755_and_returns_the_path(tmp_path):
    path = tmp_path / "claude"

    returned = write_stub(path, 'echo "$@"\nexit 3\n')

    assert (returned, path.read_bytes(), stat.S_IMODE(path.stat().st_mode)) == (
        path, b'#!/bin/sh\necho "$@"\nexit 3\n', 0o755)
