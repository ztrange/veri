"""veri's GitHub access: lib/github.sh's GraphQL→REST fallback, run through gh."""
import re
import subprocess


def gh_rest_list(path, empty=r"^\[\]$"):
    answer = ""
    sep = "&" if "?" in path else "?"
    page = 1
    while True:
        body = subprocess.run(["gh", "api", "%s%spage=%d" % (path, sep, page)],
                              stdout=subprocess.PIPE, text=True).stdout.rstrip("\n")
        if re.search(empty, body):
            return answer
        answer += body
        page += 1
