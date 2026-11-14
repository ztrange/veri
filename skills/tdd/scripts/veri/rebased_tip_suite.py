"""rebased-tip-suite.sh's logic, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

import suite_mode


def main(argv):
    return suite_mode.run("rebased-tip-suite.sh", "VERI_REBASED_TIP_SUITE")


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
