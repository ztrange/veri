"""pin-recheck.sh's re-run of the recorded pin mutations a range touches."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import contextlib
import glob
import os
import shutil
import tempfile
import re
import subprocess
import sys
from pathlib import Path

import event
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


def is_pytest_failure(run):
    return any(line.startswith("FAILED ") for line in output_lines(run))


def needs_a_look(looks, file, reason):
    looks[(file, reason)] = looks.get((file, reason), 0) + 1


def flush_looks(looks):
    for (file, reason), n in looks.items():
        sys.stdout.write(f"needs a look: {file} ({reason})" + (f" ×{n}" if n > 1 else "") + "\n")


def write_tail(run):
    sys.stderr.write("".join(line + "\n" for line in (run.stdout.splitlines() + run.stderr.splitlines())[-40:]))


def git_out(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout


def tick_commit(ledger):
    number = Path(ledger).name.removeprefix("issue-").removesuffix("-mutations.md")
    return subprocess.run(["git", "log", "-1", "--format=%H", "--", ledger_path(".", number)],
                          capture_output=True, text=True).stdout.strip()


def replay_before(pin, ledger, root=Path(".")):
    green = tick_commit(ledger) or pin.get("green")
    names = git_out("diff", "--name-only", pin["before"], *([green] if green else [])).split()
    names = [n for n in names if n != pin["keep"] and not n.startswith(".tdd/")]
    if not names and green:
        sys.stderr.write(f"empty replay range: before {pin['before']} green {green}\n")
        return None
    here = os.getcwd()
    os.chdir(root)
    try:
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
    finally:
        os.chdir(here)
    return ran.returncode


@contextlib.contextmanager
def base_worktree():
    base = git_out("merge-base", "origin/main", "HEAD").strip()
    scratch = tempfile.mkdtemp()
    tree = Path(scratch) / "base"
    try:
        added = subprocess.run(["git", "worktree", "add", "--detach", str(tree), base], capture_output=True, text=True)
        if added.returncode != 0:
            sys.stderr.write(f"cannot create the base worktree at {base}: {added.stderr.strip()}\n")
            yield None
        else:
            yield tree
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", str(tree)], capture_output=True)
        shutil.rmtree(scratch, ignore_errors=True)


def replay_on_base(pin, ledger):
    with base_worktree() as tree:
        return None if tree is None else replay_before(pin, ledger, tree)


def mutation_green_on_base(pin):
    with base_worktree() as tree:
        if tree is None:
            return None
        target = tree / pin["file"]
        if not target.exists() or pin["old"].encode() not in target.read_bytes():
            return False
        target.write_bytes(target.read_bytes().replace(pin["old"].encode(), pin["new"].encode()))
        return subprocess.run(pin["command"], shell=True, cwd=tree, capture_output=True).returncode == 0


def mutated_file_of(record):
    return record.get("file", record.get("keep"))


def recheck(argv, looks):
    if not argv:
        sys.stderr.write("usage: pin-recheck.sh <base-sha>\n")
        return 2
    touched = set(git_out("diff", "--name-only", f"{argv[0]}..HEAD").split())
    found = [(f, r) for f in sorted(glob.glob(".tdd/issue-*-mutations.md")) for r in records(Path(f).read_text())]
    for f, r in found:
        if "before" not in r and "file" not in r:
            sys.stderr.write(f"unparseable mutation record in {f}: {r}\n")
            return 2
    pins = [(f, r) for f, r in found if r.get("keep", r.get("file")) in touched]
    if not pins:
        return 3
    deleted = set(git_out("diff", "--name-only", "--diff-filter=D", f"{argv[0]}..HEAD").split())
    declared = {}
    for line in git_out("diff", "-U0", f"{argv[0]}..HEAD", "--", ".tdd").splitlines():
        m = re.match(r"\+\s*retire-pin: (\S+) (\S+) --(.*)$", line)
        if m:
            if not m[3].strip():
                sys.stderr.write(f"retire-pin for {m[1]} {m[2]} has an empty reason\n")
                return 2
            declared[(m[1], m[2])] = m[3].strip()
    held = {(f, mutated_file_of(r)) for f, r in found}
    for key in declared:
        if key not in held:
            sys.stderr.write(f"retire-pin names no pin: {key[0]} {key[1]}\n")
            return 2
    status = 0
    retired = 0
    for ledger, pin in pins:
        mutated_file = mutated_file_of(pin)
        if "retired" in pin:
            retired += 1
            continue
        reason = declared.get((ledger, mutated_file))
        if reason:
            sys.stdout.write(f"retired: {ledger} {mutated_file} {reason}\n")
            retired += 1
            event.append("", {}, "pin-retired", [f"reason={reason}"])
            pin["retired"] = reason
            Path(ledger).write_text("".join(
                "".join(f"{k} {len(v)}\n{v}\n" for k, v in r.items()) + "\n" for f, r in found if f == ledger))
            continue
        named = [n.strip("\"'") for n in re.findall(r"TESTS=(\S+)", pin["command"])]
        gone = [n for n in named if n.split("::")[0] in deleted]
        named = [n for n in named if n.split("::")[0] not in deleted]
        if gone and not named:
            for n in gone:
                sys.stdout.write(f"retired: {ledger} {mutated_file} {n}\n")
            retired += 1
            continue
        for n in gone:
            pin["command"] = re.sub(r"TESTS=[\"']?" + re.escape(n) + r"[\"']*(?=\s|$)", "", pin["command"])
        missing = [n for n in named if not Path(n.split("::")[0]).exists()]
        if missing:
            for n in missing:
                if subprocess.run(["git", "cat-file", "-e", f"origin/main:{n.split('::')[0]}"],
                                  capture_output=True).returncode == 0:
                    sys.stderr.write(f"named test missing at HEAD: {n} (pin file {ledger})\n")
                    return 2
            sys.stdout.write(f"stale: {ledger} {mutated_file}\n")
            continue
        if "before" in pin:
            replayed = replay_before(pin, ledger)
            if replayed is None:
                return 2
            if replayed == 0:
                on_base = replay_on_base(pin, ledger)
                if on_base is None:
                    return 2
                if on_base == 0:
                    sys.stdout.write(f"stale: {ledger} {(named[0].split('::')[0] if named else pin['keep'])}\n")
                else:
                    sys.stderr.write(f"pin stayed green on the before-state: {pin['keep']}\n")
                    status = 1
            continue
        pin["command"] = current_wrapper(pin["command"])
        path = Path(pin["file"])
        original = path.read_bytes()
        if pin["old"].encode() not in original:
            needs_a_look(looks, pin["file"], "old text gone")
            continue
        if original.count(pin["old"].encode()) > 1:
            needs_a_look(looks, pin["file"], "old text occurs more than once")
            continue
        base = run_captured(pin["command"])
        if base.returncode == 127 or "no makefile found" in base.stderr.lower():
            sys.stderr.write(f"command not found: {pin['command']} (pin file {ledger})\n")
            return 2
        if base.returncode == 2 and ("invalid option" in base.stderr or "Usage: make" in base.stderr):
            sys.stderr.write(f"command rejected by make: {pin['command']} (pin file {ledger})\n")
            return 2
        if base.returncode != 0:
            needs_a_look(looks, pin["file"], "base run failed")
            write_tail(base)
            continue
        path.write_bytes(original.replace(pin["old"].encode(), pin["new"].encode()))
        mutated = run_captured(pin["command"])
        path.write_bytes(original)
        green = mutated.returncode == 0
        base_lines = output_lines(base)
        if not green and not base_lines & output_lines(mutated) and not is_go_test_failure(mutated) and not is_pytest_failure(mutated):
            needs_a_look(looks, pin["file"], "mutation did not build")
            write_tail(mutated)
            status = 1
            continue
        if green:
            control = control_run(path, original, pin["command"])
            if control.returncode == 0:
                needs_a_look(looks, pin["file"], "mutation and control green")
                continue
            on_base = mutation_green_on_base(pin)
            if on_base is None:
                return 2
            if on_base:
                sys.stdout.write(f"stale: {ledger} {pin['file']}\n")
                continue
            sys.stderr.write(f"pin stayed green under its mutation: {pin['file']}\n")
            status = 1
    if retired == len(pins):
        return 3
    return status


RECEIPT = Path(".tdd/pin-recheck-ok")


def main(argv):
    RECEIPT.unlink(missing_ok=True)
    looks = {}
    status = recheck(argv, looks)
    flush_looks(looks)
    if status in (0, 3):
        head = git_out("rev-parse", "HEAD").strip()
        RECEIPT.write_text(head + "\n")
    return status


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
