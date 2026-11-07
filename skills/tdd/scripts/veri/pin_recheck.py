"""pin-recheck.sh's re-run of the recorded pin mutations a range touches."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import glob
import re
import subprocess
import sys
from pathlib import Path

from ledger import ledger_path


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


def tick_commit(ledger):
    number = Path(ledger).name.removeprefix("issue-").removesuffix("-mutations.md")
    return subprocess.run(["git", "log", "-1", "--format=%H", "--", ledger_path(".", number)],
                          capture_output=True, text=True).stdout.strip()


def replay_before(pin, ledger):
    green = tick_commit(ledger) or pin.get("green")
    names = subprocess.run(["git", "diff", "--name-only", pin["before"], *([green] if green else [])],
                           capture_output=True, text=True,
                           check=True).stdout.split()
    names = [n for n in names if n != pin["keep"] and not n.startswith(".tdd/")]
    if not names and green:
        sys.stderr.write(f"empty replay range: before {pin['before']} green {green}\n")
        return None
    saved = {n: Path(n).read_bytes() for n in names if Path(n).exists()}
    modes = {n: Path(n).stat().st_mode for n in saved}
    try:
        for n in names:
            shown = subprocess.run(["git", "show", f"{pin['before']}:{n}"], capture_output=True)
            if shown.returncode == 0:
                Path(n).write_bytes(shown.stdout)
            else:
                Path(n).unlink(missing_ok=True)
        ran = run_captured(current_wrapper(pin["command"]))
    finally:
        for n in names:
            if n in saved:
                Path(n).write_bytes(saved[n])
                Path(n).chmod(modes[n])
            else:
                Path(n).unlink(missing_ok=True)
    return ran.returncode


def recheck(argv):
    if not argv:
        sys.stderr.write("usage: pin-recheck.sh <base-sha>\n")
        return 2
    touched = set(subprocess.run(["git", "diff", "--name-only", f"{argv[0]}..HEAD"], capture_output=True, text=True,
                                 check=True).stdout.split())
    found = [(f, r) for f in sorted(glob.glob(".tdd/issue-*-mutations.md")) for r in records(Path(f).read_text())]
    for f, r in found:
        if "before" not in r and "file" not in r:
            sys.stderr.write(f"unparseable mutation record in {f}: {r}\n")
            return 2
    pins = [(f, r) for f, r in found if r.get("keep", r.get("file")) in touched]
    if not pins:
        return 3
    deleted = set(subprocess.run(["git", "diff", "--name-only", "--diff-filter=D", f"{argv[0]}..HEAD"],
                                 capture_output=True, text=True, check=True).stdout.split())
    status = 0
    retired = 0
    for ledger, pin in pins:
        named = re.findall(r"TESTS=(\S+)", pin["command"])
        gone = [n for n in named if n.split("::")[0] in deleted]
        named = [n for n in named if n.split("::")[0] not in deleted]
        mutated_file = pin.get("file", pin.get("keep"))
        if gone and not named:
            for n in gone:
                sys.stdout.write(f"retired: {ledger} {mutated_file} {n}\n")
            retired += 1
            continue
        for n in gone:
            pin["command"] = re.sub(r"TESTS=" + re.escape(n) + r"(?=\s|$)", "", pin["command"])
        for n in named:
            if not Path(n.split("::")[0]).exists():
                sys.stderr.write(f"named test missing at HEAD: {n} (pin file {ledger})\n")
                return 2
        if "before" in pin:
            replayed = replay_before(pin, ledger)
            if replayed is None:
                return 2
            if replayed == 0:
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
        if base.returncode == 127 or "no makefile found" in base.stderr.lower():
            sys.stderr.write(f"command not found: {pin['command']} (pin file {ledger})\n")
            return 2
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
    if retired == len(pins):
        return 3
    return status


RECEIPT = Path(".tdd/pin-recheck-ok")


def main(argv):
    RECEIPT.unlink(missing_ok=True)
    status = recheck(argv)
    if status in (0, 3):
        head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
        RECEIPT.write_text(head + "\n")
    return status


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
