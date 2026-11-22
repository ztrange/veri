"""refactor-touched.sh's touched-files list, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import re
import subprocess
import sys

import entry

USAGE = "usage: refactor-touched.sh <commit> | --issue <base> [--candidate <text>]"


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


def touched_files(span):
    """The paths `git diff --name-only <span>` prints, in its order, minus those under `.tdd/`."""
    diff = subprocess.run(["git", "diff", "--name-only", *span],
                          stdout=subprocess.PIPE, text=True)
    return [p for p in diff.stdout.splitlines() if not p.startswith(".tdd/")]


def main(argv):
    candidate = None
    check_only = "--check" in argv
    argv = [a for a in argv if a != "--check"]
    if "--candidate" in argv:
        i = argv.index("--candidate")
        candidate = argv[i + 1] if i + 1 < len(argv) else ""
        argv = argv[:i] + argv[i + 2:]
    if check_only and candidate is None:
        return entry.refuse(usage=USAGE)
    rev = argv[0] if argv else ""
    span = [f"{rev}^", rev]
    if rev == "--issue":
        rev = argv[1] if len(argv) > 1 else ""
        span = [rev, "HEAD"]
    if not rev:
        return entry.refuse(usage=USAGE)
    check = subprocess.run(["git", "rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}"],
                           stdout=subprocess.DEVNULL)
    if check.returncode != 0:
        return entry.refuse(f"refactor-touched: cannot resolve commit '{rev}'", usage=USAGE)
    touched = touched_files(span)
    if not touched:
        return 3
    if candidate:
        named = list(dict.fromkeys(named_files(candidate)))
        if check_only and named and not any(p in touched for p in named):
            return 1
        touched += [p for p in named if p not in touched]
    if not check_only:
        print(",".join(touched))
    return 0


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
