"""leaf-launchable.sh's launch probe, run in-process."""
# hazard: runs on the python3 it may refuse, so nothing here may need more than Python 3.9.
import os
import subprocess
import sys
import tempfile

import launch_floor


def main(argv):
    if launch_floor.bash_refusal("leaf-launchable") or launch_floor.python_refusal("leaf-launchable"):
        return 2
    leaf_bin = os.environ.get("CLAUDE_BIN") or "claude"
    with tempfile.TemporaryFile() as probe_err:
        try:
            status = subprocess.call([leaf_bin, "--version"], stdout=subprocess.DEVNULL, stderr=probe_err)
        except OSError as error:
            said = os.fsencode("%s\n" % error)
        else:
            if status == 0:
                return 0
            probe_err.seek(0)
            said = probe_err.read()
    sys.stderr.flush()
    sys.stderr.buffer.write(diagnostic(leaf_bin, said))
    sys.stderr.buffer.flush()
    return 2


def diagnostic(leaf_bin, said):
    lines = said.split(b"\n")
    block = b"".join(b"    " + line + b"\n" for line in lines[:-1])
    if lines[-1]:
        block += b"    " + lines[-1]
    return (b"leaf-launchable: the leaf binary (" + os.fsencode(leaf_bin)
            + b") could not be launched, so every leaf of this run would die at launch. It said:\n"
            + block
            + ("Run the conductor from a plain shell instead — the supported invocation is:\n"
               "    claude -p \"/tdd <issue-number>\"\n"
               "veri does not work around this itself: a guard of this kind names a risk the binary is refusing to"
               " take, and taking it silently on the operator's behalf would put that risk on them without their"
               " knowledge.\n").encode("utf-8"))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
