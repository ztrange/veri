"""merge-lock.sh through the real /bin/sh shim."""
import subprocess
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2]


@pytest.mark.process("merge-lock.sh run as the /bin/sh shim it is")
def test_merge_lock_sh_with_no_argument_prints_a_usage_line_naming_take_release_and_holder_and_exits_2():
    done = subprocess.run(["/bin/sh", str(SCRIPTS / "merge-lock.sh")], stdin=subprocess.DEVNULL,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert (done.returncode, all(verb in done.stderr for verb in ("take", "release", "holder"))) == (2, True)
