"""pin-recheck.sh's re-run of the recorded pin mutations a range touches."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import glob
import subprocess
import sys
from pathlib import Path


def records(text):
    out, i = [], 0
    while i < len(text):
        if text[i] == "\n":
            i += 1
            continue
        record = {}
        while i < len(text) and text[i] != "\n":
            end = text.index("\n", i)
            name, size = text[i:end].split()
            record[name] = text[end + 1:end + 1 + int(size)]
            i = end + 2 + int(size)
        out.append(record)
    return out


def current_wrapper(command):
    head, _, rest = command.partition(" ")
    if head.endswith("/timed-test-run.sh") and not Path(head).exists():
        return f"{Path(__file__).resolve().parent.parent / 'timed-test-run.sh'} {rest}"
    return command


def run_captured(command):
    return subprocess.run(command, shell=True, capture_output=True, text=True)


def output_lines(run):
    return set(run.stdout.splitlines()) | set(run.stderr.splitlines())


def main(argv):
    if not argv:
        sys.stderr.write("usage: pin-recheck.sh <base-sha>\n")
        return 2
    touched = set(subprocess.run(["git", "diff", "--name-only", f"{argv[0]}..HEAD"], capture_output=True, text=True,
                                 check=True).stdout.split())
    pins = [r for f in sorted(glob.glob(".tdd/issue-*-mutations.md")) for r in records(Path(f).read_text())
            if r["file"] in touched]
    if not pins:
        return 3
    status = 0
    for pin in pins:
        pin["command"] = current_wrapper(pin["command"])
        path = Path(pin["file"])
        original = path.read_bytes()
        if pin["old"].encode() not in original:
            sys.stdout.write(f"needs a look: {pin['file']}\n")
            continue
        base = run_captured(pin["command"])
        if base.returncode != 0:
            sys.stdout.write(f"needs a look: {pin['file']}\n")
            continue
        path.write_bytes(original.replace(pin["old"].encode(), pin["new"].encode()))
        mutated = run_captured(pin["command"])
        path.write_bytes(original)
        green = mutated.returncode == 0
        base_lines = output_lines(base)
        if not green and not base_lines & output_lines(mutated):
            sys.stdout.write(f"needs a look: {pin['file']} (mutation did not build)\n")
            status = 1
            continue
        if green:
            sys.stderr.write(f"pin stayed green under its mutation: {pin['file']}\n")
            status = 1
    return status


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
