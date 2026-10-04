"""refactor-touched.sh's touched-files list, run in-process."""
import subprocess
import sys

USAGE = "usage: refactor-touched.sh <commit> | --issue <base>"


def refuse(message=None):
    if message:
        print(message, file=sys.stderr)
    print(USAGE, file=sys.stderr)
    return 2


def main(argv):
    rev = argv[0] if argv else ""
    if rev == "--issue":
        rev = argv[1] if len(argv) > 1 else ""
    if not rev:
        return refuse()
    check = subprocess.run(["git", "rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}"],
                           stdout=subprocess.DEVNULL)
    if check.returncode != 0:
        return refuse(f"refactor-touched: cannot resolve commit '{rev}'")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
