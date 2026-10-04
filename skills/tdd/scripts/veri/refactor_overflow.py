"""refactor-overflow.sh's logic, run in-process."""
import os
import re
import subprocess
import sys

USAGE = "usage: refactor-overflow.sh <n> <owed-file> <reached>"
NUMBER = re.compile(r"[0-9]+")


def fail(message, code):
    print(f"refactor-overflow: {message}", file=sys.stderr)
    return code


def main(argv):
    n, owed, reached, skipped = (list(argv[:4]) + [""] * 4)[:4]
    if not NUMBER.fullmatch(n) or not owed or not NUMBER.fullmatch(reached):
        return fail(USAGE, 2)
    if skipped and not os.path.isfile(skipped):
        return fail(f"no such skipped file: {skipped}", 2)
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    listed = subprocess.run([os.path.join(here, "refactor-owed.sh"), "list", owed],
                            stdout=subprocess.PIPE, text=True)
    if listed.returncode:
        return listed.returncode
    skip = int(reached, 10)
    start = (skip + 1 + 2**63) % 2**64 - 2**63
    if start < 0:
        return fail(f"illegal offset -- +{start}", 1)
    text = ""
    if skipped:
        with open(skipped) as f:
            text = f.read()
    text += "\n".join(listed.stdout.split("\n")[max(start - 1, 0):])
    unreached = text.rstrip("\n")
    if not unreached:
        return 3
    body = f"Structural candidates #{n}'s closing pass could not reach:\n\n" + "\n".join(
        f"- {line}" for line in unreached.split("\n"))
    filed = subprocess.run(["gh", "api", "repos/{owner}/{repo}/issues",
                            "-f", f"title=Refactor owed by #{n}", "-f", f"body={body}",
                            "-q", ".html_url"], stdout=subprocess.PIPE, text=True)
    if filed.returncode:
        return 2
    print(filed.stdout.rstrip("\n"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
