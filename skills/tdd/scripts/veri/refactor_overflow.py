"""refactor-overflow.sh's logic, run in-process."""
import json
import os
import re
import subprocess
import sys

from refactor_owed import out_of_scope_transforms, structural_lines

USAGE = "usage: refactor-overflow.sh <n> <owed-file> <reached>"
NUMBER = re.compile(r"[0-9]+")


def fail(message, code):
    print(f"refactor-overflow: {message}", file=sys.stderr)
    return code


def gh_api(*args):
    return subprocess.run(["gh", "api", *args], stdout=subprocess.PIPE, text=True)


def main(argv):
    n, owed, reached, skipped = (list(argv[:4]) + [""] * 4)[:4]
    if not NUMBER.fullmatch(n) or not owed or not NUMBER.fullmatch(reached):
        return fail(USAGE, 2)
    if skipped and not os.path.isfile(skipped):
        return fail(f"no such skipped file: {skipped}", 2)
    code, candidates = structural_lines(owed)
    if code not in (0, 3):
        return code
    skip = int(reached, 10)
    text = ""
    if skipped:
        with open(skipped) as f:
            text = f.read()
    text += "\n".join(candidates[skip:])
    text = text.rstrip("\n")
    structural = text.split("\n") if text else []
    out_of_scope = out_of_scope_transforms(owed)
    if not structural and not out_of_scope:
        return 3
    title = f"Refactor owed by #{n}"
    found = gh_api("repos/{owner}/{repo}/issues?state=open&per_page=100")
    try:
        existing = next((i for i in json.loads(found.stdout) if i["title"] == title), None)
    except ValueError:
        existing = None
    sections = [
        (f"Structural candidates #{n}'s closing pass could not reach", structural),
        (f"Out-of-scope transforms #{n}'s closing pass did not attempt", out_of_scope)]
    if existing:
        listed = existing["body"].split("\n")
        sections = [(h, [l for l in lines if f"- {l}" not in listed]) for h, lines in sections]
    body = "\n\n".join(
        f"{heading}:\n\n" + "\n".join(f"- {line}" for line in lines)
        for heading, lines in sections if lines)
    if existing:
        gh_api(f"repos/{{owner}}/{{repo}}/issues/{existing['number']}/comments", "-f", f"body={body}")
        print(existing["html_url"])
        return 0
    filed = gh_api("repos/{owner}/{repo}/issues", "-f", f"title={title}", "-f", f"body={body}",
                   "-q", ".html_url")
    if filed.returncode:
        return 2
    print(filed.stdout.rstrip("\n"))
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
