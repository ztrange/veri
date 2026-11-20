"""role-state.sh's logic, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import glob
import os
import re
import sys
import time

import entry
import event_log
import run_dir
import timed_n_format
import tunables

USAGE = ("usage: role-state.sh dev [--lane <lane>] set <n|lane|auto|session|transcript|baseline|baseline-at|refused-at|refused-now-at|resetter> <value>"
         " | add <decision|message|override|timed-n> <text>"
         " | drop <decision|message|override|timed-n> <id> | show | recovered | request-reset\n")


def state_path(tree, role, lane=None):
    name = role if lane is None else "%s-%s" % (role, lane)
    return run_dir.main_file(tree, "role-%s.state" % name)


STAMP = "%Y-%m-%dT%H:%M:%S"


def marker_path(path):
    name = os.path.basename(path)[len("role-"):-len(".state")]
    return os.path.join(os.path.dirname(path), "reset-request-" + name)


def now():
    return time.strftime(STAMP)


def epoch(stamp):
    return time.mktime(time.strptime(stamp, STAMP))


def replace(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        f.write(text)
    os.replace(tmp, path)


def read(path):
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        return None


def read_lines(role, lane=None):
    """The role's state lines (`.tdd/role-<role>[-<lane>].state` of the main tree), `None` when the file is missing."""
    text = read(state_path(run_dir.main_tree(missing=""), role, lane))
    return None if text is None else text.splitlines()


class Malformed(ValueError):
    """The one way a state line is refused. `kind` is "n-missing" (no `n=` line, `line` None), "n", "timed-n", "override" or "state"; `line` is the offending line. Each caller words it."""

    def __init__(self, kind, line=None):
        super().__init__("%s: %s" % (kind, line))
        self.kind = kind
        self.line = line


class State:
    """The grammar of a role's state file, over its lines: `key=value` lines and `<kind> <id> <stamp> <text>` item lines."""

    def __init__(self, lines):
        self.lines = list(lines)

    def fields(self):
        """Every `key=value` line as a dict, the last of a key winning."""
        return dict(line.partition("=")[::2] for line in self.lines)

    def field(self, name):
        """The value of the last `<name>=<value>` line, `None` when there is none."""
        return self.fields().get(name)

    def values(self, name):
        """The value of every `<name>=<value>` line, in file order."""
        return [value for key, sep, value in (line.partition("=") for line in self.lines) if sep and key == name]

    def items(self, *kinds):
        """The raw lines of the given item kinds, in file order."""
        return [line for line in self.lines if line.startswith(tuple(kind + " " for kind in kinds))]

    def check(self):
        """Raises Malformed("state") on a line that is neither `key=value` nor an item line."""
        for line in self.lines:
            if "=" not in line and not line.startswith(tuple(kind + " " for kind in ITEM_KINDS)):
                raise Malformed("state", line)

    def last_n(self):
        """The target from the last `n=` line, as an int."""
        ns = [line for line in self.lines if line.startswith("n=")]
        if not ns:
            raise Malformed("n-missing")
        try:
            return int(ns[-1][2:])
        except ValueError:
            raise Malformed("n", ns[-1])

    def timed_ns(self):
        """`(value, expiry epoch)` of each timed-n line, in file order."""
        found = []
        for line in self.items("timed-n"):
            try:
                found.append(timed_n_format.parse(line.split(None, 3)[3]))
            except (IndexError, ValueError):
                raise Malformed("timed-n", line)
        return found

    def override_numbers(self):
        """The first number each override line names (a string), `None` when it names none, in file order."""
        found = []
        for line in self.lines:
            if not line.startswith("override "):
                continue
            fields = line.split(None, 3)
            if len(fields) < 4:
                raise Malformed("override", line)
            named = re.search(r"\d+", fields[3])
            found.append(named.group() if named else None)
        return found


class BadStateFile(Exception):
    """A state file `State.check` refuses; its text, `malformed state file <path>`, is the whole message."""

    def __init__(self, path):
        super().__init__("malformed state file %s\n" % path)


def checked(path):
    """The State of the file at `path` (no lines when it is missing), once `check` passes; raises BadStateFile naming `path` otherwise."""
    state = State((read(path) or "").splitlines())
    try:
        state.check()
    except Malformed:
        raise BadStateFile(path)
    return state


def append(path, text):
    replace(path, (read(path) or "") + text)


def usage():
    sys.stderr.write(USAGE)
    return 2


def main(argv):
    return run_verbs(argv)


