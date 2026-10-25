"""next-unchecked.sh's computation, run in-process."""
import os
import sys

import tunables

if sys.pycache_prefix is None:
    sys.pycache_prefix = tunables.read("VERI_PYCACHE") or os.path.join(tunables.read("TMPDIR") or "/tmp", "veri-pycache-%d" % os.getuid())

from ledger import handed_out, ledger_steps, read_ledger_stdin


def main(argv):
    text = read_ledger_stdin()
    for record in ledger_steps(text):
        if handed_out(record):
            sys.stdout.buffer.write((record[6] + "\n").encode(errors="surrogateescape"))
            return 0
    return 3


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
