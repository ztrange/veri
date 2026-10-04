"""leaf-role.sh's mapping, run in-process."""
import sys

USAGE = "usage: leaf-role.sh <leaf-name>"
ACTORS = {"develop": "developer"}


def leaf_role(name):
    """VERI_ACTOR, VERI_PHASE and VERI_ATTEMPT for a leaf name."""
    actor_word = name.split("-", 1)[0]
    return {"VERI_ACTOR": ACTORS[actor_word], "VERI_PHASE": name[len(actor_word) + 1:], "VERI_ATTEMPT": "1"}


def main(argv):
    if not argv or not argv[0]:
        print(USAGE, file=sys.stderr)
        return 2
    role = leaf_role(argv[0])
    print("VERI_ACTOR=%(VERI_ACTOR)s VERI_PHASE=%(VERI_PHASE)s VERI_ATTEMPT=%(VERI_ATTEMPT)s" % role)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
