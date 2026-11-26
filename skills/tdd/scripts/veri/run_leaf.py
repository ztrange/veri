"""run-leaf.sh's logic, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import contextlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile

import entry
import leaf_timeout
import paths
import redaction
import tunables
from context_limits import context_limits
from extract_result import extract
from session_env import strip_session_env

GUARD = os.path.join(paths.scripts_of(__file__), "leaf-guard")
DEFAULT_TOOLS = "Bash,Read,Edit,Write,Grep,Glob"
USAGE = "usage: run-leaf.sh <prompt-file|-> [claude args...]"
# The one allow-list of a leaf's environment (PRD 022.5): a name neither here, nor under a prefix here, nor set by
# launch_spec itself is dropped, so a credential no list names (GH_TOKEN, a cloud key) never reaches a leaf.
LEAF_ENV_NAMES = frozenset((
    "PATH", "HOME", "TMPDIR", "PWD", "USER", "LOGNAME", "LANG",
    "CLAUDE_BIN", "REVISE_BUDGET", "VERIFY_LEAF_ARGS", "PYTHONCOERCECLOCALE",
    "ANTHROPIC_API_KEY", "CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_BASE_URL", "CLAUDE_CONFIG_DIR",
    "HTTPS_PROXY", "HTTP_PROXY", "NO_PROXY", "NODE_EXTRA_CA_CERTS",
    # supervise.sh sets it for the leaf, so a full suite the leaf runs marks its wait on the full-run lock (#2380).
    "PYTEST_LEG_LOCK_WAIT_MARKER",
    # The reconcile leaf pushes (prompts/develop-reconcile.md); over an ssh remote its key is held by an agent. It
    # names a socket, not a secret, and a leaf can already reach gh's stored login under HOME, so it widens nothing.
    # GH_TOKEN, GITHUB_TOKEN and GIT_SSH_COMMAND stay out: a push that needs one names it in VERI_LEAF_ENV.
    "SSH_AUTH_SOCK",
))
LEAF_ENV_PREFIXES = ("VERI_", "LC_")
VARIABLE_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
SET_NAMES = frozenset(("GIT_CONFIG_GLOBAL", "PYTHONDONTWRITEBYTECODE", "FORCE_PROMPT_CACHING_5M",
                       "CLAUDE_CODE_DISABLE_BACKGROUND_TASKS", "SHELL", "CLAUDE_CODE_SHELL",
                       "BASH_DEFAULT_TIMEOUT_MS", "BASH_MAX_TIMEOUT_MS"))


def leaf_passes(name, added=()):
    """Whether the allow-list, the names `added` (VERI_LEAF_ENV's) or launch_spec's own names let `name` into a
    leaf's environment."""
    return name in LEAF_ENV_NAMES or name in SET_NAMES or name in added or name.startswith(LEAF_ENV_PREFIXES)


def claude_mds(directory):
    """The project memory files Claude Code reads in `directory`: `CLAUDE.md`, `CLAUDE.local.md` and
    `.claude/CLAUDE.md`."""
    return [os.path.join(directory, "CLAUDE.md"), os.path.join(directory, "CLAUDE.local.md"),
            os.path.join(directory, ".claude", "CLAUDE.md")]


def above_top_level(toplevel):
    """The project memory files (`claude_mds`) of every directory above `toplevel` up to the root; none for None."""
    if toplevel is None:
        return []
    above = []
    directory = toplevel
    while os.path.dirname(directory) != directory:
        directory = os.path.dirname(directory)
        above += claude_mds(directory)
    return above


def top_level(directory):
    """The top level of the working tree holding `directory`, as `git rev-parse --show-toplevel` names it for a main
    tree or a linked worktree: the nearest directory at or above it holding a `.git` entry. None outside one. Read
    from the file system, so no process is started per leaf."""
    while True:
        if os.path.lexists(os.path.join(directory, ".git")):
            return directory
        parent = os.path.dirname(directory)
        if parent == directory:
            return None
        directory = parent


class UnmergeableSettings(Exception):
    """A caller's `--settings` value that is not a JSON object (a file path, say): `value`."""

    def __init__(self, value):
        super().__init__(value)
        self.value = value


def callers_settings(extra):
    """`(settings, rest)`: every JSON object the caller's arguments pass as `--settings <json>`, merged in order
    (a later key wins), since the CLI keeps only one `--settings` and the leaf already passes its own; and the
    arguments without those pairs. Raises UnmergeableSettings for a `--settings` value that is not a JSON object."""
    settings, rest, words = {}, [], list(extra)
    while words:
        word = words.pop(0)
        if word != "--settings" or not words:
            rest.append(word)
            continue
        value = words.pop(0)
        try:
            given = json.loads(value)
        except ValueError:
            given = None
        if not isinstance(given, dict):
            raise UnmergeableSettings(value)
        settings.update(given)
    return settings, rest


def leaf_argv(binary, model, extra, excludes=()):
    settings, extra = callers_settings(extra)
    argv = [binary, "-p",
            "--output-format", "stream-json", "--verbose"] + context_limits(excludes, settings)
    tools = tunables.read("VERI_LEAF_TOOLS", DEFAULT_TOOLS)
    if tools is not None and "--tools" not in extra:
        argv += ["--tools", tools]
    if model and "--model" not in extra:
        argv += ["--model", model]
    return argv + extra


def launch_spec(environ, git_path, shell, seconds, binary, model, extra, coerce_marker="", toplevel=None,
                own_dir=None):
    """What a leaf is launched with, decided and not started: `(argv, env)`, a pure function of its inputs.

    `env` holds only the names of `environ` the allow-list or its `VERI_LEAF_ENV` passes (`leaf_passes`), stripped
    of the conductor's session variables, with the leaf's private git config, bytecode, caching, background-task, shell and Bash-tool timeout settings and the guard first on
    PATH; the shim's locale marker, when `coerce_marker` (its value, read by the caller) is "1", is removed together with
    PYTHONCOERCECLOCALE. `toplevel` is the leaf's working tree's top level (None: outside one), above which no
    `CLAUDE.md` is loaded; `own_dir`, when given, is a directory whose project memory files are not
    loaded either (the grader's). `seconds` is the hard cap as text: raises ValueError when it is not a whole number;
    UnmergeableSettings for a caller's `--settings` that is not a JSON object (`callers_settings`)."""
    added = environ.get("VERI_LEAF_ENV", tunables.default("VERI_LEAF_ENV")).split()
    env = {name: value for name, value in environ.items() if leaf_passes(name, added)}
    strip_session_env(env)
    env["GIT_CONFIG_GLOBAL"] = git_path
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["FORCE_PROMPT_CACHING_5M"] = "1"
    env["CLAUDE_CODE_DISABLE_BACKGROUND_TASKS"] = "1"
    env["SHELL"] = env["CLAUDE_CODE_SHELL"] = shell
    cap_ms = str(int(seconds) * 1000)
    env.setdefault("BASH_DEFAULT_TIMEOUT_MS", cap_ms)
    env.setdefault("BASH_MAX_TIMEOUT_MS", cap_ms)
    env["PATH"] = GUARD + os.pathsep + env.get("PATH", "")
    if coerce_marker == "1":
        env.pop("VERI_SHIM_SET_COERCE", None)
        env.pop("PYTHONCOERCECLOCALE", None)
    own = [] if own_dir is None else claude_mds(own_dir)
    return leaf_argv(binary, model, extra, own + above_top_level(toplevel)), env


def read_prompt(path):
    if path == "-":
        data = sys.stdin.buffer.read()
    else:
        with open(path, "rb") as f:
            data = f.read()
    return os.fsdecode(data.replace(b"\0", b"").rstrip(b"\n"))


def effective_timeout():
    """The hard cap in seconds as text: VERI_TIMEOUT, else the run's timeout pin (relative to the
    current directory), else the tunable's default. Raises leaf_timeout.Malformed for a bad pin."""
    seconds = tunables.read("VERI_TIMEOUT")
    issue = tunables.read("VERI_ISSUE")
    if not seconds and issue:
        with contextlib.suppress(OSError):
            seconds = leaf_timeout.settled("", issue)
    return seconds or tunables.default("VERI_TIMEOUT")


def complain(name, error):
    print(f"run-leaf.sh: {name}: {error.strerror}", file=sys.stderr)


def main(argv):
    if not argv or not argv[0]:
        print(USAGE, file=sys.stderr)
        return 2
    for name in tunables.pop("VERI_SHIM_DEFAULT_SIGNALS").split():
        signal.signal(getattr(signal, "SIG" + name), signal.SIG_DFL)
    try:
        prompt = read_prompt(argv[0])
    except OSError as error:
        complain(argv[0], error)
        return 2
    if not prompt:
        print(f"run-leaf.sh: {argv[0]}: the prompt is empty", file=sys.stderr)
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
        binary = tunables.claude_bin()
        model = tunables.read("VERI_LEAF_MODEL")
        shell = shutil.which("bash")
        coerce_marker = tunables.read("VERI_SHIM_SET_COERCE")
        own_dir = os.getcwd() if tunables.read("VERI_LEAF_SKIP_PROJECT_CLAUDE_MD") == "1" else None
        try:
            seconds = effective_timeout()
        except leaf_timeout.Malformed as bad:
            print(f"run-leaf.sh: {bad.path} must hold a whole number of seconds >= 1: '{bad.text}'",
                  file=sys.stderr)
            return 2
        try:
            command, env = launch_spec(tunables.environment(), git_path, shell, seconds, binary, model, argv[1:],
                                      coerce_marker, top_level(os.getcwd()), own_dir)
        except UnmergeableSettings as bad:
            print(f"run-leaf.sh: --settings {bad.value!r} is not a JSON object, so it cannot be merged into the"
                  " leaf's one --settings", file=sys.stderr)
            return 2
        except ValueError:
            print(f"run-leaf.sh: VERI_TIMEOUT is not a whole number: {seconds!r}",
                  file=sys.stderr)
            return 2
        malformed = [item for item in tunables.get("VERI_LEAF_ENV").split() if not VARIABLE_NAME.fullmatch(item)]
        if malformed:
            print("run-leaf.sh: VERI_LEAF_ENV items that are not variable names, so they add nothing: "
                  + " ".join(malformed), file=sys.stderr)
        for name in sorted(set(tunables.get("VERI_LEAF_ENV").split()) & set(redaction.listed_names())):
            print(f"run-leaf.sh: VERI_LEAF_ENV passes {name}, which VERI_REDACT_VARS names as a credential, to the"
                  " leaf", file=sys.stderr)
        try:
            leaf = subprocess.Popen(command, stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE, env=env,
                                    restore_signals=False)
        except OSError as error:
            complain(command[0], error)
            status = 2
        else:
            with leaf:
                feed = getattr(leaf, "stdin", None)
                if feed is not None:
                    previous = signal.signal(signal.SIGPIPE, signal.SIG_IGN)
                    try:
                        with contextlib.suppress(BrokenPipeError):
                            feed.write(os.fsencode(prompt))
                            feed.close()
                    finally:
                        signal.signal(signal.SIGPIPE, previous)
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
    return entry.to_contract(status)

if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
