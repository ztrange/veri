"""refactor-touched.sh's touched-files list, run in-process."""
import os
import re
import subprocess
import sys

USAGE = "usage: refactor-touched.sh <commit> | --issue <base>"


def refuse(message=None):
    if message:
        print(message, file=sys.stderr)
    print(USAGE, file=sys.stderr)
    return 2


def named_files(candidate):
    tracked = subprocess.run(["git", "ls-files"], stdout=subprocess.PIPE, text=True).stdout.splitlines()
    by_base = {}
    for path in tracked:
        by_base.setdefault(os.path.basename(path), []).append(path)
    named = []
    for token in re.findall(r"[\w./-]+", candidate):
        if token in tracked:
            named.append(token)
        elif len(by_base.get(token, [])) == 1:
            named.append(by_base[token][0])
    return named


def main(argv):
    candidate = None
    if "--candidate" in argv:
        i = argv.index("--candidate")
        candidate = argv[i + 1] if i + 1 < len(argv) else ""
        argv = argv[:i] + argv[i + 2:]
    rev = argv[0] if argv else ""
    span = [f"{rev}^", rev]
    if rev == "--issue":
        rev = argv[1] if len(argv) > 1 else ""
        span = [rev, "HEAD"]
    if not rev:
        return refuse()
    check = subprocess.run(["git", "rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}"],
                           stdout=subprocess.DEVNULL)
    if check.returncode != 0:
        return refuse(f"refactor-touched: cannot resolve commit '{rev}'")
    diff = subprocess.run(["git", "diff", "--name-only", *span],
                          stdout=subprocess.PIPE, text=True)
    touched = [p for p in diff.stdout.splitlines() if not p.startswith(".tdd/")]
    if not touched:
        return 3
    if candidate:
        touched += [p for p in dict.fromkeys(named_files(candidate)) if p not in touched]
    print(",".join(touched))
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
