"""refactor-touched.sh's touched-files list, run in-process."""
import subprocess
import sys

USAGE = "usage: refactor-touched.sh <commit> | --issue <base>"


def main(argv):
    rev = argv[0] if argv else ""
    if rev == "--issue":
        rev = argv[1] if len(argv) > 1 else ""
    if not rev:
        print(USAGE, file=sys.stderr)
        return 2
    check = subprocess.run(["git", "rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}"],
                           stdout=subprocess.DEVNULL)
    if check.returncode != 0:
        print(f"refactor-touched: cannot resolve commit '{rev}'", file=sys.stderr)
        print(USAGE, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
