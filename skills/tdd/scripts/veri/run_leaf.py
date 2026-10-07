"""run-leaf.sh's logic, run in-process."""
import os
import subprocess
import sys

USAGE = "usage: run-leaf.sh <prompt-file|-> [claude args...]"


def leaf_argv(prompt, extra):
    argv = [os.environ.get("CLAUDE_BIN") or "claude", "-p", prompt,
            "--output-format", "stream-json", "--verbose"]
    model = os.environ.get("VERI_LEAF_MODEL", "")
    if model:
        argv += ["--model", model]
    return argv + extra


def read_prompt(path):
    if path == "-":
        data = sys.stdin.buffer.read()
    else:
        with open(path, "rb") as f:
            data = f.read()
    return os.fsdecode(data.replace(b"\0", b"").rstrip(b"\n"))


def main(argv):
    if not argv or not argv[0]:
        print(USAGE, file=sys.stderr)
        return 2
    try:
        prompt = read_prompt(argv[0])
    except OSError as error:
        print(f"run-leaf.sh: {argv[0]}: {error.strerror}", file=sys.stderr)
        return 1
    with subprocess.Popen(leaf_argv(prompt, argv[1:]), stdout=subprocess.PIPE) as leaf:
        leaf.stdout.read()
    return leaf.returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
