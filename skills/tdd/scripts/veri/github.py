"""veri's GitHub access: lib/github.sh's GraphQL→REST fallback, run through gh."""
import subprocess


def gh_rest_list(path):
    answer = ""
    sep = "&" if "?" in path else "?"
    page = 1
    while True:
        body = subprocess.run(["gh", "api", "%s%spage=%d" % (path, sep, page)],
                              stdout=subprocess.PIPE, text=True).stdout.rstrip("\n")
        if body == "[]":
            return answer
        answer += body
        page += 1
