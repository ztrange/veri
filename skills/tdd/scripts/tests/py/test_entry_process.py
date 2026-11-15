"""Process-starting cases split from unit/test_entry.py, which holds the small cases of the same module."""
import os
import subprocess
import sys

import pytest

from conftest import SCRIPTS


@pytest.mark.process("a real pipe whose read end is closed, observed at interpreter shutdown")
def test_run_leaves_nothing_for_shutdown_to_flush_so_a_real_closed_pipe_still_exits_141_with_an_empty_stderr_1150():
    program = (
        "import sys\n"
        f"sys.path.insert(0, {str(SCRIPTS)!r})\n"
        "from veri import entry\n"
        "def main(argv):\n"
        "    sys.stdout.write('an answer\\n')\n"
        "    return 0\n"
        "entry.run(main, [])\n"
    )
    read_end, write_end = os.pipe()
    os.close(read_end)
    try:
        run = subprocess.run([sys.executable, "-c", program], stdin=subprocess.DEVNULL, stdout=write_end,
                             stderr=subprocess.PIPE, timeout=10)
    finally:
        os.close(write_end)

    assert (run.returncode, run.stderr.decode()) == (141, "")
