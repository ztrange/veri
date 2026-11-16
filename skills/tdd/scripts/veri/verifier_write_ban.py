"""The PreToolUse hook command a verifier leaf's --settings carry (verify.LEAF_ARGS): the verifier's write ban.

The hook is matched on `Write|Edit|MultiEdit|NotebookEdit`; this command reads the tool call Claude Code hands it as
JSON on stdin and blocks a call of one of those tools (exit 2, the hook protocol's block, with one stderr line the
leaf is shown), letting any other tool's call through (exit 0). A call it cannot read escapes as an exception, which
entry.run turns into exit 2 too, so the ban fails closed.

Interface:
  BANNED       the tools whose calls are blocked
  main(argv)   reads the call on stdin; 2 for a banned tool, else 0
"""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import json
import sys

from entry import write

BANNED = ("Write", "Edit", "MultiEdit", "NotebookEdit")


def main(argv):
    tool = json.loads(sys.stdin.read())["tool_name"]
    if tool in BANNED:
        write(sys.stderr, "verifier-write-ban: the verifier may not modify files (%s)" % tool)
        return 2
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