def run_verbs(argv, after_set_n=None):
    """The role-state.sh verbs; after a written `set n`, the line after_set_n(path, n) returns is printed
    (role_state_cli passes the lane budget's, PRD 036.5)."""
    if len(argv) < 2:
        return usage()
    name = argv[0]
    if name != "dev":
        return usage()
    lane = None
    if argv[1] == "--lane":
        if len(argv) < 4:
            return usage()
        lane = argv[2]
        argv = [argv[0]] + argv[3:]
    path = state_path(run_dir.main_tree_from_files(os.getcwd()), name, lane)
    verb = VERBS.get(argv[1])
    code = verb(path, argv) if verb else usage()
    if code == 0 and after_set_n and argv[1:3] == ["set", "n"]:
        sys.stdout.write(after_set_n(path, int(argv[3])))
    return code


def do_recovered(path, argv):
    session = os.environ.get("CLAUDE_CODE_SESSION_ID")
    if not session:
        return usage()
    kept = [l for l in (read(path) or "").splitlines(True) if not l.startswith(("refused-at=", "refused-now-at="))]
    replace(path, "".join(kept) + "recovered-at=%s\nsession-id=%s\n" % (now(), session))
    try:
        os.remove(marker_path(path))
    except FileNotFoundError:
        pass
    return 0


def launched_since(path, recovered):
    since = epoch(recovered)
    main = os.path.dirname(os.path.dirname(path))
    runs = [main] + sorted(d for d in glob.glob(os.path.join(run_dir.worktrees(main), "*")) if os.path.isdir(d))
    events = [e for run in runs for e in event_log.events(run, "conductor-start", "merged", skip_unreadable=True)]
    return any(e.get("ts", 0) > since for e in events)


def refusal(path, lines, stamp):
    state = State(lines)
    recovered = state.values("recovered-at")
    if recovered:
        decided = any(l.split()[2] > recovered[-1] for l in lines if l.startswith(("decision ", "dropped-decision ")))
        if not decided and not launched_since(path, recovered[-1]):
            return "request-reset refused: nothing launched, merged or decided since the last recovery"
    hour_ago = epoch(stamp) - 3600
    recent = [at for at in state.values("reset-at") if epoch(at) > hour_ago]
    if len(recent) >= int(tunables.get("VERI_RESET_MAX_PER_HOUR")):
        return "request-reset refused: %d resets in the last hour" % len(recent)
    return None


def do_request_reset(path, argv):
    if argv[2:]:
        return usage()
    lines = (read(path) or "").splitlines()
    stamp = now()
    reason = refusal(path, lines, stamp)
    if reason:
        sys.stderr.write(reason + "\n")
        return 1
    append(path, "reset-at=%s\n" % stamp)
    replace(marker_path(path), stamp + "\n")
    return 0


def do_set(path, argv):
    if len(argv) != 4 or argv[2] not in SET_FIELDS:
        return usage()
    if argv[2] == "n" and entry.whole_number(argv[3], minimum=0) is None:
        return usage()
    if argv[2] == "auto" and argv[3] not in ("on", "off"):
        return usage()
    append(path, "%s=%s\n" % (argv[2], argv[3]))
    return 0


def do_add(path, argv):
    if argv[2] not in LISTS or len(argv) != 4:
        return usage()
    if argv[2] == "timed-n":
        try:
            timed_n_format.parse(argv[3])
        except ValueError:
            sys.stderr.write("timed-n text must be: <n> until <ISO-8601 datetime>\n")
            return 2
    item = str(max([int(l.split()[1]) for l in (read(path) or "").splitlines() if l.partition(" ")[0] in LISTS] + [0]) + 1)
    append(path, "%s %s %s %s\n" % (argv[2], item, now(), argv[3]))
    print(item)
    return 0


def drop_lines(path, doomed):
    lines = (read(path) or "").splitlines(True)
    kept = [l for l in lines if not doomed(l)]
    if kept == lines:
        return 3
    replace(path, "".join(kept))
    return 0


def do_drop(path, argv):
    if argv[2] not in LISTS:
        return usage()
    code = drop_lines(path, lambda l: l.split()[:2] == argv[2:4])
    if code == 0 and argv[2] == "decision":
        append(path, "dropped-decision %s %s\n" % (argv[3], now()))
    return code


def do_show(path, argv):
    text = read(path)
    if text is None:
        return 3
    sys.stdout.write(text)
    return 0


SET_FIELDS = ("n", "lane", "auto", "session", "transcript", "baseline", "baseline-at", "refused-at", "refused-now-at", "resetter")
LISTS = ("decision", "message", "override", "timed-n")
ITEM_KINDS = LISTS + ("dropped-decision",)
VERBS = {"recovered": do_recovered, "request-reset": do_request_reset, "set": do_set, "add": do_add, "drop": do_drop, "show": do_show}


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
