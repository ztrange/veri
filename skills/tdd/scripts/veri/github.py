"""veri's GitHub access: lib/github.sh's GraphQL→REST fallback, run through gh."""
import re
import subprocess


class NoAnswer(Exception):
    def __init__(self, answer):
        self.answer = answer


def gh_rest_list(path, empty=r"^\[\]$"):
    answer = ""
    sep = "&" if "?" in path else "?"
    page = 1
    while True:
        run = subprocess.run(["gh", "api", "%s%spage=%d" % (path, sep, page)],
                             stdout=subprocess.PIPE, text=True)
        if run.returncode != 0:
            raise NoAnswer(answer)
        body = run.stdout.rstrip("\n")
        if re.search(empty, body):
            return answer
        answer += body
        page += 1


def gh_list(path, *args):
    run = subprocess.run(["gh", *args], stdout=subprocess.PIPE,
                         stderr=subprocess.DEVNULL, text=True)
    if run.returncode != 0:
        return gh_rest_list(path)
    return run.stdout
