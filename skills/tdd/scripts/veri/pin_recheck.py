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


def control_run(path, original, command):
    path.write_bytes(b"\x00 control run: no runner can load this\n")
    control = run_captured(command)
    path.write_bytes(original)
    return control


def output_lines(run):
    return set(run.stdout.splitlines()) | set(run.stderr.splitlines())


def is_go_test_failure(run):
    lines = output_lines(run)
    return any(line.startswith("--- FAIL: ") for line in lines)


def write_tail(run):
    sys.stderr.write("".join(line + "\n" for line in (run.stdout.splitlines() + run.stderr.splitlines())[-40:]))


def replay_before(pin):
    names = subprocess.run(["git", "diff", "--name-only", pin["before"]], capture_output=True, text=True,
                           check=True).stdout.split()
    names = [n for n in names if n != pin["keep"] and not n.startswith(".tdd/")]
    saved = {n: Path(n).read_bytes() for n in names}
    for n in names:
        Path(n).write_bytes(subprocess.run(["git", "show", f"{pin['before']}:{n}"], capture_output=True,
                                           check=True).stdout)
    ran = run_captured(current_wrapper(pin["command"]))
    for n, data in saved.items():
        Path(n).write_bytes(data)
    return ran.returncode


def main(argv):
    if not argv:
        sys.stderr.write("usage: pin-recheck.sh <base-sha>\n")
        return 2
    touched = set(subprocess.run(["git", "diff", "--name-only", f"{argv[0]}..HEAD"], capture_output=True, text=True,
                                 check=True).stdout.split())
    pins = [r for f in sorted(glob.glob(".tdd/issue-*-mutations.md")) for r in records(Path(f).read_text())
            if "before" in r or r["file"] in touched]
    if not pins:
        return 3
    status = 0
    for pin in pins:
        if "before" in pin:
            if replay_before(pin) == 0:
                sys.stderr.write(f"pin stayed green on the before-state: {pin['keep']}\n")
                status = 1
            continue
        pin["command"] = current_wrapper(pin["command"])
        path = Path(pin["file"])
        original = path.read_bytes()
        if pin["old"].encode() not in original:
            sys.stdout.write(f"needs a look: {pin['file']}\n")
            continue
        base = run_captured(pin["command"])
        if base.returncode != 0:
            sys.stdout.write(f"needs a look: {pin['file']}\n")
            write_tail(base)
            continue
        path.write_bytes(original.replace(pin["old"].encode(), pin["new"].encode()))
        mutated = run_captured(pin["command"])
        path.write_bytes(original)
        green = mutated.returncode == 0
        base_lines = output_lines(base)
        if not green and not base_lines & output_lines(mutated) and not is_go_test_failure(mutated):
            sys.stdout.write(f"needs a look: {pin['file']} (mutation did not build)\n")
            write_tail(mutated)
            status = 1
            continue
        if green:
            control = control_run(path, original, pin["command"])
            if control.returncode == 0:
                sys.stdout.write(f"needs a look: {pin['file']}\n")
                continue
            sys.stderr.write(f"pin stayed green under its mutation: {pin['file']}\n")
            status = 1
    return status


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
