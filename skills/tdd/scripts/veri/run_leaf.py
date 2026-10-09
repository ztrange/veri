"""run-leaf.sh's logic, run in-process."""
import contextlib
import os
import shutil
import signal
import subprocess
import sys
import tempfile

from extract_result import extract
from session_env import strip_session_env

USAGE = "usage: run-leaf.sh <prompt-file|-> [claude args...]"


def leaf_argv(binary, model, prompt, extra):
    argv = [binary or "claude", "-p", prompt,
            "--output-format", "stream-json", "--verbose"]
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
    for name in os.environ.pop("VERI_SHIM_DEFAULT_SIGNALS", "").split():
        signal.signal(getattr(signal, "SIG" + name), signal.SIG_DFL)
    try:
        prompt = read_prompt(argv[0])
    except OSError as error:
        complain(argv[0], error)
        return 2
    with contextlib.suppress(ValueError):
        signal.signal(signal.SIGTERM, lambda *_: sys.exit(2))
    tmpdir = os.environ.get("TMPDIR") or "/tmp"
    stream_fd, stream_path = tempfile.mkstemp(dir=tmpdir)
    git_fd, git_path = tempfile.mkstemp(dir=tmpdir)
    os.close(git_fd)
    gitconfig = os.path.join(os.environ["HOME"], ".gitconfig")
    try:
        try:
            if os.path.isfile(gitconfig):
                shutil.copyfile(gitconfig, git_path)
        except OSError as error:
            complain(git_path, error)
            return 2
        env = dict(os.environ)
        binary = env.get("CLAUDE_BIN")
        model = env.get("VERI_LEAF_MODEL", "")
        strip_session_env(env)
        env["GIT_CONFIG_GLOBAL"] = git_path
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        if env.get("VERI_SHIM_SET_COERCE") == "1":
            del env["VERI_SHIM_SET_COERCE"]
            env.pop("PYTHONCOERCECLOCALE", None)
        command = leaf_argv(binary, model, prompt, argv[1:])
        try:
            leaf = subprocess.Popen(command, stdout=subprocess.PIPE, env=env,
                                    restore_signals=False)
        except OSError as error:
            complain(command[0], error)
            status = 2
        else:
            with leaf:
                while chunk := os.read(leaf.stdout.fileno(), 65536):
                    os.write(1, chunk)
                    os.write(stream_fd, chunk)
            status = leaf.returncode
        os.write(1, b"\n")
        try:
            with open(stream_path, "rb") as f:
                stream = f.read()
        except OSError as error:
            complain(stream_path, error)
            return 2
    finally:
        os.close(stream_fd)
        for path in (stream_path, git_path):
            with contextlib.suppress(OSError):
                os.remove(path)
    text = stream.decode(sys.__stdin__.encoding, sys.__stdin__.errors)
    os.write(1, extract(text).encode(sys.__stdout__.encoding, sys.__stdout__.errors))
    return status if 0 <= status <= 3 else 2

if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
