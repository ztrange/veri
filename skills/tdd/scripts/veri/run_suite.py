"""run-suite.sh's count-line check, run in-process."""
import fnmatch
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile

import tunables

OFFLINE_PROXY = "http://127.0.0.1:1"
SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read_guard(path):
    guard = {}
    try:
        with open(path) as f:
            for line in f:
                match = re.match(r"^(COUNT_LINE|COUNTLESS)='(.*)'$", line.rstrip("\n"))
                if match:
                    guard[match.group(1)] = match.group(2)
    except OSError:
        return {}
    return guard


def render_printf(fmt, arg):
    escapes = {"n": "\n", "t": "\t", "r": "\r", "a": "\a", "\\": "\\"}
    out = []
    i = 0
    while i < len(fmt):
        c = fmt[i]
        nxt = fmt[i + 1] if i + 1 < len(fmt) else ""
        if c == "%" and nxt == "%":
            out.append("%")
            i += 2
        elif c == "%" and nxt == "s":
            out.append(arg)
            arg = ""
            i += 2
        elif c == "%" and nxt == "d":
            out.append("0")
            i += 2
        elif c == "\\" and (octal := re.match(r"[0-7]{1,3}", fmt[i + 1:])):
            digits = octal.group(0)
            out.append(chr(int(digits, 8)))
            i += 1 + len(digits)
        elif c == "\\" and nxt in escapes:
            out.append(escapes[nxt])
            i += 2
        else:
            out.append(c)
            i += 1
    return "".join(out)


def report_countless(stream, fmt, name, text, last_line):
    stream.write(render_printf(fmt, name))
    if text.strip():
        stream.write("%s: its last line was: %s\n" % (name, last_line))
    else:
        stream.write("%s: its output was empty\n" % name)
    stream.flush()


def venv_python():
    py = os.path.join(tunables.venv_dir(), "bin", "python3")
    if os.access(py, os.X_OK):
        return py
    return shutil.which("python3") or ""


def run_pytest(suite, env):
    py = venv_python()
    try:
        importable = subprocess.run([py, "-m", "pytest", "--version"], stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL, env=env).returncode == 0
    except OSError:
        importable = False
    if not importable:
        sys.stderr.write("run-suite.sh: pytest cannot be imported by %s; run make install-dev\n" % py)
        return 2
    code = subprocess.run([py, "-m", "pytest", suite], stdin=subprocess.DEVNULL, env=env).returncode
    return code if 0 <= code <= 3 else 2


def main(argv):
    if not argv:
        sys.stderr.write("usage: run-suite.sh <suite>\n")
        return 2
    suite = argv[0]
    env = {k: v for k, v in tunables.environment().items() if k == "VERI_VENV" or not k.startswith(("VERI_", "CLAUDE_"))}
    n = int(env.get("GIT_CONFIG_COUNT") or 0)
    offline = (("maintenance.auto", "false"), ("http.proxy", OFFLINE_PROXY),
               ("protocol.allow", "never"), ("protocol.file.allow", "always"))
    for i, (key, value) in enumerate(offline):
        env["GIT_CONFIG_KEY_%d" % (n + i)] = key
        env["GIT_CONFIG_VALUE_%d" % (n + i)] = value
    env["GIT_CONFIG_COUNT"] = str(n + len(offline))
    env["LC_ALL"] = "C"
    env["HTTP_PROXY"] = env["HTTPS_PROXY"] = OFFLINE_PROXY
    env["NO_PROXY"] = "127.0.0.1,localhost"
    pytest_suite = fnmatch.fnmatchcase("/" + suite, "*/tests/py/test_*.py")
    guard = {}
    if not pytest_suite:
        guard_path = os.path.join(SCRIPTS, "lib", "count-line-guard.sh")
        guard = read_guard(guard_path)
        if not guard.get("COUNT_LINE") or not guard.get("COUNTLESS"):
            sys.stderr.write("run-suite.sh: could not read the count-line guard from %s\n" % guard_path)
            return 2
    name = os.path.basename(suite)

    def run(env):
        return run_pytest(suite, env) if pytest_suite else run_counted(suite, name, guard, env)

    if "OFFLINE_REACH_LOG" in env:
        return run(env)
    guards = [os.path.join(SCRIPTS, "tests", "offline")]
    if os.path.dirname(os.path.abspath(suite)) == os.path.join(SCRIPTS, "tests", "unit"):
        guards.insert(0, os.path.join(SCRIPTS, "tests", "unit-guard"))
    with tempfile.NamedTemporaryFile("r", prefix="veri-reach-") as reach_log:
        env["OFFLINE_REACH_LOG"] = reach_log.name
        if len(guards) > 1 or pytest_suite:
            env["UNIT_GUARD_LOG"] = reach_log.name
        env["PATH"] = os.pathsep.join(guards + [env.get("PATH", "")])
        code = run(env)
        reached = reach_log.read().splitlines()
    for line in reached:
        sys.stdout.write("%s: tried the network: %s\n" % (name, line))
    sys.stdout.flush()
    return 1 if reached else code


def run_counted(suite, name, guard, env):
    out = bytearray()
    try:
        proc = subprocess.Popen([suite], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, env=env)
    except OSError:
        report_countless(sys.stderr, guard["COUNTLESS"], name, "", "")
        return 1
    with proc:
        for chunk in iter(lambda: proc.stdout.read1(65536), b""):
            sys.stdout.buffer.write(chunk)
            sys.stdout.buffer.flush()
            out += chunk
    text = out.decode(errors="surrogateescape")
    lines = text.split("\n")
    last_line = lines[-2] if text.endswith("\n") else lines[-1]
    if re.search(guard["COUNT_LINE"], last_line):
        return 128 - proc.returncode if proc.returncode < 0 else proc.returncode
    report_countless(sys.stdout, guard["COUNTLESS"], name, text, last_line)
    return 1


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, lambda signum, frame: sys.exit(2))
    import entry
    entry.run(main, sys.argv[1:])
