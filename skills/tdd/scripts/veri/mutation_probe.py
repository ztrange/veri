"""mutation-probe.sh's computations, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import re
import shlex
import signal
import subprocess
import sys
from pathlib import Path

import tunables

USAGE = "usage: mutation-probe.sh <file> <old> <new> -- <command…>"
BEFORE_USAGE = "usage: mutation-probe.sh --before <sha> --keep <test-path> -- <command…>"


def append_record(fields):
    record = tunables.read("VERI_MUTATION_RECORD")
    if record:
        with open(record, "a") as f:
            for name, value in fields:
                f.write(f"{name} {len(value)}\n{value}\n")
            f.write("\n")


def run_keeping_journal(run):
    journal = Path(".tdd/events.jsonl")
    before = journal.read_bytes() if journal.exists() else None
    ran = run()
    if before is not None and not journal.read_bytes().startswith(before):
        journal.write_bytes(before)
    return ran


def run_with(contents, command):
    saved = {path: path.read_bytes() if path.exists() else None for path in contents}
    try:
        for path, content in contents.items():
            if content is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(content)
        return run_keeping_journal(lambda: subprocess.run(command)).returncode
    finally:
        for path, content in saved.items():
            if content is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(content)


def before_state(argv):
    if len(argv) < 6 or argv[2] != "--keep" or argv[4] != "--":
        sys.stderr.write(BEFORE_USAGE + "\n")
        return 2
    sha, keep, command = argv[1], argv[3], argv[5:]
    if not re.fullmatch(r"[0-9a-f]{7,40}", sha):
        sys.stderr.write(f"mutation-probe.sh: {sha} is not 7-40 lowercase hex\n")
        return 2
    if subprocess.run(["git", "rev-parse", "--verify", "--quiet", f"{sha}^{{commit}}"], capture_output=True).returncode:
        sys.stderr.write(f"mutation-probe.sh: {sha} does not resolve to a commit\n")
        return 2
    names = subprocess.run(["git", "diff", "--no-renames", "--name-only", "-z", sha], capture_output=True).stdout
    untracked = subprocess.run(["git", "ls-files", "--others", "--exclude-standard", "-z"], capture_output=True).stdout
    restored = {}
    for name in names.decode().split("\0") + untracked.decode().split("\0"):
        if name and name != keep and not name.startswith(".tdd/"):
            old = subprocess.run(["git", "show", f"{sha}:{name}"], capture_output=True)
            restored[Path(name)] = None if old.returncode else old.stdout
    if not restored:
        sys.stderr.write(f"mutation-probe.sh: no file differs from {sha}\n")
        return 2
    returncode = run_with(restored, command)
    if returncode == 0:
        return 1
    fields = [("before", sha), ("keep", keep), ("command", shlex.join(timed_stripped(command)))]
    if not names_issue_ledger(tunables.read("VERI_MUTATION_RECORD")):
        green = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        fields.append(("green", green))
    append_record(fields)
    return 0


def timed_stripped(command):
    if Path(command[0]).resolve() == Path(__file__).resolve().parent.parent / "timed-test-run.sh":
        return command[3:]
    return command


def names_issue_ledger(record):
    return re.fullmatch(r"issue-\d+-mutations\.md", Path(record).name) is not None


def main(argv):
    if argv and argv[0] == "--before":
        return before_state(argv)
    if len(argv) < 5 or argv[3] != "--":
        sys.stderr.write(USAGE + "\n")
        return 2
    domain = tunables.read("VERI_MUTATION_ADDRESS_DOMAIN")
    if domain:
        for address in re.findall(r"[^\s@]+@[^\s@]+", argv[1] + " " + argv[2]):
            if address.rsplit("@", 1)[1] != domain:
                sys.stderr.write(f"mutation-probe.sh: {address} is outside the allowed address domain {domain}\n")
                return 2
    path = Path(argv[0])
    saved = path.read_bytes()
    mutated = saved.replace(argv[1].encode(), argv[2].encode())
    if mutated == saved:
        sys.stderr.write("mutation-probe.sh: file not mutated\n")
        return 2
    signal.signal(signal.SIGTERM, lambda signum, frame: sys.exit(128 + signum))
    returncode = run_with({path: mutated}, argv[4:])
    if returncode == 0:
        sys.stderr.write("mutation-probe.sh: suite stayed green under the mutation\n")
        return 1
    text = saved.decode()
    start = text.index(argv[1])
    context = text[text.rfind("\n", 0, start) + 1:].split("\n", 1)[0]
    append_record((("file", argv[0]), ("old", argv[1]), ("new", argv[2]), ("context", context), ("command", shlex.join(timed_stripped(argv[4:])))))
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
