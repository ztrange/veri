"""refactor-overflow.sh's logic, run in-process."""
import os
import re
import subprocess
import sys

from refactor_owed import out_of_scope_transforms

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
    if listed.returncode not in (0, 3):
        return listed.returncode
    candidates = listed.stdout if listed.returncode == 0 else ""
    skip = int(reached, 10)
    text = ""
    if skipped:
        with open(skipped) as f:
            text = f.read()
    text += "\n".join(candidates.split("\n")[skip:])
    text = text.rstrip("\n")
    structural = text.split("\n") if text else []
    out_of_scope = out_of_scope_transforms(owed)
    if not structural and not out_of_scope:
        return 3
    body = "\n\n".join(
        f"{heading}:\n\n" + "\n".join(f"- {line}" for line in lines)
        for heading, lines in [
            (f"Structural candidates #{n}'s closing pass could not reach", structural),
            (f"Out-of-scope transforms #{n}'s closing pass did not attempt", out_of_scope)]
        if lines)
    filed = subprocess.run(["gh", "api", "repos/{owner}/{repo}/issues",
                            "-f", f"title=Refactor owed by #{n}", "-f", f"body={body}",
                            "-q", ".html_url"], stdout=subprocess.PIPE, text=True)
    if filed.returncode:
        return 2
    print(filed.stdout.rstrip("\n"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
