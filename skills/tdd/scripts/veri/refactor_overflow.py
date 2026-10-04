"""refactor-overflow.sh's logic, run in-process."""
import os
import re
import subprocess
import sys

USAGE = "refactor-overflow: usage: refactor-overflow.sh <n> <owed-file> <reached>"
NUMBER = re.compile(r"[0-9]+")


def main(argv):
    n, owed, reached, skipped = (list(argv[:4]) + [""] * 4)[:4]
    if not NUMBER.fullmatch(n) or not owed or not NUMBER.fullmatch(reached):
        print(USAGE, file=sys.stderr)
        return 2
    if skipped and not os.path.isfile(skipped):
        print(f"refactor-overflow: no such skipped file: {skipped}", file=sys.stderr)
        return 2
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    listed = subprocess.run([os.path.join(here, "refactor-owed.sh"), "list", owed],
                            stdout=subprocess.PIPE, text=True)
    if listed.returncode:
        return listed.returncode
    text = ""
    if skipped:
        with open(skipped) as f:
            text = f.read()
    text += "\n".join(listed.stdout.split("\n")[int(reached):])
    unreached = text.rstrip("\n")
    if not unreached:
        return 3
    body = f"Structural candidates #{n}'s closing pass could not reach:\n\n" + "\n".join(
        f"- {line}" for line in unreached.split("\n"))
    url = subprocess.run(["gh", "api", "repos/{owner}/{repo}/issues",
                          "-f", f"title=Refactor owed by #{n}", "-f", f"body={body}",
                          "-q", ".html_url"], stdout=subprocess.PIPE, text=True).stdout
    print(url.rstrip("\n"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
