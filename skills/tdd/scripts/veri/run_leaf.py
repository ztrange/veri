"""run-leaf.sh's logic, run in-process."""
import os
import subprocess
import sys
import tempfile

from extract_result import extract

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


def complain(name, error):
    print(f"run-leaf.sh: {name}: {error.strerror}", file=sys.stderr)


def main(argv):
    if not argv or not argv[0]:
        print(USAGE, file=sys.stderr)
        return 2
    try:
        prompt = read_prompt(argv[0])
    except OSError as error:
        complain(argv[0], error)
        return 1
    stream_fd, stream_path = tempfile.mkstemp(dir=os.environ.get("TMPDIR") or "/tmp")
    command = leaf_argv(prompt, argv[1:])
    stream = b""
    try:
        leaf = subprocess.Popen(command, stdout=subprocess.PIPE)
    except OSError as error:
        complain(command[0], error)
        status = 2
    else:
        with leaf:
            while chunk := os.read(leaf.stdout.fileno(), 65536):
                os.write(1, chunk)
                os.write(stream_fd, chunk)
                stream += chunk
        status = leaf.returncode
    os.close(stream_fd)
    os.remove(stream_path)
    os.write(1, b"\n")
    text = stream.decode(sys.__stdin__.encoding, sys.__stdin__.errors)
    os.write(1, extract(text).encode(sys.__stdout__.encoding, sys.__stdout__.errors))
    return status if 0 <= status <= 3 else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
