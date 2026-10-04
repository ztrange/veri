"""veri's GitHub access: lib/github.sh's GraphQL→REST fallback, run through gh."""
import re
import subprocess


class NoAnswer(Exception):
    pass


def gh_rest_list(path, empty=r"^\[\]$"):
    answer = ""
    sep = "&" if "?" in path else "?"
    page = 1
    while True:
        run = subprocess.run(["gh", "api", "%s%spage=%d" % (path, sep, page)],
                             stdout=subprocess.PIPE, text=True)
        if run.returncode != 0:
            raise NoAnswer
        body = run.stdout.rstrip("\n")
        if re.search(empty, body):
            return answer
        answer += body
        page += 1
