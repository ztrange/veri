"""seam-settle.sh's computation, run in-process: after a stage done by hand, write the record that stage's script
would have written, so the next stage runs as after a clean call (PRD 038.1 SC6, SC7)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

import fused
import fused_step
import run_dir
from ledger import handed_out

USAGE = "usage: seam-settle.sh <n> <stage> key=value…"
LEDGER = run_dir.ledger("", "%s")


def main(argv):
    n, stage, pairs = argv[0], argv[1], argv[2:]
    given = fused_step.inputs("seam-settle.sh", n, LEDGER)
    if given is None:
        return 2
    _, wt = given
    values = dict(pair.split("=", 1) for pair in pairs)
    step = fused_step.first_step(wt, n, handed_out)
    target = values["target_test"]
    red_test_id = target if "::" in target else values["test_path"] + "::" + target
    return fused.settle(wt, n, stage, ["step=" + step, "test_path=" + values["test_path"], "target_test=" + target,
                                       "red_test_id=" + red_test_id, "against_unmodified=FAILS"])


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
