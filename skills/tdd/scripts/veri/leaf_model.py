"""leaf-model.sh's resolution, run in-process."""
import os
import sys

from leaf_role import leaf_role

USAGE = "usage: leaf-model.sh <leaf-name>"
WHITESPACE = " \t\n\v\f\r"


def _write(stream, line):
    stream.flush()
    stream.buffer.write(os.fsencode(line + "\n"))
    stream.buffer.flush()


def main(argv):
    if not argv or not argv[0]:
        _write(sys.stderr, USAGE)
        return 2
    actor = leaf_role(argv[0])["VERI_ACTOR"]
    model = os.environ.get("VERI_MODEL_" + actor.upper()) or os.environ.get("VERI_MODEL", "")
    if any(c in WHITESPACE for c in model):
        _write(sys.stderr, f"leaf-model: model '{model}' contains whitespace (a model id or alias is one word)")
        return 2
    if model:
        _write(sys.stdout, model)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
