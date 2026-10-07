"""run-suite.sh's count-line check, run in-process."""
import fnmatch
import os
import re
import shutil
import subprocess
import sys

SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read_guard(path):
    guard = {}
    with open(path) as f:
        for line in f:
            match = re.match(r"^(COUNT_LINE|COUNTLESS)='(.*)'$", line.rstrip("\n"))
            if match:
                guard[match.group(1)] = match.group(2)
    return guard


def render_printf(fmt, arg):
    escapes = {"n": "\n", "t": "\t", "r": "\r", "a": "\a", "\\": "\\"}
    args = [arg]
    out = []
    i = 0
    while i < len(fmt):
        c = fmt[i]
        nxt = fmt[i + 1] if i + 1 < len(fmt) else ""
        if c == "%" and nxt == "%":
            out.append("%")
            i += 2
        elif c == "%" and nxt == "s":
            out.append(args.pop(0) if args else "")
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


def venv_python():
    venv = os.environ.get("VERI_VENV") or os.path.join(os.environ.get("HOME", ""), ".veri-tools", "venv")
    py = os.path.join(venv, "bin", "python3")
    if os.access(py, os.X_OK):
        return py
    return shutil.which("python3") or ""


def run_pytest(suite, env):
    py = venv_python()
    version = subprocess.run([py, "-m", "pytest", "--version"], stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL, env=env)
    if version.returncode != 0:
        sys.stderr.write("run-suite.sh: pytest cannot be imported by %s; run make install-dev\n" % py)
        return 2
    code = subprocess.run([py, "-m", "pytest", suite], stdin=subprocess.DEVNULL, env=env).returncode
    return code if 0 <= code <= 3 else 2


def main(argv):
    if not argv:
        sys.stderr.write("usage: run-suite.sh <suite>\n")
        return 2
    suite = argv[0]
    env = dict(os.environ)
    n = int(env.get("GIT_CONFIG_COUNT") or 0)
    env["GIT_CONFIG_KEY_%d" % n] = "maintenance.auto"
    env["GIT_CONFIG_VALUE_%d" % n] = "false"
    env["GIT_CONFIG_COUNT"] = str(n + 1)
    if fnmatch.fnmatchcase(suite, "*/tests/py/test_*.py"):
        return run_pytest(suite, env)
    guard_path = os.path.join(SCRIPTS, "lib", "count-line-guard.sh")
    try:
        guard = read_guard(guard_path)
    except OSError:
        guard = {}
    if not guard.get("COUNT_LINE") or not guard.get("COUNTLESS"):
        sys.stderr.write("run-suite.sh: could not read the count-line guard from %s\n" % guard_path)
        return 2
    out = bytearray()
    with subprocess.Popen([suite], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, env=env) as proc:
        for chunk in iter(lambda: proc.stdout.read1(65536), b""):
            sys.stdout.buffer.write(chunk)
            sys.stdout.buffer.flush()
            out += chunk
    text = out.decode(errors="surrogateescape")
    lines = text.split("\n")
    last_line = lines[-2] if text.endswith("\n") else lines[-1]
    if re.search(guard["COUNT_LINE"], last_line):
        return proc.returncode
    name = os.path.basename(suite)
    sys.stdout.write(render_printf(guard["COUNTLESS"], name))
    if text.strip():
        sys.stdout.write("%s: its last line was: %s\n" % (name, last_line))
    else:
        sys.stdout.write("%s: its output was empty\n" % name)
    sys.stdout.flush()
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
