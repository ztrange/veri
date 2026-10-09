"""leaf-role.sh's mapping, run in-process."""
import os
import re
import sys

USAGE = "usage: leaf-role.sh <leaf-name>"
ACTORS = {"develop": "developer", "revise": "developer", "verify": "verifier", "conductor": "conductor"}
SHAPES = "(want develop-*|revise-*|verify-*|conductor-*)"


def _write(stream, line):
    stream.flush()
    stream.buffer.write(os.fsencode(line + "\n"))
    stream.buffer.flush()


def _refuse(name, reason):
    _write(sys.stderr, "leaf-role: leaf name '%s' %s %s" % (name, reason, SHAPES))


def leaf_role(name):
    """VERI_ACTOR, VERI_PHASE and VERI_ATTEMPT for a leaf name."""
    if not name:
        _write(sys.stderr, "leaf-role: " + USAGE)
        return None
    actor_word = name.split("-", 1)[0]
    if actor_word not in ACTORS:
        _refuse(name, "has an unknown leading word")
        return None
    phase, attempt = name[len(actor_word) + 1:], "1"
    if not phase:
        _refuse(name, "says no phase")
        return None
    split = re.fullmatch(r"(.*)-([0-9]+)", phase, re.DOTALL)
    if split:
        phase, attempt = split.groups()
    return {"VERI_ACTOR": ACTORS[actor_word], "VERI_PHASE": phase, "VERI_ATTEMPT": attempt}


def main(argv):
    if not argv or not argv[0]:
        _write(sys.stderr, USAGE)
        return 2
    role = leaf_role(argv[0])
    if role is None:
        return 2
    _write(sys.stdout, "VERI_ACTOR=%(VERI_ACTOR)s VERI_PHASE=%(VERI_PHASE)s VERI_ATTEMPT=%(VERI_ATTEMPT)s" % role)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
