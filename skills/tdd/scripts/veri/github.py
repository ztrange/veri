"""veri's GitHub access: lib/github.sh's GraphQL→REST fallback, run through gh."""
import subprocess


def gh_rest_list(path):
    answer = ""
    page = 1
    while True:
        body = subprocess.run(["gh", "api", "%s?page=%d" % (path, page)],
                              stdout=subprocess.PIPE, text=True).stdout.rstrip("\n")
        if body == "[]":
            return answer
        answer += body
        page += 1
